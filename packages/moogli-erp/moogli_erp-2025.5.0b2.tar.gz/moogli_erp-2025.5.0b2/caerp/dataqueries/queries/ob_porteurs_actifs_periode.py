import logging
from datetime import (
    date,
    timedelta,
)
from typing import (
    Iterable,
    List,
    Optional,
    Tuple,
)

from sqlalchemy import func
from sqlalchemy.orm import (
    aliased,
    with_polymorphic,
)

from caerp.consts.users import ACCOUNT_TYPES
from caerp.models.activity import (
    Activity,
    ActivityType,
    Attendance,
    Event,
)
from caerp.models.career_path import (
    MotifSortieOption,
    CareerPath,
)
from caerp.models.user import (
    User,
    Login,
)
from caerp.models.user.userdatas import (
    SocialDocTypeOption,
    UserDatas,
    UserDatasSocialDocTypes,
)
from caerp.models.user.utils import (
    get_all_userdatas_active_on_period,
    get_epci_label,
    get_user_analytical_accounts,
    get_social_statuses_label,
    get_userdatas_cae_situation,
    get_num_hours_worked,
    get_ongoing_parcours,
)
from caerp.dataqueries.base import BaseDataQuery
from caerp.models.workshop import (
    Timeslot,
    Workshop,
)
from caerp.services.user.login import has_access_right
from caerp.utils.dataqueries import dataquery_class

logger = logging.getLogger(__name__)


def _is_equipe(login: Login):
    return login.account_type in (
        ACCOUNT_TYPES["equipe_appui"],
        ACCOUNT_TYPES["hybride"],
    )


def _is_entrepreneur(login: Login):
    return login.account_type in (
        ACCOUNT_TYPES["entrepreneur"],
        ACCOUNT_TYPES["hybride"],
    )


def social_status_to_flags(social_status_label) -> Tuple[str, str, str, str]:
    # Les booléens successifs correspondent à, dans l'ordre:
    # Chômeurs moins de 2 ans (OUI / NON)
    # Chômeurs de longue durée (OUI / NON)
    # Personnes inactives (OUI / NON)
    # Personne exerçant un emploi, y compris les indépendants (OUI / NON)

    _map = {
        "Salarié.e - Temps plein": (False, False, False, True),
        "Salarié.e - Temps partiel": (False, False, False, True),
        "Demandeur.e d'emploi (plus de 2 ans) - Non indemnisé.e": (
            False,
            True,
            True,
            False,
        ),
        "Demandeur.e d'emploi (plus de 2 ans) - Indemnisé.e": (
            False,
            True,
            True,
            False,
        ),
        "Demandeur.e d'emploi (entre 1 et 2 ans) - Non indemnisé.e": (
            True,
            False,
            True,
            False,
        ),
        "Demandeur.e d'emploi (entre 1 et 2 ans) - Indemnisé.e": (
            True,
            False,
            True,
            False,
        ),
        "Demandeur.e d'emploi (moins de 1 an) - Non indemnisé.e": (
            True,
            False,
            True,
            False,
        ),
        "Demandeur.e d'emploi (moins de 1 an) - Indemnisé.e": (
            True,
            False,
            True,
            False,
        ),
        "Étudiant.e": (False, False, False, False),
        # "RSA": [],
    }
    try:
        return _map[social_status_label]
    except KeyError:
        return ("INCONNU",) * 4


def exit_type_to_flags(
    all_motifs: List[MotifSortieOption], motif: MotifSortieOption
) -> List[bool]:
    flags = []

    for existing_motif in all_motifs:
        if motif == existing_motif:
            flags.append(True)
        else:
            flags.append(False)

    return flags


def doctypes_to_flags(userdatas: UserDatas, docs_to_show: List[str]) -> List[bool]:
    """
    Returns a flag for each of the social doc types we have interest in.

    :param userdatas:
    :param docs_to_show: the list of docs to be shown
    :return: True/False for each doctype listed in docs_to_show, in same order as docs_to_show
    """
    docs = (
        UserDatasSocialDocTypes.query()
        .join(UserDatasSocialDocTypes.doctype)
        .filter(
            UserDatasSocialDocTypes.userdatas == userdatas,
            SocialDocTypeOption.label.in_(docs_to_show),
        )
    )
    db_dict = {doc.doctype.label: doc.status for doc in docs.all()}
    return [db_dict.get(k, False) for k in docs_to_show]


def get_activity_date(
    user: User, after_date: date, activity_type: str
) -> Optional[date]:
    q = Attendance.query()
    q = q.join(Activity, Attendance.user, User.userdatas, ActivityType)
    q = q.filter(
        Attendance.status.in_(("registered", "attended")),
        ActivityType.label == activity_type,
        Activity.datetime >= after_date,  # ,UserDatas.parcours_date_info_coll,
        User.id == user.id,
    )
    activity = q.first()
    if activity is not None:
        return activity.event.datetime.date()
    else:
        return None


def get_sortie_comptable_date(
    userdatas_id: int, sortie_step: CareerPath
) -> Optional[date]:
    """
    Given a CareerPath w stage_type='exit', look for the corresponding CareerPath linked to

    Liberal in what it accepts: the step can be sortie_step iteslf, or another step.

    Notion propre au workflow de l'ouvre-boites : 2 sorties : une sortie contractuelle (la première) et
    une sortie comptable (qui vient après).
    """
    cae_situation_label = "Sortie comptable"
    sortie_comptable_step = None
    if sortie_step.cae_situation.label == cae_situation_label:
        sortie_comptable_step = sortie_step
    else:
        query = (
            CareerPath.query(CareerPath.userdatas_id == userdatas_id)
            .join(CareerPath.cae_situation)
            .filter(
                CareerPath.start_date >= sortie_step.start_date,
                CareerPath.stage_type.in_(["exit", "entry", "contract", "amendment"]),
                CareerPath.id != sortie_step.id,
            )
        )
        steps = query.all()
        # Cannot manage to SQL-sort it, don't know why…
        steps.sort(key=lambda x: x.start_date)
        try:
            # We consider only the first significant step
            # if there are significant steps between the sortie contractuelle and sortie comptable,
            # they might not be related. So we consider only the first significant step.
            next_significant_step = steps[0]
        except IndexError:
            sortie_comptable_step = None
        else:
            if next_significant_step.cae_situatiion.label == cae_situation_label:
                sortie_comptable_step = next_significant_step

    if sortie_comptable_step:
        return sortie_comptable_step.start_date
    else:
        return None


@dataquery_class()
class OBActiveOrSupportedESQuery(BaseDataQuery):
    name = "ob_porteurs_actifs_ou_accompagnes_periode"
    label = (
        "[OUVRE-BOITES] Requête stats financeurs (porteurs actifs et/ou accompagnés)"
    )
    description = """
    <p>
        Liste de tous les porteurs de projets actifs sur la période choisie avec les informations nécessaires pour les financeurs BPI/FSE.
    </p>
    <p>
        Requête taillée pour les besoins et la config de l'<a href="https://ouvre-boites.coop">Ouvre-Boites</a> sur la base des requêtes existantes « porteurs actifs » et « porteurs accompagnés ».
    </p>
    <br/>
    <ul>
        <li>Un porteur est considéré <strong>actif</strong> si il est présent sur au moins une partie de la période (présent signifie <em>entré</em> et pas encore <em>sorti</em> au regard des étapes de parcours).</li>
        <li>Un porteur est considéré <strong>accompagné</strong> s'il a eu un rendez-vous 
    d'accompagnement ou a participé à un atelier (en étant présent) sur la période.</li>
    </ul>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cached just the time of the query generation
        self._cached_exit_types = MotifSortieOption.query().all()
        self._docs_to_show = [
            "Avis situation Pôle Emploi",
            "Déclaration Minimis",
            "Attestation RQTH",
            "Questionnaire FSE",
        ]

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "ID Utilisateur",
            "Code(s) analytique(s)",
            "Civilité",
            "Nom",
            "Prénom",
            "E-mail 1",
            "Tél. mobile",
            "Adresse",
            "Code postal",
            "Ville",
            # Désactivé pour l'instant, lent, aurait plus sa place dans une autre requete de vérif de données
            # "EPCI (auto depuis geo.api.gouv)",
            "Zone d'habitation (infos manquantes complétées depuis geo.api.gouv)",  # EPCI et quartier
            "QPV ?",
            f"Situation dans la CAE (au {self.end_date:%d/%m/%Y})",
            "Sociétaire (OUI/NON)",
            "Formateurice (OUI/NON)",
            "",  # SECTION : Statut social à l'entrée
            # "Statut social à l'entrée",
            "Chômeurs moins de 2 ans (OUI / NON / INCONNU)",
            "Chômeurs de longue durée (OUI / NON / INCONNU)",
            "Personne inactive  (OUI / NON / INCONNU)",
            "Personne exerçant un emploi, y compris les indépendants (OUI / NON / INCONNU)",
            "Antenne de rattachement",
            "Accompagnateur",
            "Prescripteur",
            "Sexe",
            "Date de naissance",
            "Code postal lieu de naissance",
            "Age (en fin de période)",
            "Nationalité",
            "Reconnaissance RQTH (OUI/NON)",
            "Niveau d'études",
            "",  # SECTION : Parcours
            "Date info coll",
            "Date 1er RDV",
            "Date signature CAPE",
            "Date CESA",
            "Date d'entrée au sociétariat",
            f"Nombre d'heure contractuel au {self.start_date:%d/%m/%Y}",
            "Nombre d'heures calculées + projetée sur période",
            "Sortie (OUI/NON) (à date de fin de période)",
            "Date de sortie contractuelle",
            "Type de sortie",  # Ajout Jocelyn, il me semble que ça pouvait être utile
            "Date de sortie comptable",
            # "Exerce une activité d'indépendant (OUI / NON)",
            # "Exerce un emploi durable (CDI ou CDD) (OUI / N   ON)",
            # "Exerce un emploi temporaire (OUI / NON)",
            # "Exerce un emploi aidé (OUI / NON)", ## TODO: voir pour éventuellement la rajouter, demande un paramétrage enDI
            # "Est en formation (OUI / NON)",
            # "Recherche activement un emploi (OUI / NON)",
            # Cette ligne correspond aux options du dessus
            *[f"{motif.label} (OUI/NON)" for motif in self._cached_exit_types],
            "",  # SECTION : Justificatifs FSE
            # Masqués pour l'instant car pas exploité, mais on garde le code pour exploitation future
            # *[f"{i} (OUI/NON)" for i in self._docs_to_show],
            # "Statut social à l'entrée",
            # "Statut social actuel",
            "Date de fin de droit",
            "Typologie d'activité principale",
            "Équipe d'appui",
            "Raison de retenue dans les données",
        ]

        return headers

    def data(self):
        data = []
        active_users: Iterable[UserDatas] = get_all_userdatas_active_on_period(
            self.start_date, self.end_date
        )
        user_ids_in_request = set()

        for u in active_users:
            data_row = self.data_row_from_userdatas(u)
            data.append(data_row + ["Porteur actif"])
            user_ids_in_request.add(u.user.id)

        all_events = with_polymorphic(Event, "*")
        timeslot_workshop = aliased(Workshop)

        # Timeslot.datetime may be wrong, the reliable time is Timeslot.start_time
        date_of_event = func.IF(
            all_events.type_ == "timeslot",
            Timeslot.start_time,
            all_events.datetime,
        )

        supported_users = (
            User.query()
            .join(Attendance)
            .join(all_events)
            .outerjoin(timeslot_workshop, Timeslot.workshop)
            .outerjoin(UserDatas, User.id == UserDatas.user_id)
            .where(date_of_event.between(self.start_date, self.end_date))
            .where(Attendance.status == "attended")
            # On exclut tous les workshop qui ne sont pas des infocol
            .where(
                (Event.type_ != "workshop")
                | (
                    func.lower(func.ifnull(all_events.name, "")).contains("collective")
                    | func.lower(func.ifnull(timeslot_workshop.name, "")).contains(
                        "collective"
                    )
                )
            )
            .distinct()
            .order_by(User.lastname, User.firstname)
        )

        for user in supported_users:
            if (not _is_entrepreneur(user.login) and user.userdatas is None) or (
                user.id in user_ids_in_request
            ):
                continue
            else:
                if user.userdatas:
                    data_row = self.data_row_from_userdatas(user.userdatas)
                else:
                    # Should not happen in OB context (and if so, this is likely garbage data)
                    logger.warning("Ignoring user #{user.id} without userdatas")
                data.append(data_row + ["Porteur accompagné"])
                user_ids_in_request.add(user.id)

        return data

    def data_row_from_userdatas(self, u: UserDatas):
        cae_situation = get_userdatas_cae_situation(u.id, self.end_date)

        if cae_situation:
            cae_situation_label = cae_situation.label
        elif u.parcours_date_info_coll and (u.parcours_date_info_coll <= self.end_date):
            # À l'OB, l'étape de parcours infocol n'est pas forcément remplie, on fallback
            cae_situation_label = "Candidat"
        else:
            cae_situation_label = ""
        social_status_flags = social_status_to_flags(
            get_social_statuses_label(u.social_statuses)
        )
        current_parcours = get_ongoing_parcours(u.id, at_date=self.end_date)
        if current_parcours is None:
            latest_exit_ = None
            dernier_cesa_ou_avenant = None
            first_cape_step = None
            first_cesa_step = None
            sortie_comptable_date = None
        else:
            latest_exit_ = current_parcours.exit
            # Contrat CESA ou avenant, dernier en date
            # À l'OB les stage_types contract/amendment qualifient une signature de CESA/avenant
            dernier_cesa_ou_avenant = current_parcours.last_of_type(
                ["contract", "amendment"]
            )

            # Contrat CAPE
            # en cas de multiples CAPE, on retient le premier du parcours
            # À l'OB le stage_type "entry" qualifie une signature de CAPE
            first_cape_step = current_parcours.first_of_type(["entry"])

            # Contrat CESA
            # en cas de multiples CAPE, on retient le premier du parcours
            first_cesa_step = current_parcours.first_of_type(["contract"])
            if latest_exit_:
                sortie_comptable_date = get_sortie_comptable_date(u.id, latest_exit_)
            else:
                sortie_comptable_date = None

        date_premier_rdv_diag = (
            get_activity_date(
                u.user,
                after_date=u.parcours_date_info_coll,
                activity_type="1er RDV diag",
            )
            if u.parcours_date_info_coll
            else None
        )

        user_data = [
            u.user_id,
            # u.coordonnees_identifiant_interne,
            get_user_analytical_accounts(u.user_id),
            u.coordonnees_civilite,
            u.coordonnees_lastname,
            u.coordonnees_firstname,
            u.coordonnees_email1,
            u.coordonnees_mobile,
            u.coordonnees_address,
            u.coordonnees_zipcode,
            u.coordonnees_city,
            # Désactivé pour l'instant, lent, aurait plus sa place dans une autre requete de vérif de données
            # get_epci_label(u.coordonnees_zipcode, u.coordonnees_city),
            # TODO: ici on voudrait bien requêter la BDD de l'ANCT plutôt
            # que de faire une saisie manuelle…
            # Demande envoyée le 13/3 https://sig.ville.gouv.fr/page/174
            # Requête api.geo.gouv pour les champs non remplis
            u.coordonnees_zone.label
            if u.coordonnees_zone
            else get_epci_label(u.coordonnees_zipcode, u.coordonnees_city),
            u.coordonnees_zone_qual.label  # et celui-ci
            if u.coordonnees_zone_qual
            else "",
            cae_situation_label,
            "OUI" if u.situation_societariat_entrance else "NON",
            "OUI" if has_access_right(None, u.user, "es_trainer") else "NON",
            "",  # SECTION : Statut social à l'entrée
            # get_social_statuses_label(u.social_statuses),
            *("OUI" if i else "NON" for i in social_status_flags),  # x 4
            u.situation_antenne.label if u.situation_antenne else "",
            u.situation_follower.label if u.situation_follower else "",
            u.parcours_prescripteur.label if u.parcours_prescripteur else "",
            u.coordonnees_sex,
            self.date_tools.format_date(u.coordonnees_birthday),
            u.coordonnees_birthplace_zipcode,
            self.date_tools.age(u.coordonnees_birthday, self.end_date),
            u.coordonnees_nationality,
            # ça veut dire que même si on a 1J d'AAH, c'est considéré RQTH:
            "OUI"
            if (
                u.statut_handicap_allocation_expiration
                and u.statut_handicap_allocation_expiration > self.start_date
            )
            else "NON",
            u.coordonnees_study_level.label if u.coordonnees_study_level else "",
            "",  # SECTION : Parcours
            self.date_tools.format_date(u.parcours_date_info_coll),
            self.date_tools.format_date(date_premier_rdv_diag),
            self.date_tools.format_date(first_cape_step.start_date)
            if first_cape_step
            else "",
            self.date_tools.format_date(first_cesa_step.start_date)
            if first_cesa_step
            else "",
            self.date_tools.format_date(u.situation_societariat_entrance),
            dernier_cesa_ou_avenant.num_hours if dernier_cesa_ou_avenant else "",
            get_num_hours_worked(u, self.start_date, self.end_date + timedelta(days=1)),
            "OUI" if latest_exit_ else "NON",
            self.date_tools.format_date(latest_exit_.start_date)
            if latest_exit_
            else "",
            latest_exit_.type_sortie.label
            if latest_exit_ and latest_exit_.type_sortie
            else "",
            self.date_tools.format_date(sortie_comptable_date),
            *(
                (
                    "OUI" if bool_flag else "NON"
                    for bool_flag in exit_type_to_flags(
                        self._cached_exit_types,
                        latest_exit_.motif_sortie,
                    )
                )
                if latest_exit_
                else (("",) * len(self._cached_exit_types))
            ),
            "",
            # Masqués pour l'instant car pas exploité, mais on garde le code pour exploitation future
            # *(
            #     "OUI" if bool_flag else "NON"
            #     for bool_flag in doctypes_to_flags(u, self._docs_to_show)
            # ),
            self.date_tools.format_date(u.statut_end_rights_date),
            u.activity_typologie.label if u.activity_typologie else "",
            ("OUI" if _is_equipe(u.user.login) else "NON") if u.user.login else "NON",
        ]
        return user_data
