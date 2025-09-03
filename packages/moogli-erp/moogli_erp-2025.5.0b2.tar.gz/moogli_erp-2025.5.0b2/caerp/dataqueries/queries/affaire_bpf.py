import logging

from caerp.compute.math_utils import integer_to_amount
from caerp.dataqueries.base import BaseDataQuery
from caerp.services.business_bpf import (
    get_training_businesses_with_invoices_query,
    get_business_bpf_data_query,
    get_training_goal,
)
from caerp.utils.dataqueries import dataquery_class
from caerp.utils.strings import boolean_to_string

logger = logging.getLogger(__name__)


@dataquery_class()
class BusinessBPFCheckQuery(BaseDataQuery):
    """
    Data query demandée par Suite 126.

    TODO : Restreindre le filtre sur une année donnée.
    Aujourd'hui on prend l'année de la date de départ comme référence,
    ce qui peut induire l'utilisateur en erreur (on n'export qu'une année
    alors qu'il peut en sélectionner deux).

    Liste des affaires de formation sur une année donnée :
        "Enseigne",
        "Nom de l'affaire",
        "Type d'affaire",
        "Client",
        "Année fiscale",
        "Liste des numéros de factures/avoirs",
        "Cette formation est-elle portée en direct par la CAE ?",
        "Cette formation est-elle sous-traitée à un autre OF ?",
        "Nombre de stagiaires",
        "Nb. Heures total suivies par l'ensemble des stagiaires",
        "Cette formation est-elle tout ou partie en distanciel ?",
        "Objectif principal de formation",
        "Spécialité de formation",
        "Montant total des factures HT",
        "Montant total des factures TTC",

    Note sur les factures :
     - On exporte les factures avoir rattachée à l'année fiscale que l'on exporte,
     qu'elles soient renseignées comme source de revenu dans le BPF ou pas.

    """

    name = "business_bpf_check"
    label = "Liste des affaires liées au BPF"
    description = """
    <p>Éléments permettant le contrôle des données saisies dans le cadre de l'activité 
    de formation professionnelle.</p>
    <p>La requête fonctionne sur année fiscale.</p>
    """

    def default_dates(self):
        self.start_date = self.date_tools.previous_year_start()
        self.end_date = self.date_tools.previous_year_end()

    def get_financial_year(self) -> int:
        return self.start_date.year

    def headers(self):
        headers = [
            "Enseigne",
            "Nom de l'affaire",
            "Type d'affaire",
            "Client",
            "Année fiscale",
            "Liste des numéros de factures/avoirs",
            "Cette formation est-elle portée en direct par la CAE ?",
            "Cette formation est-elle sous-traitée à un autre OF ?",
            "Nombre de stagiaires",
            "Nb. Heures total suivies par l'ensemble des stagiaires",
            "Cette formation est-elle tout ou partie en distanciel ?",
            "Objectif principal de formation",
            "Spécialité de formation",
            "Montant total des factures HT",
            "Montant total des factures TTC",
        ]
        return headers

    def data(self):
        data = []
        query = get_training_businesses_with_invoices_query(
            self.start_date, self.end_date
        )
        financial_year = self.get_financial_year()
        for business in self.request.dbsession.execute(query).scalars():
            business_data = [
                business.project.company.name,
                business.name,
                business.business_type.label,
                business.get_customer().name,
            ]
            business_data.append(str(financial_year))

            bpf_data = (
                self.request.dbsession.execute(
                    get_business_bpf_data_query(business.id, financial_year)
                )
                .scalars()
                .first()
            )
            valid_invoices = [
                invoice
                for invoice in business.invoices
                if invoice.status == "valid"
                and invoice.financial_year == financial_year
            ]
            if valid_invoices:
                business_data.append(
                    "\n ".join(invoice.official_number for invoice in valid_invoices)
                )
            else:
                business_data.append("")

            if bpf_data:
                logger.debug(f"Found BPF data for {business.id} in {financial_year}")
                logger.debug(f"Data: {bpf_data}")
                goal = get_training_goal(financial_year, bpf_data)
                business_data.extend(
                    [
                        boolean_to_string(not bpf_data.is_subcontract),
                        boolean_to_string(not bpf_data.has_subcontract),
                        bpf_data.headcount if bpf_data.headcount else "",
                        bpf_data.total_hours if bpf_data.total_hours else "",
                        boolean_to_string(bpf_data.has_remote),
                        goal if goal else "",
                        bpf_data.training_speciality.label
                        if bpf_data.training_speciality
                        else "",
                    ]
                )
            else:
                business_data.extend([""] * 7)
            business_data.append(
                integer_to_amount(
                    sum(invoice.ht for invoice in valid_invoices),
                    5,
                )
            )
            business_data.append(
                integer_to_amount(
                    sum(invoice.ttc for invoice in valid_invoices),
                    5,
                )
            )

            data.append(business_data)
        return data
