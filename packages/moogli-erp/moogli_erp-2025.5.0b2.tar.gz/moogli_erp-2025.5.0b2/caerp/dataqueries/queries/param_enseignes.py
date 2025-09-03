from caerp.dataqueries.base import BaseDataQuery
from caerp.models.company import Company
from caerp.utils.dataqueries import dataquery_class
from caerp.utils.strings import boolean_to_string


@dataquery_class()
class ParamEnseignesQuery(BaseDataQuery):

    name = "param_enseignes"
    label = "État du paramétrage des enseignes"
    description = """
    Liste de toutes les enseignes active à l'instant T avec le détail de leur 
    paramétrage.
    """

    def headers(self):
        headers = [
            "Compte analytique",
            "Nom de l'enseigne",
            "Enseigne interne ?",
            "Descriptif de l'activité",
            "Activité principale",
            "Antenne de rattachement",
            "Accompagnateur",
            "E-mail",
            "Téléphone",
            "Mobile",
            "Adresse",
            "Code postal",
            "Ville",
            "Pays",
            "Position publiée dans l'annuaire ?",
            "RIB",
            "IBAN",
            "-----",
            "Logo chargé ?",
            "Bannière chargée ?",
            "CGV complémentaires ?",
            "Nombre de décimales",
            "Acompte par défaut",
            "Détails du devis dans les factures ?",
            "-----",
            "Compte client général",
            "Compte client tiers",
            "Compte fournisseur général",
            "Compte fournisseur tiers",
            "Compte client interne général",
            "Compte client interne tiers",
            "Compte fournisseur interne général",
            "Compte fournisseur interne tiers",
            "Compte achat général",
            "-----",
            "Contribution à la CAE",
            "Contribution à la CAE (interne)",
            "Taux d'assurance pro",
            "Taux d'assurance pro (interne)",
            "Coef. frais généraux",
            "Coef. marge",
            "Coef. marge dans le catalogue ?",
        ]
        return headers

    def data(self):
        data = []
        companies = (
            Company.query().filter(Company.active == True).order_by(Company.name)
        )
        for c in companies:
            company_data = [
                c.code_compta,
                c.name,
                boolean_to_string(c.internal),
                c.goal,
                c.activities[0].label if c.activities else "",
                c.antenne.label if c.antenne else "",
                f"{c.follower.lastname} {c.follower.firstname}" if c.follower else "",
                c.email,
                c.phone,
                c.mobile,
                c.address,
                c.zip_code,
                c.city,
                c.country,
                boolean_to_string(c.latitude is not None),
                c.RIB,
                c.IBAN,
                "",
                boolean_to_string(c.logo_id is not None),
                boolean_to_string(c.header_id is not None),
                boolean_to_string(len(c.cgv) > 0) if c.cgv else "Non",
                c.decimal_to_display,
                c.default_estimation_deposit,
                boolean_to_string(c.default_add_estimation_details_in_invoice),
                "",
                c.general_customer_account,
                c.third_party_customer_account,
                c.general_supplier_account,
                c.third_party_supplier_account,
                c.internalgeneral_customer_account,
                c.internalthird_party_customer_account,
                c.internalgeneral_supplier_account,
                c.internalthird_party_supplier_account,
                c.general_expense_account,
                "",
                c.contribution,
                c.internalcontribution,
                c.insurance,
                c.internalinsurance,
                c.general_overhead,
                c.margin_rate,
                boolean_to_string(c.use_margin_rate_in_catalog),
            ]
            data.append(company_data)
        return data
