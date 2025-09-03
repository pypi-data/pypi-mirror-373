from sqlalchemy import func, or_

from caerp_base.models.base import DBSESSION
from caerp.models.node import Node
from caerp.models.status import StatusLogEntry
from caerp.models.user import User
from caerp.dataqueries.base import BaseDataQuery
from caerp.utils.dataqueries import dataquery_class


@dataquery_class()
class ValidationsQuery(BaseDataQuery):

    name = "validations"
    label = "Nombre de validations par utilisateur sur une période"
    description = """
    Nombre de validations (acceptées ou refusées) réalisés par utilisateur 
    et par type de document sur la période choisie.
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "Utilisateur",
            "Type de document",
            "Nombre de validations",
        ]
        return headers

    def data(self):
        data = []
        validations = (
            DBSESSION()
            .query(
                StatusLogEntry,
                User,
                Node,
                func.count(StatusLogEntry.id).label("NbVal"),
            )
            .join(
                StatusLogEntry.user,
                StatusLogEntry.node,
            )
            .filter(
                or_(
                    StatusLogEntry.state_manager_key == "status",
                    StatusLogEntry.state_manager_key == "validation_status",
                )
            )
            .filter(
                or_(
                    StatusLogEntry.status == "valid",
                    StatusLogEntry.status == "invalid",
                )
            )
            .filter(StatusLogEntry.datetime.between(self.start_date, self.end_date))
            .group_by(StatusLogEntry.user_id, Node.type_)
            .order_by(User.lastname, User.firstname)
            .all()
        )
        for v in validations:
            validations_data = [
                f"{v.User.lastname} {v.User.firstname}",
                v.Node.type_label,
                v.NbVal,
            ]
            data.append(validations_data)
        data.sort(key=lambda i: (i[0], i[1]))
        return data
