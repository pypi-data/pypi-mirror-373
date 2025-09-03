"""
Progress Invoicing Status models

In a business this models are used 

- To store the percentages that should be invoiced
- To link invoicing elements with the original estimation's (or price_study in case 
    of WorkItems) elements


    PriceStudy        <->      Estimation    <->      Business

    PriceStudyChapter <->     TaskLineGroup  <->      ProgressInvoicingChapterStatus

    PriceStudyProduct <->       TaskLine     <->      ProgressInvoicingProductStatus
    PriceStudyWork                                    ProgressInvoicingWorkStatus

    PriceStudyWorkItem        <---------->            ProgressInvoicingWorkItem
"""

import logging
from caerp_base.models.base import DBBASE, default_table_args
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Numeric,
    Boolean,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .services.status import (
    ProductStatusService,
    ChapterStatusService,
    WorkItemStatusService,
    WorkStatusService,
)

logger = logging.getLogger(__name__)


TABLE_PREFIX = "progress_invoicing_"


class ProgressInvoicingChapterStatus(DBBASE):
    """
    Invoicing Status corresponding to a TaskLineGroup / Chapter

    Linked to a business

    Used to keep a reference to the original Estimation(s) Structure
    """

    __tablename__ = TABLE_PREFIX + "chapter_status"
    __table_args__ = default_table_args

    id = Column(
        Integer,
        primary_key=True,
    )
    business_id = Column(ForeignKey("business.id", ondelete="CASCADE"))

    # TaskLineGroup Data
    source_task_line_group_id = Column(
        ForeignKey("task_line_group.id", ondelete="CASCADE")
    )

    # Relationships
    business = relationship(
        "Business", back_populates="progress_invoicing_chapter_statuses"
    )
    source_task_line_group = relationship("TaskLineGroup")
    product_statuses = relationship(
        "ProgressInvoicingBaseProductStatus",
        back_populates="chapter_status",
        cascade="all, delete-orphan",
    )
    invoiced_elements = relationship(
        "ProgressInvoicingChapter", order_by="ProgressInvoicingChapter.created_at"
    )

    _caerp_service = ChapterStatusService

    @classmethod
    def get_or_create(cls, business, task_line_group):
        """
        Retrieve or create a new status entry for the given source item

        :param obj business: The current Business we're working in
        :param obj task_line_group: The original Estimation's TaskLineGroup we refer to
        """
        return cls._caerp_service.get_or_create(cls, business, task_line_group)

    def sync_with_plan(self, progress_invoicing_plan):
        """
        Sync the current chapter status with the given plan

        Generates the ProgressInvoicingChapter associated to it and all of its products
        """
        return self._caerp_service.sync_with_plan(self, progress_invoicing_plan)

    def is_completely_invoiced(self):
        return self._caerp_service.is_completely_invoiced(self)


class ProgressInvoicingBaseProductStatus(DBBASE):
    """
    Base Progress Invoicing Status used to remember which percentage of which
    element has been invoiced yet

    Linked to a Chapter status

    Uses two reference percentage

    percent_left

        starts at 100% and correspond to the progress invoicing (discussed with
        the customer)

    percent_to_invoice

        100% - account_percent and correspond to the percentage to be
        considered in the progress invoicing
    """

    __tablename__ = TABLE_PREFIX + "base_product_status"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": __tablename__,
    }
    id = Column(
        Integer,
        primary_key=True,
    )
    type_ = Column("type_", String(40), nullable=False)
    # mémorise le pourcentage à facturer après accompte
    percent_to_invoice = Column(Numeric(5, 2, asdecimal=False), default=100)
    # Démarre à 100% et révèle la réalité du terrain (utilisé pour l'UI et
    # transposé sur le real_percent pour les calculs)
    # Réduit avec l'avancement
    percent_left = Column(Numeric(5, 2, asdecimal=False), default=100)

    # Fks
    chapter_status_id = Column(
        ForeignKey(TABLE_PREFIX + "chapter_status.id", ondelete="CASCADE")
    )
    # Lien vers la TaskLine associée
    source_task_line_id = Column(ForeignKey("task_line.id", ondelete="CASCADE"))

    # Relationships
    chapter_status = relationship(
        ProgressInvoicingChapterStatus, back_populates="product_statuses"
    )
    source_task_line = relationship("TaskLine")
    invoiced_elements = relationship(
        "ProgressInvoicingBaseProduct",
        back_populates="status",
        cascade="all, delete",
        order_by="ProgressInvoicingBaseProduct.created_at",
    )

    @classmethod
    def get_or_create(cls, source_task_line, chapter_status, percent_to_invoice):
        """
        Retrieve or create a new status entry for the given source item
        """
        return cls._caerp_service.get_or_create(
            cls, source_task_line, chapter_status, percent_to_invoice
        )

    def total_deposit(self):
        return self._caerp_service.total_deposit(self)

    def total_ht_to_invoice(self):
        """
        Compute the total ht to invoice without deposit amount

        :returns: The HT amount in 10^5 format
        :rtype: int
        """
        return self._caerp_service.total_ht_to_invoice(self)

    def tva_to_invoice(self):
        """
        Compute the tva to invoice without deposit amount

        :returns: The tva amount in 10^5 format
        :rtype: int
        """
        return self._caerp_service.tva_to_invoice(self)

    def total_ttc_to_invoice(self):
        """
        Compute the total ttc to invoice without deposit amount

        :returns: The ttc amount in 10^5 format
        :rtype: int
        """
        return self._caerp_service.total_ttc_to_invoice(self)

    def invoiced_percentage(self, product=None):
        """
        Compute the percentage that was already invoiced
        Before product if provided

        :param obj product: ProgressInvoicingProduct
        """
        return self._caerp_service.invoiced_percentage(self, product)

    def invoiced_ht(self, product=None):
        """
        Compute the total ht that was already invoiced
        Before product if provided

        :param obj product: ProgressInvoicingProduct
        """
        return self._caerp_service.invoiced_ht(self, product)

    def get_percent_left(self):
        """
        Compute the percent left regarding the current status (also when an
        invoice is currently edited)

        :rtype: float or None
        """
        return self._caerp_service.get_percent_left(self)

    def total_ht_left(self):
        """
        Compute the total ht regarding the current status (also when an invoice
        is currently edited)

        :rtype: int
        """
        return self._caerp_service.total_ht_left(self)

    def get_cost(self, ui_percentage, product, percent_left):
        """
        Compute the cost corresponding to ui_percentage for the given product

        :param float ui_percentage: The Percentage to compute
        :param obj product: The ProgressInvoicingProduct asking for its cost
        :param float percent_left: The percentage left before this product is invoiced
        """
        return self._caerp_service.get_cost(self, ui_percentage, product, percent_left)

    def is_completely_invoiced(self):
        return self._caerp_service.is_completely_invoiced(self)

    def has_deposit(self):
        """
        Return True if a deposit has been deduced from the original HT amount
        """
        return self.percent_to_invoice != 100

    def sync_with_plan(self, progress_invoicing_chapter):
        """
        Sync the current product status with the given plan

        Generates the ProgressInvoicingProduct
        """
        return self._caerp_service.sync_with_plan(self, progress_invoicing_chapter)


class ProgressInvoicingProductStatus(ProgressInvoicingBaseProductStatus):
    """
    Status attached to a single product TaskLine (not one associated to a
    PriceStudyWorkItem)
    """

    __tablename__ = TABLE_PREFIX + "product_status"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": __tablename__,
    }
    _caerp_service = ProductStatusService

    id = Column(
        ForeignKey(TABLE_PREFIX + "base_product_status", ondelete="CASCADE"),
        primary_key=True,
    )


class ProgressInvoicingWorkStatus(ProgressInvoicingBaseProductStatus):
    __tablename__ = TABLE_PREFIX + "work_status"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": __tablename__,
    }
    id = Column(
        ForeignKey(TABLE_PREFIX + "base_product_status", ondelete="CASCADE"),
        primary_key=True,
    )
    # Les pourcentages sont-ils déterminés au niveau de cet élément ?
    locked = Column(Boolean(), default=True)
    # relationship
    item_statuses = relationship("ProgressInvoicingWorkItemStatus")

    _caerp_service = WorkStatusService


class ProgressInvoicingWorkItemStatus(DBBASE):
    __tablename__ = TABLE_PREFIX + "work_item_status"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    # mémorise le pourcentage à facturer après accompte
    percent_to_invoice = Column(Numeric(5, 2, asdecimal=False), default=100)
    # Démarre à 100% et révèle la réalité du terrain (utilisé pour l'UI et
    # transposé sur le real_percent pour les calculs)
    # Réduit avec l'avancement
    _percent_left = Column(Numeric(5, 2, asdecimal=False), default=100)

    # Fks
    work_status_id = Column(
        ForeignKey(TABLE_PREFIX + "work_status.id", ondelete="CASCADE")
    )
    price_study_work_item_id = Column(
        ForeignKey("price_study_work_item.id", ondelete="CASCADE")
    )
    # Relationships
    work_status = relationship(
        ProgressInvoicingWorkStatus, back_populates="item_statuses"
    )
    price_study_work_item = relationship("PriceStudyWorkItem")
    invoiced_elements = relationship(
        "ProgressInvoicingWorkItem",
        back_populates="status",
        cascade="all, delete",
        order_by="ProgressInvoicingWorkItem.created_at",
    )

    _caerp_service = WorkItemStatusService

    @hybrid_property
    def percent_left(self):
        if self.work_status.locked:
            return self.work_status.percent_left
        else:
            return self._percent_left

    @percent_left.setter
    def percent_left(self, value):
        self._percent_left = value

    @classmethod
    def get_or_create(cls, price_study_work_item, work_status, percent_to_invoice):
        """
        Get or create a new instance associated to a price_study_work_item and
        a work_status
        """
        return cls._caerp_service.get_or_create(
            cls, price_study_work_item, work_status, percent_to_invoice
        )

    def total_deposit(self):
        return self._caerp_service.total_deposit(self)

    def total_ht_to_invoice(self):
        """
        Compute the total ht to invoice without deposit amount

        :returns: The HT amount in 10^5 format
        :rtype: int
        """
        return self._caerp_service.total_ht_to_invoice(self)

    def tva_to_invoice(self):
        """
        Compute the tva to invoice without deposit amount

        :returns: The tva amount in 10^5 format
        :rtype: int
        """
        return self._caerp_service.tva_to_invoice(self)

    def total_ttc_to_invoice(self):
        """
        Compute the total ttc to invoice without deposit amount

        :returns: The ttc amount in 10^5 format
        :rtype: int
        """
        return self._caerp_service.total_ttc_to_invoice(self)

    def invoiced_percentage(self, work_item=None):
        """
        Compute the percentage that was already invoiced
        Before work_item if provided

        :param obj work_item: ProgressInvoicingWorkITem
        """
        return self._caerp_service.invoiced_percentage(self, work_item)

    def invoiced_ht(self, work_item=None):
        """
        Compute the total ht that was already invoiced
        Before work_item if provided

        :param obj work_item: ProgressInvoicingWorkITem
        """
        return self._caerp_service.invoiced_ht(self, work_item)

    def get_percent_left(self):
        """
        Compute the percent left regarding the current status (also when an
        invoice is currently edited)

        :rtype: float or None
        """
        return self._caerp_service.get_percent_left(self)

    def total_ht_left(self):
        """
        Compute the total ht regarding the current status (also when an invoice
        is currently edited)

        :rtype: int
        """
        return self._caerp_service.total_ht_left(self)

    def get_cost(self, ui_percentage, work_item, percent_left):
        """
        Compute the cost corresponding to ui_percentage for the given work_item

        :param float ui_percentage: The Percentage to compute
        :param obj work_item: The ProgressInvoicingWorkITem asking for its cost
        :param float percent_left: The percentage left before this work_item is invoiced
        """
        return self._caerp_service.get_cost(
            self, ui_percentage, work_item, percent_left
        )

    def is_completely_invoiced(self):
        return self._caerp_service.is_completely_invoiced(self)

    def has_deposit(self):
        """
        Return True if a deposit has been deduced from the original HT amount
        """
        return self.percent_to_invoice != 100

    def sync_with_plan(self, progress_invoicing_work):
        """
        Sync the current work_item status with the given plan

        Generates the ProgressInvoicingWorkITem
        """
        return self._caerp_service.sync_with_plan(self, progress_invoicing_work)
