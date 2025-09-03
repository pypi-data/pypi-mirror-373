import dataclasses
import logging
from dataclasses import (
    dataclass,
    Field,
)
from datetime import (
    date,
    datetime,
    timedelta,
)
from typing import (
    Any,
    Hashable,
)
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.orm import (
    aliased,
    Query,
)
from unidecode import unidecode

from caerp.models.activity import Attendance
from caerp.models.career_path import CareerPath
from caerp.models.career_stage import CareerStage
from caerp.models.user import (
    User,
    Login,
)
from caerp.models.user.userdatas import (
    UserDatas,
)
from caerp.dataqueries.base import BaseDataQuery
from caerp.models.user.utils import (
    iter_situations_durations,
    get_userdatas_seniority,
    get_ongoing_parcours,
    collect_activity_typologies,
)
from caerp.models.workshop import (
    Timeslot,
    Workshop,
)
from caerp.services.user.login import (
    get_last_connection,
)

from caerp.utils.dataqueries import dataquery_class
from caerp.utils.strings import strip_nonletters

logger = logging.getLogger(__name__)


def _normalize(s: str) -> str:
    """
    >>> _normalize("é a-'")
    "e a'"
    """
    s = s.lower()
    s = unidecode(s)
    s = s.replace("-", "")

    return s


def _normalize_identity(first_name: str, last_name: str) -> str:
    """
    >>> _normalize_identity('Jean-Michel','BALO RETO')
    'jeanmichel boloreto'
    """
    return f"{strip_nonletters(_normalize(first_name))} {strip_nonletters(_normalize(last_name))}"


def _get_info_col_workshops(user: User) -> Query:
    """For a given user returns a query with all its infocol workshops

    Infocol are detected a fuzzy way : workshops containint collective in title.

    :return: a query of Workshops
    """
    workshop_of_attendance = aliased(Workshop, flat=True)
    return (
        Attendance.query()
        .join(Timeslot, Timeslot.id == Attendance.event_id)
        .join(workshop_of_attendance, Timeslot.workshop)
        .filter(
            Attendance.user == user,
            Attendance.status == "attended",
            func.lower(func.ifnull(workshop_of_attendance.name, "")).contains(
                "collective"
            ),
        )
        .order_by(Timeslot.start_time.desc())
    ).with_entities(workshop_of_attendance)


class DuplicateFinder:
    def __init__(self):
        self._store = {}

    def process(self, key: Hashable, content: Any) -> list[Any]:
        if key:
            previous_content = self._store.get(key, [])
            if previous_content:
                self._store[key].append(content)
            else:
                self._store[key] = [content]

            return previous_content
        else:
            # key is None/empty, do not store the record
            return []


def _labeled(label) -> Field:
    return dataclasses.field(metadata=dict(label=label))


def check_activity_type_consistency(ud: UserDatas) -> bool:
    if not ud:
        return True  # no check
    if ud.user.login.account_type == "equipe_appui":
        return True  # no check
    else:
        typologies = collect_activity_typologies(ud)
        relevant_typologies = [
            i for i in typologies if i["source"] != "userdatas_activities"
        ]
        if len(relevant_typologies) > 1:
            # Compare profile typology with first activity of first company
            return (
                relevant_typologies[0]["typology"] == relevant_typologies[1]["typology"]
            )
        else:
            return False


@dataquery_class()
class OBQualityCheckActiveAccounts(BaseDataQuery):
    name = "ob_qualite_comptes_actifs"
    label = "[OUVRE-BOITES] Qualité des données pour les comptes actuels enDI"
    description = """
    <p>
        Vérifie la qualité des données des utilisateurs actuels d'enDI <strong>actuellement autorisés à se connecter</strong> (donc uniquement ceux qui n'ont pas été désactivés).
    </p>
    <p>
        Requête taillée pour les besoins et la config de l'<a href="https://ouvre-boites.coop">Ouvre-Boites</a>.
    </p>
    <ul>
        <li>Les premières colones servent à pouvoir retrouver le compte sur MoOGLi</li>
        <li>Les suivantes sont des vérifications, si une valeur est à VRAI, il y a peut-être une anomalie sur les données concernant cette fiche</li>
    </ul>
    
    """

    @dataclass
    class Row:
        caerp_id: int = _labeled("Identifiant MoOGLi")
        first_name: str = _labeled("Prénom")
        last_name: str = _labeled("Nom")
        account_type: str = _labeled("Type de compte")
        companies: str = _labeled("Enseignes")
        accomp: str = _labeled("Chargé d'accomp")
        #
        warn_duplicate: bool = _labeled("Compte en Doublon ?")
        warn_no_connection: bool = _labeled("Pas connecté depuis > 6 mois")
        warn_exited_still_active: bool = _labeled(
            "Sorti il y a plus de six mois mais peut toujours se connecter"
        )
        warn_no_userdatas: bool = _labeled("Fiche de gestion sociale absente")
        #
        warn_inconsistent_date_infocol: bool = _labeled(
            "Date infocol et émargement incohérents"
        )
        warn_no_entry: bool = _labeled("Parcours sans étape d'entrée")
        warn_missing_type_sortie: bool = _labeled("Type de sortie non renseigné")
        warn_long_cape: bool = _labeled("CAPE anormalement long")
        warn_missing_societariat_entrance: bool = _labeled(
            "Date d'entrée au sociétariat manquante"
        )
        warn_inconsistent_societariat_entrance: bool = _labeled(
            "Date d'entrée au sociétariat incohérente avec l'étape de parcours"
        )
        warn_no_entry_date_yet: bool = _labeled(
            "Entrée il y a plus de 4 ans mais pas sociétaire"
        )
        #
        warn_es_wo_company: bool = _labeled("Entrepreneur sans enseigne active")
        warn_es_wo_analytic: bool = _labeled("Entrepreneur sans compte analytique")

        warn_no_birthname: bool = _labeled("Nom de naissance non renseigné")
        warn_no_zone: bool = _labeled("Zone d'habitation non renseignée")
        warn_no_antena: bool = _labeled("Antenne de rattachement non renseignée")
        warn_no_accomp: bool = _labeled("Chargé·e d'accomp non renseigné")
        warn_accomp_left: bool = _labeled("Chargé·e d'accomp parti de la CAE")
        warn_inconsistent_typology: bool = _labeled(
            "Incohérence dee type d'activité (enseigne/entrepreneur·euse)"
        )

        def values(self):
            return [getattr(self, i.name) for i in dataclasses.fields(self)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_index_by_email = DuplicateFinder()
        self._user_index_by_name = DuplicateFinder()

    def _duplicate_check(self, user: User) -> set[int]:
        key_email = user.email.lower()
        key_name = _normalize_identity(user.firstname, user.lastname)
        dups_ids = set(
            self._user_index_by_email.process(key_email, user.id)
            + self._user_index_by_name.process(key_name, user.id)
        )
        return dups_ids

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        return [i.metadata["label"] for i in dataclasses.fields(self.Row)]

    def data(self):
        query = (
            User.query()
            .join(Login)
            .outerjoin(UserDatas, User.id == UserDatas.user_id)
            .filter(Login.active == True)
        )
        return [self.data_row(user) for user in query]

    def data_row(self, user: User) -> list:
        missing_userdatas = user.userdatas is None
        last_connection = get_last_connection(self.request, user.id)
        duplicates = self._duplicate_check(user)
        six_months_ago = date.today() - relativedelta(months=6)

        if missing_userdatas:
            parcours = None
            user_exited_six_months_ago = False
            entry_date = None
            missing_type_sortie = False
        else:
            parcours = get_ongoing_parcours(
                user.userdatas.id,
                self.end_date,
            )
            if parcours:
                user_exited_six_months_ago = (parcours.exit_date is not None) and (
                    parcours.exit_date < six_months_ago
                )

                entry_date = parcours.entry_date
                if parcours.exit:
                    missing_type_sortie = parcours.exit.type_sortie_id is None
                else:
                    missing_type_sortie = False
            else:
                user_exited_six_months_ago = False
                entry_date = None
                missing_type_sortie = False

        if missing_userdatas:
            societariat_step = None
            steps_count = 0
            seniority = 0
        else:
            steps_query = CareerPath.query().filter(
                CareerPath.userdatas_id == user.userdatas.id
            )
            steps_count = steps_query.count()
            societariat_step = (
                (
                    steps_query.join(CareerPath.career_stage).filter(
                        CareerStage.name.contains("Associé")
                    )
                )
                .order_by(CareerPath.start_date.desc())
                .first()
            )  # latest
            seniority = (
                get_userdatas_seniority(user.id, at_date=date.today())
                if user.userdatas
                else 0
            )

        societariat_step_date = (
            societariat_step.start_date if societariat_step else None
        )
        ud: UserDatas = user.userdatas
        active_companies = user.active_companies
        active_analytics = [c.code_compta for c in active_companies if c.code_compta]
        missing_accomp = missing_userdatas or not ud.situation_follower_id

        if missing_userdatas:
            too_long_capes = []
        else:
            too_long_capes = [
                (situation, duration)
                for situation, duration in iter_situations_durations(ud, self.end_date)
                if ("CAPE" in situation.label.upper())
                and (duration.days > (366 * 3))  # 3 years
            ]

        _attended_infocols = _get_info_col_workshops(user).all()
        if _attended_infocols:
            latest_attended_infocol_date = (
                _attended_infocols[0].timeslots[0].start_time.date()
            )
        else:
            latest_attended_infocol_date = None

        return self.Row(
            caerp_id=user.id,
            first_name=user.firstname,
            last_name=user.lastname,
            account_type=user.login.account_type,
            companies=", ".join(i.name for i in user.active_companies),
            accomp=None if missing_accomp else ud.situation_follower.label,
            warn_no_connection=(datetime.now() - last_connection)
            > timedelta(weeks=6 * 4)
            if last_connection
            else True,
            warn_duplicate=len(duplicates) > 0,
            warn_exited_still_active=user_exited_six_months_ago and user.login.active,
            warn_no_userdatas=missing_userdatas,
            warn_es_wo_company=len(active_companies) < 1,
            warn_es_wo_analytic=False
            if not active_companies
            else len(active_analytics) < 1,
            warn_no_birthname=False
            if missing_userdatas
            else not ud.coordonnees_ladies_lastname,
            warn_no_zone=False if missing_userdatas else not ud.coordonnees_zone_id,
            warn_no_antena=False if missing_userdatas else not ud.situation_antenne_id,
            warn_no_accomp=False if missing_userdatas else missing_accomp,
            warn_accomp_left=False
            if missing_accomp
            else not ud.situation_follower.login.active,
            warn_no_entry=False
            if (missing_userdatas or (steps_count < 1))
            else (entry_date is None),
            warn_missing_societariat_entrance=(
                False
                if missing_userdatas
                else bool(
                    societariat_step_date
                    and not user.userdatas.situation_societariat_entrance
                )
            ),
            warn_inconsistent_societariat_entrance=(
                False
                if (
                    missing_userdatas
                    or not societariat_step_date
                    or not user.userdatas.situation_societariat_entrance
                )
                else societariat_step_date
                != user.userdatas.situation_societariat_entrance
            ),
            warn_long_cape=len(too_long_capes) > 0,
            warn_no_entry_date_yet=bool(
                seniority > (12 * 4)
                and not user.userdatas.situation_societariat_entrance
            ),
            warn_inconsistent_typology=not check_activity_type_consistency(
                user.userdatas
            ),
            warn_missing_type_sortie=missing_type_sortie,
            warn_inconsistent_date_infocol=(
                False
                if missing_userdatas
                else (
                    latest_attended_infocol_date
                    != user.userdatas.parcours_date_info_coll
                )
            ),
        ).values()
