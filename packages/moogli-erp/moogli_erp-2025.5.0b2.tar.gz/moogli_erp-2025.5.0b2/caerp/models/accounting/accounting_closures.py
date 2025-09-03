import logging

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)

logger = logging.getLogger(__name__)


class AccountingClosure(DBBASE):
    """
    Accounting closure class to store information about closures
    :param year: year of the closure
    :param active: default value will be false, value will be true after
    cosure
    :param datetime: the date and time where it has been closed (if empty,
    was never closed)
    """

    __colanderalchemy_config__ = {
        "title": "Clôtures comptables",
        "validation_msg": "Les modifications sur les clôtures comptables ont\
            bien été enregistrés",
        "help_msg": "Permet ensuite de clôturer les exercices",
    }
    __tablename__ = "accounting_closure"
    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True, info={"colanderalchemy": {"exclude": True}})
    year = Column(
        Integer,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Année de fin de l'exercice fiscal à clôturer",
            }
        },
    )
    active = Column(  # active means closed
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {"title": "Exercice comptable clos ?", "exclude": True}
        },
    )
    datetime = Column(
        DateTime(),
        nullable=True,
    )

    def __json__(self, request=None):
        return {
            "id": self.id,
            "year": self.year,
            "active": self.active,
            "datetime": self.datetime,
        }
