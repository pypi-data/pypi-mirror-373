import logging

from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    ForeignKey,
    Text,
    Numeric,
)

from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)

from caerp.compute.math_utils import integer_to_amount
from .services import PriceStudyDiscountService

logger = log = logging.getLogger(__name__)


class PriceStudyDiscount(DBBASE):
    """
    A discount line
    """

    __tablename__ = "price_study_discount"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )

    description = Column(Text)
    amount = Column(
        BigInteger(),
        default=0,
        info={"colanderalchemy": {"title": "Montant"}},
    )
    percentage = Column(Numeric(4, 2, asdecimal=False), default=0)
    type_ = Column(String(11), default="amount")
    order = Column(Integer, default=0)

    # FKs
    price_study_id = Column(
        ForeignKey(
            "price_study.id",
            ondelete="cascade",
        ),
    )
    tva_id = Column(ForeignKey("tva.id"))
    # Relationships
    price_study = relationship("PriceStudy", back_populates="discounts")
    tva = relationship("Tva")

    _caerp_service = PriceStudyDiscountService

    def get_task(self):
        return self.price_study.task

    @property
    def is_percentage(self):
        return self.type_ == "percentage"

    def __json__(self, request):
        return dict(
            id=self.id,
            price_study_id=self.price_study_id,
            description=self.description,
            amount=integer_to_amount(self.amount, 5, None),
            percentage=self.percentage,
            order=self.order,
            tva_id=self.tva_id,
            type_=self.type_,
            total_ht=integer_to_amount(self.total_ht(), 5),
            total_tva=integer_to_amount(self.total_tva(), 5),
            total_ttc=integer_to_amount(self.total_ttc(), 5),
        )

    def duplicate(self, from_parent=False):
        """
        return the equivalent InvoiceLine
        """
        line = self.__class__()
        line.tva_id = self.tva_id

        line.amount = self.amount
        line.percentage = self.percentage
        line.description = self.description
        line.type_ = self.type_
        line.order = self.order
        if not from_parent:
            line.price_study_id = self.price_study_id
        return line

    # Service proxied methods
    def total_ht(self):
        return self._caerp_service.total_ht(self)

    def total_tva(self):
        return self._caerp_service.total_tva(self)

    def total_ttc(self):
        return self._caerp_service.total_ttc(self)

    def ht_by_tva(self):
        return self._caerp_service.ht_by_tva(self)

    def on_before_commit(self, request, state, attributes=None):
        return self._caerp_service.on_before_commit(request, self, state, attributes)

    def get_company_id(self):
        return self._caerp_service.get_company_id(self)

    def sync_with_task(self, request, price_study=None):
        if price_study is None:
            price_study = self.price_study
        return self._caerp_service.sync_with_task(request, self, price_study)
