import logging

from caerp_base.models.base import DBBASE, default_table_args
from caerp_base.models.mixins import TimeStampedMixin
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, Numeric
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from caerp.compute.math_utils import integer_to_amount

from .services import PriceStudyService

logger = logging.getLogger()


class PriceStudy(TimeStampedMixin, DBBASE):
    __tablename__ = "price_study"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    ht = Column(BigInteger(), default=0)
    general_overhead = Column(Numeric(6, 5, asdecimal=False))
    mask_hours = Column(Boolean(), default=True)
    force_ht = Column(Boolean(), default=False)
    # Fks
    task_id = Column(ForeignKey("task.id", ondelete="cascade"))
    # relationships
    task = relationship(
        "Task", primaryjoin="PriceStudy.task_id==Task.id", back_populates="price_study"
    )
    # Back_populate relationships
    chapters = relationship(
        "PriceStudyChapter",
        back_populates="price_study",
        order_by="PriceStudyChapter.order",
        collection_class=ordering_list("order"),
        passive_deletes=True,
    )
    discounts = relationship(
        "PriceStudyDiscount",
        back_populates="price_study",
        order_by="PriceStudyDiscount.order",
        collection_class=ordering_list("order"),
        passive_deletes=True,
    )
    task = relationship(
        "Task",
        back_populates="price_study",
        primaryjoin="Task.id==PriceStudy.task_id",
    )
    # View only Relationships
    products = relationship(
        "BasePriceStudyProduct",
        secondary="price_study_chapter",
        primaryjoin="PriceStudy.id==PriceStudyChapter.price_study_id",
        secondaryjoin="PriceStudyChapter.id==BasePriceStudyProduct.chapter_id",
        viewonly=True,
        back_populates="price_study",
    )

    _caerp_service = PriceStudyService

    def get_task(self):
        # Uniforme avec les méthodes des autres objets des études de prix
        return self.task

    def get_company_id(self):
        return self._caerp_service.get_company_id(self)

    def get_company(self):
        return self._caerp_service.get_company(self)

    def __json__(self, request):
        return dict(
            id=self.id,
            general_overhead=self.general_overhead,
            mask_hours=self.mask_hours,
            ht=integer_to_amount(self.ht, 5),
            tva_parts=dict(
                (tva.id, integer_to_amount(item["tva"], 5))
                for tva, item in self.amounts_by_tva().items()
            ),  # {2000: 1250,25484} ...
            total_ht=integer_to_amount(self.total_ht(), 5),
            total_ttc=integer_to_amount(self.total_ttc(), 5),
            total_ht_before_discount=integer_to_amount(
                self.total_ht_before_discount(), 5
            ),
        )

    def is_editable(self):
        """
        Check if this price study can be edited
        :returns: True/False
        """
        return self._caerp_service.is_editable(self)

    def is_admin_editable(self):
        """
        Check if this price study can be edited by an admin
        :returns: True/False
        """
        return self._caerp_service.is_admin_editable(self)

    def amounts_by_tva(self):
        return self._caerp_service.amounts_by_tva(self)

    def discounts_by_tva(self):
        return self._caerp_service.discounts_by_tva(self)

    # HT
    def total_ht_before_discount(self):
        return self._caerp_service.total_ht_before_discount(self)

    def discount_ht(self):
        return self._caerp_service.discount_ht(self)

    def total_ht(self):
        return self._caerp_service.total_ht(self)

    # TVA
    def total_tva_before_discount(self):
        return self._caerp_service.total_tva_before_discount(self)

    def discount_tva(self):
        return self._caerp_service.discount_tva(self)

    def total_tva(self):
        return self._caerp_service.tva_amounts(self)

    # TTC
    def total_ttc(self):
        return self._caerp_service.total_ttc(self)

    def duplicate(self, force_ht=False, exclude_discounts=False, remove_cost=False):
        if not force_ht:
            company = self.get_company()
            if company and company.general_overhead:
                general_overhead = company.general_overhead
            else:
                general_overhead = self.general_overhead
        else:
            general_overhead = 0
        instance = self.__class__(
            general_overhead=general_overhead,
            mask_hours=self.mask_hours,
            force_ht=force_ht,
        )

        for chapter in self.chapters:
            instance.chapters.append(
                chapter.duplicate(
                    from_parent=True, force_ht=force_ht, remove_cost=remove_cost
                )
            )
        if not exclude_discounts:
            for discount in self.discounts:
                instance.discounts.append(discount.duplicate(from_parent=True))

        self.sync_amounts(sync_down=True)
        return instance

    def sync_amounts(self, sync_down=False):
        """
        Set cached amounts on the current PriceStudy

        :param bool sync_down: Should we sync_amounts all the products down in
         the hierarchy ?
        """
        return self._caerp_service.sync_amounts(self, sync_down=sync_down)

    def sync_with_task(self, request):
        """
        Synchronize the associated task with the price_study configuration
        (create TaskLineGroup, DiscountLine, TaskLine instances ...)
        """
        return self._caerp_service.sync_with_task(request, self)

    def on_before_commit(self, request, action, changes=None):
        self._caerp_service.on_before_commit(request, self, action, changes)

    def json_totals(self, request):
        return self._caerp_service.json_totals(request, self)
