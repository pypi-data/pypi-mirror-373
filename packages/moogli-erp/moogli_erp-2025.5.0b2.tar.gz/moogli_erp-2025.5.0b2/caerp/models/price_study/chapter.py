from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from caerp_base.models.base import DBBASE, default_table_args

from caerp.compute.math_utils import integer_to_amount

from .services import PriceStudyChapterService


class PriceStudyChapter(DBBASE):
    """
    Chapitre : Correspond au TaskLineGroup du document associé
    """

    __tablename__ = "price_study_chapter"
    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(255), default="")
    description = Column(Text(), default="")
    price_study_id = Column(
        ForeignKey(
            "price_study.id",
            ondelete="cascade",
        ),
    )
    order = Column(Integer, default=0)
    display_details = Column(Boolean(), default=True)

    # FKs
    task_line_group_id = Column(ForeignKey("task_line_group.id", ondelete="set null"))
    # relationships
    price_study = relationship("PriceStudy", back_populates="chapters")
    task_line_group = relationship(
        "TaskLineGroup", back_populates="price_study_chapter", cascade="all, delete"
    )
    products = relationship(
        "BasePriceStudyProduct",
        order_by="BasePriceStudyProduct.order",
        collection_class=ordering_list("order"),
        cascade="all, delete",
        back_populates="chapter",
    )

    _caerp_service = PriceStudyChapterService

    def get_task(self):
        result = None
        if self.price_study:
            result = self.price_study.task
        return result

    def get_company(self):
        return self._caerp_service.get_company(self)

    def get_company_id(self):
        return self._caerp_service.get_company_id(self)

    def get_general_overhead(self):
        result = None
        if self.price_study:
            result = self.price_study.general_overhead
        return result

    def __json__(self, request):
        return {
            "id": self.id,
            "title": self.title,
            "display_details": self.display_details,
            "description": self.description,
            "price_study_id": self.price_study_id,
            "order": self.order,
            "task_line_group_id": self.task_line_group_id,
            "products": self.products,
            "total_ht": integer_to_amount(self.total_ht(request), 5),
        }

    def duplicate(self, from_parent=False, force_ht=False, remove_cost=False):
        instance = self.__class__()
        instance.title = self.title
        instance.description = self.description
        instance.order = self.order
        instance.display_details = self.display_details

        for product in self.products:
            instance.products.append(
                product.duplicate(
                    from_parent=True, force_ht=force_ht, remove_cost=remove_cost
                )
            )

        if not from_parent:
            instance.price_study_id = self.price_study_id
        return instance

    def sync_with_task(self, request, task):
        return self._caerp_service.sync_with_task(request, self, task)

    def on_before_commit(self, request, action, changes=None):
        return self._caerp_service.on_before_commit(request, self, action, changes)

    def total_ht(self, request):
        """
        Total HT without discounts
        """
        return self._caerp_service.total_ht(request, self)
