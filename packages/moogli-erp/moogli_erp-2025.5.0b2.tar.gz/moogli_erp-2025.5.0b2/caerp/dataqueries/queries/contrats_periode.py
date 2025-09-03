import logging

from caerp_base.models.base import DBSESSION
from sqlalchemy import or_

from caerp.dataqueries.base import BaseDataQuery
from caerp.models.career_path import PERIOD_OPTIONS, CareerPath
from caerp.models.user.utils import (
    get_ongoing_parcours,
    get_tuple_option_label,
    get_user_analytical_accounts,
)
from caerp.utils.dataqueries import dataquery_class

logger = logging.getLogger(__name__)


@dataquery_class()
class ContractsQuery(BaseDataQuery):
    name = "contrats_periode"
    label = "Liste des contrats signés sur une période"
    description = """
    Liste de tous les porteurs de projets ayant une étape de parcours de type "Contrat de travail" sur la période choisie.
    """

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
            "Antenne de rattachement",
            "Typologie d'activité",
            "Date d'entrée dans la CAE",
            "Intitulé du contrat",
            "Date d'effet",
            "Date d'échéance",
            "Type de contrat",
            "Qualité du salarié",
            "Taux horaire",
            "Nombre d'heures",
            "Salaire brut",
            "Objectif de CA / d'activité",
            "Numéro d'avenant",
        ]
        return headers

    def data(self):
        data = []
        contracts = (
            DBSESSION()
            .query(CareerPath)
            .filter(
                or_(
                    CareerPath.stage_type == "contract",
                    CareerPath.stage_type == "amendment",
                )
            )
            .filter(CareerPath.start_date.between(self.start_date, self.end_date))
            .order_by(CareerPath.start_date)
            .all()
        )
        for c in contracts:
            if not c.userdatas:
                logger.waring(f"Career path without userdatas (id={c.id})")
                continue
            parcours = get_ongoing_parcours(c.userdatas.id, at_date=self.end_date)
            goals_amount_str = ""
            if c.goals_amount:
                goals_amount_str = "{} {}".format(
                    c.goals_amount,
                    get_tuple_option_label(PERIOD_OPTIONS, c.goals_period),
                )
            u = c.userdatas
            contract_data = [
                u.user_id,
                get_user_analytical_accounts(u.user_id),
                u.coordonnees_civilite,
                u.coordonnees_lastname,
                u.coordonnees_firstname,
                u.situation_antenne.label if u.situation_antenne else "",
                u.activity_typologie.label if u.activity_typologie else "",
                self.date_tools.format_date(parcours.entry_date),
                c.career_stage.name if c.career_stage else "",
                self.date_tools.format_date(c.start_date),
                self.date_tools.format_date(c.end_date),
                c.type_contrat.label if c.type_contrat else "",
                c.employee_quality.label if c.employee_quality else "",
                c.taux_horaire,
                c.num_hours,
                c.parcours_salary,
                goals_amount_str,
                c.amendment_number,
            ]
            data.append(contract_data)
        return data
