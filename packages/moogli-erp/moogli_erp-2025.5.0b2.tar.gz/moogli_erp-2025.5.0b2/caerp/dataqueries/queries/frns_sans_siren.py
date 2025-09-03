from sqlalchemy import or_

from caerp.dataqueries.base import BaseDataQuery
from caerp.models.third_party.supplier import Supplier
from caerp.utils.dataqueries import dataquery_class


@dataquery_class()
class FrnsSansSIRENQuery(BaseDataQuery):

    name = "frns_sans_siren"
    label = "Liste des fournisseurs sans numéro d'immatriculation"
    description = """
    Liste de tous les fournisseurs, toutes enseignes confondues, qui n'ont
    pas encore de numéro d'immatriculation renseigné.
    """

    def headers(self):
        headers = [
            "Raison sociale",
            "Enseigne",
            "Lien",
        ]
        return headers

    def data(self):
        data = []
        suppliers = (
            Supplier.query()
            .filter(or_(Supplier.registration == "", Supplier.registration == None))
            .order_by(Supplier.label)
        )
        for s in suppliers:
            url = self.request.route_path("supplier", id=s.id)
            validations_data = [
                s.label,
                s.company.name,
                f"<a href='{url}'>Voir la fiche</a>",
            ]
            data.append(validations_data)
        return data
