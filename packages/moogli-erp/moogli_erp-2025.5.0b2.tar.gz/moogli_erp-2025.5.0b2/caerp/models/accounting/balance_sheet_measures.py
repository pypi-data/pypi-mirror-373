import logging

from sqlalchemy import (
    Column,
    ForeignKey,
    Date,
)

from caerp_base.models.base import (
    default_table_args,
)
from caerp.models.accounting.base import (
    BaseAccountingMeasureType,
    BaseAccountingMeasureGrid,
    BaseAccountingMeasure,
)
from caerp.models.accounting.services import (
    BalanceSheetMeasureGridService,
)


logger = logging.getLogger(__name__)


class BalanceSheetMeasureType(BaseAccountingMeasureType):
    """
    Balance sheet measure type
    """

    __tablename__ = "balance_sheet_measure_type"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "balance_sheet"}
    __colanderalchemy_config__ = {
        "help_msg": """Les indicateurs de comptes résultats permettent de
        regrouper des écritures sous un même libellé.<br />
        Ils permettent d'assembler les comptes de résultats des entrepreneurs.
        <br />Vous pouvez définir ici les préfixes de comptes généraux pour
        indiquer quelles écritures doivent être utilisées pour calculer cet
        indicateur.
        <br />
        Si nécessaire vous pourrez alors recalculer les derniers indicateurs
        générés.
        """
    }
    id = Column(
        ForeignKey(
            "base_accounting_measure_type.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    @staticmethod
    def default_sign():
        return 1


class ActiveBalanceSheetMeasureType(BalanceSheetMeasureType):
    __tablename__ = "active_balance_sheet_measure_type"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "active_balance_sheet"}
    id = Column(
        ForeignKey(
            "balance_sheet_measure_type.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )


class PassiveBalanceSheetMeasureType(BalanceSheetMeasureType):
    __tablename__ = "passive_balance_sheet_measure_type"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "passive_balance_sheet"}
    id = Column(
        ForeignKey(
            "balance_sheet_measure_type.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )


class BalanceSheetMeasureGrid(BaseAccountingMeasureGrid):
    """
    A grid of measures, one grid per month/year couple

    """

    __tablename__ = "balance_sheet_measure_grid"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "balance_sheet"}

    id = Column(
        ForeignKey(
            "base_accounting_measure_grid.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    date = Column(Date(), info={"colanderalchemy": {"title": "Date du dépôt"}})

    _caerp_service = BalanceSheetMeasureGridService

    @classmethod
    def last(cls, company_id):
        return cls._caerp_service.last(cls, company_id)

    @classmethod
    def get_grid_from_year(cls, company_id, year):
        return cls._caerp_service.get_grid_from_year(cls, company_id, year)


class BalanceSheetMeasure(BaseAccountingMeasure):
    """
    Stores a treasury_measure measure associated to a given company
    """

    __tablename__ = "balance_sheet_measure"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "balance_sheet"}
    id = Column(
        ForeignKey(
            "base_accounting_measure.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
