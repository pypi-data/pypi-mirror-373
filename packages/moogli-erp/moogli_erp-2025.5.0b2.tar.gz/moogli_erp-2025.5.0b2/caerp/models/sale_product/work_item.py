"""
Models related to work item management

WorkItem
"""
import logging
from sqlalchemy.orm import (
    relationship,
)
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    ForeignKey,
    Text,
    String,
    Numeric,
    Boolean,
)
from sqlalchemy.ext.hybrid import hybrid_property
from caerp_base.models.base import DBBASE, default_table_args
from caerp.compute.math_utils import integer_to_amount
from .sale_product import (
    SaleProductProduct,
    SaleProductWorkForce,
    SaleProductMaterial,
    SaleProductServiceDelivery,
)
from .services import WorkItemService


logger = logging.getLogger(__name__)


class WorkItem(DBBASE):
    """
    id

    Ventes

        type_
        ht (product ht)
        total_ht (ht * quantity)
        unity
        quantity
        base_sale_product_id (relationship)
        work_id (relationshio)
        product_id (relationship)
        tva_id (relationship)
        description
    """

    __table_args__ = default_table_args
    __tablename__ = "sale_catalog_work_item"

    id = Column(Integer, primary_key=True)
    type_ = Column("type_", String(30), nullable=False)
    # Indique si le work item hérite directement des informations de son
    # base_sale_product associé
    locked = Column(Boolean(), default=True)

    # Champs utilisés si locked est à False
    # Mode de calcul ht / supplier_ht
    _mode = Column(String(20), default="ht", nullable=False)
    _supplier_ht = Column(BigInteger())
    _ht = Column(BigInteger())
    _unity = Column(
        String(100),
        info={"colanderalchemy": {"title": "Unité"}},
    )

    # Specific fields
    description = Column(
        Text(),
        info={"colanderalchemy": {"title": "Description"}},
    )
    quantity = Column(
        Numeric(15, 5, asdecimal=False),
        info={"colanderalchemy": {"title": "Quantité"}},
        default=1,
    )
    # ht total part for this item
    total_ht = Column(BigInteger(), default=0)
    base_sale_product_id = Column(
        Integer, ForeignKey("base_sale_product.id"), nullable=False
    )
    sale_product_work_id = Column(
        Integer, ForeignKey("sale_product_work.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    base_sale_product = relationship(
        "BaseSaleProduct",
        foreign_keys=[base_sale_product_id],
        info={"colanderalchemy": {"exclude": True}},
    )
    sale_product_work = relationship(
        "SaleProductWork",
        foreign_keys=[sale_product_work_id],
        info={"colanderalchemy": {"exclude": True}},
    )

    _caerp_service = WorkItemService

    SALE_PRODUCT_FACTORIES = {
        "sale_product_product": SaleProductProduct,
        "sale_product_material": SaleProductMaterial,
        "sale_product_work_force": SaleProductWorkForce,
        "sale_product_service_delivery": SaleProductServiceDelivery,
    }

    def get_company(self):
        return getattr(self.sale_product_work, "company", None)

    def get_tva(self):
        return getattr(self.sale_product_work, "tva", None)

    def generate_sale_product(self, label, category_id, company, **attributes):
        """
        Generate a sale product from a work item object

        :param str label: The label configured by the user when creating the
        workitem
        :param category_id: the category
        :param company_id: the company we're working on
        :param dict attributes: The submitted datas (are not all set at this
        stage)
        :return: BasSaleProduct Object
        """
        result = self.SALE_PRODUCT_FACTORIES[self.type_]()

        result.label = label
        result.category_id = category_id
        result.company = company

        for key in (
            "description",
            "supplier_ht",
            "ht",
            "unity",
            "mode",
        ):

            if key in attributes:
                value = attributes[key]
            else:
                value = getattr(self, key, None)

            if value:
                setattr(result, key, value)
        return result

    def sync_base_sale_product(self):
        """
        Synchronize associated base_sale_product with the current work items
        info

        :return: BasSaleProduct Object
        """
        base_sale_product = self.base_sale_product
        if base_sale_product is None:
            raise Exception(
                "We try to synchronize a work item with a "
                "non-existing base_sale_product"
            )

        logger.debug("Syncing base product, ht : %s" % self.ht)

        base_sale_product.description = self.description

        # On synchronise le ht que si il n'a pas été calculé : si le coût HT
        # n'est pas renseigné
        if self._supplier_ht in (None, 0):
            if self._ht not in (None, 0):
                base_sale_product.ht = self._ht

        keys_to_sync = (
            "mode",
            "supplier_ht",
            "ht",
            "unity",
        )
        changes = {}
        for key in keys_to_sync:
            value = getattr(self, key)
            if value is not None:
                changes[key] = value
                setattr(base_sale_product, key, value)

        base_sale_product.on_before_commit("update", changes)

        return base_sale_product

    @classmethod
    def from_base_sale_product(cls, sale_product):
        """
        Create a new instance generated from the given sale_product
        """
        result = cls()
        result.type_ = sale_product.type_
        result.base_sale_product_id = sale_product.id
        result.base_sale_product = sale_product
        result.description = sale_product.description
        result.locked = True
        return result

    # Properties forwarding the values to the parent sale_product
    @hybrid_property
    def mode(self):
        if self.locked and self.base_sale_product_id:
            return self.base_sale_product.mode
        else:
            return self._mode

    @mode.setter
    def mode(self, value):
        if self.locked and self.base_sale_product_id:
            self.base_sale_product.mode = value
        else:
            self._mode = value

    # Properties forwarding the values to the parent sale_product
    @hybrid_property
    def ht(self):
        if self.locked and self.base_sale_product_id:
            return self.base_sale_product.ht
        else:
            return self._ht

    @ht.setter
    def ht(self, value):
        if self.locked and self.base_sale_product_id:
            self.base_sale_product.ht = value
        else:
            self._ht = value

    @hybrid_property
    def supplier_ht(self):
        if self.locked and self.base_sale_product_id:
            return self.base_sale_product.supplier_ht
        else:
            return self._supplier_ht

    @supplier_ht.setter
    def supplier_ht(self, value):
        if self.locked and self.base_sale_product_id:
            self.base_sale_product.supplier_ht = value
        else:
            self._supplier_ht = value

    @hybrid_property
    def unity(self):
        if self.locked and self.base_sale_product_id:
            return self.base_sale_product.unity
        else:
            return self._unity

    @unity.setter
    def unity(self, value):
        if self.locked and self.base_sale_product_id:
            self.base_sale_product.unity = value
        else:
            self._unity = value

    def __json__(self, request):
        return dict(
            id=self.id,
            label=self.base_sale_product.label,
            type_=self.type_,
            supplier_ht=integer_to_amount(self.supplier_ht, 5, None),
            ht=integer_to_amount(self.ht, 5, None),
            total_ht=integer_to_amount(self.total_ht, 5, None),
            unity=self.unity,
            quantity=self.quantity,
            base_sale_product_id=self.base_sale_product_id,
            sale_product_work_id=self.sale_product_work_id,
            description=self.description,
            locked=self.locked,
            mode=self.mode,
        )

    def flat_cost(self, unitary=False):
        return self._caerp_service.flat_cost(self, unitary)

    def cost_price(self, unitary=False):
        return self._caerp_service.cost_price(self, unitary)

    def intermediate_price(self, unitary=False):
        return self._caerp_service.intermediate_price(self, unitary)

    def price_with_contribution(self, unitary=False, base_sale_price=None):
        return self._caerp_service.price_with_contribution(
            self, unitary, base_sale_price
        )

    def price_with_insurance(self, unitary=False, base_sale_price=None):
        return self._caerp_service.price_with_insurance(self, unitary, base_sale_price)

    def unit_ht(self):
        return self._caerp_service.unit_ht(self)

    def compute_total_ht(self):
        return self._caerp_service.compute_total_ht(self)

    def total_ttc(self, tva=None):
        return self._caerp_service.total_ttc(self, tva)

    def sync_amounts(self, work=None):
        return self._caerp_service.sync_amounts(self, work=None)

    def on_before_commit(self, state, changes=None):
        self._caerp_service.on_before_commit(self, state, changes=changes)

    def duplicate(self):
        result = self.__class__()
        result.base_sale_product_id = self.base_sale_product_id
        result.type_ = self.type_
        result.locked = self.locked and self.base_sale_product_id is not None
        result.description = self.description
        result.quantity = self.quantity
        result.total_ht = self.total_ht
        result._ht = self._ht
        result._supplier_ht = self._supplier_ht
        result._unity = self._unity
        result._mode = self._mode
        return result

    def get_company_id(self):
        return self.sale_product_work.company_id
