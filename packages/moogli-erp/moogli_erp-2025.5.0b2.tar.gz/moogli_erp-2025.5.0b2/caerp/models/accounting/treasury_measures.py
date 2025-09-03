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
    BaseAccountingMeasureTypeCategory,
    BaseAccountingMeasureType,
    BaseAccountingMeasureGrid,
    BaseAccountingMeasure,
)
from caerp.models.accounting.services import (
    TreasuryMeasureGridService,
)


logger = logging.getLogger(__name__)


class TreasuryMeasureTypeCategory(BaseAccountingMeasureTypeCategory):
    """
    Categories joining different TreasuryMeasureTypes
    """

    __tablename__ = "treasury_measure_type_category"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "treasury"}
    __colanderalchemy_config__ = {
        "help_msg": """Les catégories permettent de regrouper les types
        d'indicateurs afin d'en faciliter la configuration.
        Ils peuvent ensuite être utilisé pour calculer des totaux.<br />
        """
    }
    id = Column(
        ForeignKey(
            "base_accounting_measure_type_category.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )


class TreasuryMeasureType(BaseAccountingMeasureType):
    """
    Treasury measure type
    """

    __tablename__ = "treasury_measure_type"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "treasury"}
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


class TreasuryMeasureGrid(BaseAccountingMeasureGrid):
    """
    A grid of measures, one grid per month/year couple

    """

    __tablename__ = "treasury_measure_grid"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "treasury"}

    id = Column(
        ForeignKey(
            "base_accounting_measure_grid.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    date = Column(Date(), info={"colanderalchemy": {"title": "Date du dépôt"}})

    _caerp_service = TreasuryMeasureGridService

    @classmethod
    def last(cls, company_id):
        return cls._caerp_service.last(cls, company_id)


class TreasuryMeasure(BaseAccountingMeasure):
    """
    Stores a treasury_measure measure associated to a given company
    """

    __tablename__ = "treasury_measure"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "treasury"}
    id = Column(
        ForeignKey(
            "base_accounting_measure.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
