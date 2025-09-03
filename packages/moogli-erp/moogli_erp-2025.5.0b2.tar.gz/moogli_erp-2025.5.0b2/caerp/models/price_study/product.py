"""
Models related to price study product management

PriceStudyProduct
"""
from caerp_base.models.base import default_table_args
from sqlalchemy import (
    Column,
    ForeignKey,
    BigInteger,
    String,
)
from sqlalchemy.orm import relationship

from caerp.compute.math_utils import integer_to_amount
from .base import BasePriceStudyProduct
from .services import PriceStudyProductService


class PriceStudyProduct(BasePriceStudyProduct):
    """
    price study product
    """

    __tablename__ = "price_study_product"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": __tablename__,
    }
    id = Column(
        ForeignKey("base_price_study_product.id", ondelete="CASCADE"), primary_key=True
    )
    # Mode de calcul ht / supplier_ht
    mode = Column(String(20), default="supplier_ht", nullable=False)
    supplier_ht = Column(BigInteger(), default=0)
    # FKs
    base_sale_product_id = Column(
        ForeignKey("base_sale_product.id", ondelete="SET NULL")
    )
    # Relationships
    base_sale_product = relationship(
        "BaseSaleProduct",
        foreign_keys=[base_sale_product_id],
        info={"colanderalchemy": {"exclude": True}},
    )

    _caerp_service = PriceStudyProductService

    def __json__(self, request):
        result = BasePriceStudyProduct.__json__(self, request)
        result.update(
            dict(
                supplier_ht=integer_to_amount(self.supplier_ht, 5, None),
                mode=self.mode,
            )
        )
        return result

    @classmethod
    def from_sale_product(cls, sale_product):
        instance = super(PriceStudyProduct, cls).from_sale_product(sale_product)
        instance.supplier_ht = getattr(sale_product, "supplier_ht", None)
        instance.mode = getattr(sale_product, "mode", "ht")
        instance.base_sale_product = sale_product
        return instance

    def duplicate(self, from_parent=False, force_ht=False, remove_cost=False):
        """
        :param bool from_parent: We are duplicating the whole tree, the parent is not
        the same as the current's instance
        :param bool force_ht: Should we force ht mode while duplicating ?
        """
        instance = super().duplicate(from_parent, force_ht, remove_cost)
        instance.base_sale_product_id = self.base_sale_product_id
        if not force_ht:
            for field in ("supplier_ht", "mode"):
                setattr(instance, field, getattr(self, field, None))
        else:
            instance.supplier_ht = 0
            instance.mode = "ht"

        return instance
