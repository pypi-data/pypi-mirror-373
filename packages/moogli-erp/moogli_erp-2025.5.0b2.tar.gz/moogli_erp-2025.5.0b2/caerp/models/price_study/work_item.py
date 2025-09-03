"""
Models related to price study work item management

PriceStudyWorkItem
"""
import logging
from typing import Optional
from caerp_base.models.base import DBBASE, default_table_args
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    BigInteger,
    Numeric,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from caerp.compute.math_utils import integer_to_amount
from .services import PriceStudyWorkItemService

logger = logging.getLogger(__name__)


class PriceStudyWorkItem(DBBASE):
    """
    Work item

    Can be locked to the PriceStudyWork for quantity definition

    original associated catalog item
    """

    __table_args__ = default_table_args
    __tablename__ = "price_study_work_item"

    id = Column(Integer, primary_key=True)
    order = Column(Integer, default=0)
    description = Column(Text())
    # Mode de calcul ht / supplier_ht
    mode = Column(String(20), default="supplier_ht", nullable=False)
    # Coût unitaire
    supplier_ht = Column(BigInteger(), default=0)
    # HT unitaire
    ht = Column(BigInteger(), default=0)
    # HT par unité d'oeuvre (synchronisé en fonction de work_unit_quantity)
    work_unit_ht = Column(BigInteger(), default=0)
    # total ht au sein de l'ouvrage (synchronisé)
    total_ht = Column(BigInteger(), default=0)

    unity = Column(
        String(100),
        info={"colanderalchemy": {"title": "Unité"}},
    )
    # Les quantités sont-elles calculées en fonction de l'ouvrage
    # Ou saisit-on directement la quantité finale
    quantity_inherited = Column(Boolean(), default=True)
    # Quantité par unité d'oéuvre
    work_unit_quantity = Column(Numeric(15, 5, asdecimal=False), default=1)
    # Quantité globale au sein d'un ouvrage : synchonisé lors de la modification
    # des quantités de l'ouvrage parent
    total_quantity = Column(Numeric(15, 5, asdecimal=False), default=1)

    # FKs
    price_study_work_id = Column(ForeignKey("price_study_work.id", ondelete="CASCADE"))
    base_sale_product_id = Column(
        ForeignKey("base_sale_product.id", ondelete="SET NULL")
    )
    # Relationships
    price_study_work = relationship(
        "PriceStudyWork",
        foreign_keys=[price_study_work_id],
        info={"colanderalchemy": {"exclude": True}},
        back_populates="items",
    )
    base_sale_product = relationship("BaseSaleProduct")

    _caerp_service = PriceStudyWorkItemService

    def __json__(self, request):
        return dict(
            id=self.id,
            supplier_ht=integer_to_amount(self.supplier_ht, 5, None),
            ht=integer_to_amount(self.ht, 5, 0),
            work_unit_ht=integer_to_amount(self.work_unit_ht, 5, 0),
            total_ht=integer_to_amount(self.total_ht, 5, 0),
            unity=self.unity,
            price_study_work_id=self.price_study_work_id,
            description=self.description,
            work_unit_quantity=self.work_unit_quantity,
            total_quantity=self.total_quantity,
            quantity_inherited=self.quantity_inherited,
            mode=self.mode,
            order=self.order,
        )

    @classmethod
    def from_work_item(cls, price_study_work, catalog_work_item):
        """
        Load a price study work item from a catalog one
        """
        instance = cls()
        instance.price_study_work = price_study_work

        for field in (
            "description",
            "supplier_ht",
            "ht",
            "unity",
            "total_ht",
            "mode",
            "base_sale_product_id",
        ):
            setattr(instance, field, getattr(catalog_work_item, field, None))

        instance.work_unit_quantity = catalog_work_item.quantity
        instance.total_quantity = catalog_work_item.quantity
        instance.work_unit_ht = catalog_work_item.total_ht
        return instance

    @classmethod
    def from_sale_product(cls, catalog_sale_product):
        """
        Load a price study work item from a catalog product
        """
        instance = cls(work_unit_quantity=1)

        instance.supplier_ht = getattr(catalog_sale_product, "supplier_ht", None)

        for field in (
            "ht",
            "description",
            "unity",
            "mode",
        ):
            setattr(instance, field, getattr(catalog_sale_product, field, None))

        instance.work_unit_ht = catalog_sale_product.ht
        instance.base_sale_product = catalog_sale_product

        return instance

    def duplicate(self, from_parent=False, force_ht=False, remove_cost=False):
        """
        Duplicate an element

        :param bool from_parent: We are duplicating the whole tree, the parent is not
        the same as the current's instance
        :param bool force_ht: Should we force ht mode while duplicating ?
        """
        instance = self.__class__()

        for field in (
            "description",
            "total_ht",
            "ht",
            "unity",
            "work_unit_quantity",
            "total_quantity",
            "quantity_inherited",
            "work_unit_ht",
            "base_sale_product_id",
        ):
            setattr(instance, field, getattr(self, field, None))

        if remove_cost:
            for field in ("ht", "total_ht", "work_unit_ht"):
                setattr(instance, field, 0)

        if not force_ht:
            for field in "supplier_ht", "mode":
                setattr(instance, field, getattr(self, field, None))
        else:
            instance.supplier_ht = 0
            instance.mode = "ht"

        if not from_parent:
            instance.price_study_work_id = self.price_study_work_id

        return instance

    def get_company_id(self) -> Optional[int]:
        """
        :returns: the Company id object associated to this WorkItem
        """
        return self._caerp_service.get_company_id(self)

    def get_company(self):
        """
        :returns: the Company object associated to this WorkItem
        """
        return self._caerp_service.get_company(self)

    def get_tva(self):
        """
        Return the Tva object associated to this WorkItem

        :rtype: `class::caerp.models.tva.Tva`
        """
        return self._caerp_service.get_tva(self)

    def get_margin_rate(self) -> float:
        """
        Collect the margin rate that should be used to compute the
        Salt Ht based on the cost price
        """
        result = None
        if self.price_study_work:
            result = self.price_study_work.margin_rate
        return result

    def get_general_overhead(self) -> float:
        """
        Collect the general overhead that should be used to compute the
        Salt Ht based on the cost price
        """
        result = None
        if self.price_study_work:
            result = self.price_study_work.get_general_overhead()
        return result

    def get_task(self):
        """
        Collect the Task instance associated to this WorkItem

        :rtype: `class::caerp.models.task.Task`
        """
        result = None
        if self.price_study_work:
            result = self.price_study_work.get_task()
        return result

    def get_price_study(self):
        result = None
        if self.price_study_work:
            result = self.price_study_work.price_study
        return result

    # Computing tools
    def flat_cost(self, unitary=False, work_level=False) -> int:
        """
        Flat cost : Cost price without any computation

        :param bool unitary: Cost by Work unit ?
        """
        return self._caerp_service.flat_cost(self, unitary, work_level)

    def cost_price(self, unitary=False) -> int:
        """
        Coût d'achat + frais généraux

        :param bool unitary: Cost by Work unit ?
        """
        return self._caerp_service.cost_price(self, unitary)

    def intermediate_price(self, unitary=False) -> int:
        """
        Coût d'achat + frais généraux + marge

        :param bool unitary: Cost by Work unit ?
        """
        return self._caerp_service.intermediate_price(self, unitary)

    def price_with_contribution(self, unitary=False, base_price=None) -> int:
        """
        Prix avec contribution (si elle est utilisée dans les calculs)

        :param bool unitary: Cost by Work unit ?
        """
        return self._caerp_service.price_with_contribution(self, unitary, base_price)

    def price_with_insurance(self, unitary=False, base_price=None) -> int:
        """
        Prix avec assurance (si elle est utilisée dans les calculs)

        :param bool unitary: Cost by Work unit ?
        """
        return self._caerp_service.price_with_insurance(self, unitary, base_price)

    def unit_ht(self) -> int:
        """
        Prix unitaire HT
        """
        return self._caerp_service.unit_ht(self)

    def compute_work_unit_ht(self) -> int:
        """
        Renvoie le Prix HT par unité d'ouvrage
        """
        return self._caerp_service.compute_work_unit_ht(self)

    def compute_total_ht(self) -> int:
        """
        Renvoie le prix HT total PU * qtité par unité d'ouvrage * qtité d'ouvrage
        """
        return self._caerp_service.compute_total_ht(self)

    def compute_total_tva(self) -> int:
        """
        Renvoie le montant de la Tva
        """
        return self._caerp_service.compute_total_tva(self)

    def ht_by_tva(self) -> dict:
        """
        :returns: {<Tva>: ht}

        :rtype: dict
        """
        return self._caerp_service.ht_by_tva(self)

    def ttc(self):
        """
        Prix TTC de ce WorkItem

        :rtype: int
        """
        return self._caerp_service.ttc(self)

    def sync_amounts(self, work=None):
        """
        Sync the computed amounts on the object (and sync the parents)

        :param obj work: The parent price_study_work
        """
        return self._caerp_service.sync_amounts(self, work=None)

    def sync_quantities(self, work=None):
        """
        Sync the work_quantities in the current item

        :param obj work: The parent price_study_work
        """
        return self._caerp_service.sync_quantities(self, work)

    def on_before_commit(self, request, state: str, changed_attrs=None):
        """
        Hook to be launched before commit

        :param obj request:
        :param str state: 'add'/'update'/'delete'
        :param list changed_attrs: List of changed attrs (in case of add/update)
        """
        return self._caerp_service.on_before_commit(request, self, state, changed_attrs)
