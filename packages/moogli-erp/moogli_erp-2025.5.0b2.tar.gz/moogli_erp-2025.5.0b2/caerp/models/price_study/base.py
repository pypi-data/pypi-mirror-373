from caerp_base.models.base import DBBASE, default_table_args
from caerp_base.models.mixins import TimeStampedMixin
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from caerp.compute.math_utils import integer_to_amount

from .services import BasePriceStudyProductService


class BasePriceStudyProduct(DBBASE, TimeStampedMixin):
    """
    Base class for PriceStudyProducts and PriceStudyWorks
    """

    __tablename__ = "base_price_study_product"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": __tablename__,
    }
    id = Column(
        Integer,
        primary_key=True,
    )
    type_ = Column("type_", String(30), nullable=False)
    margin_rate = Column(Numeric(6, 5, asdecimal=False))

    # Coût unitaire
    ht = Column(BigInteger(), default=0)

    description = Column(Text())
    unity = Column(
        String(100),
        info={"colanderalchemy": {"title": "Unité"}},
    )
    quantity = Column(
        Numeric(15, 5, asdecimal=False),
        info={"colanderalchemy": {"title": "Quantité"}},
        default=1,
    )
    total_ht = Column(BigInteger(), default=0)

    order = Column(Integer, default=0)

    # FKs
    chapter_id = Column(
        ForeignKey("price_study_chapter.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(Integer, ForeignKey("product.id"))
    tva_id = Column(Integer, ForeignKey("tva.id"))
    task_line_id = Column(ForeignKey("task_line.id", ondelete="SET NULL"))
    # Relationships
    chapter = relationship(
        "PriceStudyChapter",
        primaryjoin="PriceStudyChapter.id==BasePriceStudyProduct.chapter_id",
        back_populates="products",
    )
    tva = relationship("Tva")
    product = relationship("Product")
    task_line = relationship(
        "TaskLine", back_populates="price_study_product", cascade="all, delete"
    )

    # view_only Relationship
    price_study = relationship(
        "PriceStudy",
        uselist=False,
        secondary="price_study_chapter",
        primaryjoin="PriceStudyChapter.id==BasePriceStudyProduct.chapter_id",
        secondaryjoin="PriceStudyChapter.price_study_id==PriceStudy.id",
        viewonly=True,
        back_populates="products",
    )

    TYPE_LABELS = {
        "price_study_work": "Ouvrage",
        "price_study_product": "Produit simple",
    }
    _caerp_service = BasePriceStudyProductService

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} id:{self.id} "
            f"ht={self.ht} "
            f"unity={self.unity} "
            f"quantity={self.quantity} "
            f"total_ht={self.total_ht} "
            f"product_id={self.product_id} "
            f"tva_id={self.tva_id} "
            f"chapter_id={self.chapter_id}>"
        )

    def __json__(self, request):
        return dict(
            id=self.id,
            chapter_id=self.chapter_id,
            type_=self.type_,
            margin_rate=self.margin_rate,
            ht=integer_to_amount(self.ht, 5, 0),
            description=self.description,
            product_id=self.product_id,
            tva_id=self.tva_id,
            unity=self.unity,
            quantity=self.quantity,
            total_ht=integer_to_amount(self.total_ht, 5),
            order=self.order,
        )

    @classmethod
    def from_sale_product(cls, sale_product):
        instance = cls(quantity=1)
        for field in (
            "ht",
            "description",
            "unity",
        ):
            setattr(instance, field, getattr(sale_product, field, None))

        if sale_product.company:
            margin_rate = sale_product.company.margin_rate
            if (
                sale_product.company.use_margin_rate_in_catalog
                and sale_product.margin_rate
            ):
                margin_rate = sale_product.margin_rate

            instance.margin_rate = margin_rate

        return instance

    def duplicate(self, from_parent=False, force_ht=False, remove_cost=False):
        """
        :param bool from_parent: We are duplicating the whole tree, the parent is not
        the same as the current's instance
        :param bool force_ht: Should we force ht mode while duplicating ?
        """
        instance = self.__class__()
        for field in (
            "ht",
            "description",
            "unity",
            "quantity",
            "total_ht",
        ):
            setattr(instance, field, getattr(self, field, None))

        for field in ("tva_id", "tva", "product_id", "product"):
            value = getattr(self, field, None)
            if value is not None:
                setattr(instance, field, value)

        if remove_cost:
            instance.ht = 0
            instance.total_ht = 0

        if not from_parent:
            instance.chapter_id = self.chapter_id

        if not force_ht:
            company = self.get_company()
            if company and company.margin_rate:
                margin_rate = company.margin_rate
            else:
                margin_rate = self.margin_rate
            instance.margin_rate = margin_rate
        return instance

    def get_company_id(self):
        return self._caerp_service.get_company_id(self)

    def get_company(self):
        return self._caerp_service.get_company(self)

    def get_general_overhead(self):
        result = None
        if self.chapter:
            result = self.chapter.get_general_overhead()
        return result

    def get_task(self):
        result = None
        if self.chapter:
            result = self.chapter.get_task()
        return result

    # Computing tools
    def flat_cost(self):
        return self._caerp_service.flat_cost(self)

    def cost_price(self):
        return self._caerp_service.cost_price(self)

    def intermediate_price(self):
        return self._caerp_service.intermediate_price(self)

    def price_with_contribution(self, base_price=None):
        return self._caerp_service.price_with_contribution(self, base_price)

    def price_with_insurance(self, base_price=None):
        return self._caerp_service.price_with_insurance(self, base_price)

    def unit_ht(self):
        return self._caerp_service.unit_ht(self)

    def compute_total_ht(self):
        return self._caerp_service.compute_total_ht(self)

    def ht_by_tva(self):
        return self._caerp_service.ht_by_tva(self)

    def ttc(self):
        return self._caerp_service.ttc(self)

    def sync_amounts(self, propagate=True):
        """
        Set cached amounts on the current object

        :param bool propagate: Should we propagate the syncing up (else we sync down in
        case of PriceStudyWork entries) ?
        """
        return self._caerp_service.sync_amounts(self, propagate=propagate)

    def on_before_commit(self, request, state, attributes=None):
        return self._caerp_service.on_before_commit(request, self, state, attributes)

    def sync_with_task(self, request):
        return self._caerp_service.sync_with_task(request, self, self.chapter)
