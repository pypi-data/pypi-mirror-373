"""
Progress invoicing Invoicing models
------------------------------------

Models bound to an invoice that stores the data related to progressing invoice
Final Invoice are kept in sync with the model here under


Main schema 

    Invoice         <->        ProgressInvoicingPlan
                                        |
    TaskLineGroup   <->        ProgressInvoicingChapter
                                        |
    TaskLine        <->        ProgressInvoicingProduct
                               ProgressInvoicingWork
                                        |
                               ProgressInvoicingWorkItem
"""
import logging

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Numeric,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.hybrid import hybrid_property

from caerp_base.models.base import DBBASE, default_table_args
from caerp_base.models.mixins import TimeStampedMixin
from caerp.compute import math_utils
from .services.invoicing import (
    PlanService,
    ChapterService,
    ProductService,
    WorkService,
    WorkItemService,
)

logger = logging.getLogger(__name__)
TABLE_PREFIX = "progress_invoicing_"


class ProgressInvoicingPlan(DBBASE):
    """
    Associated to an invoice

    """

    __tablename__ = TABLE_PREFIX + "plan"
    __table_args__ = default_table_args

    id = Column(
        Integer,
        primary_key=True,
    )
    # Fks
    business_id = Column(ForeignKey("business.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    # Relationships
    task = relationship("Task", back_populates="progress_invoicing_plan")
    business = relationship("Business", back_populates="progress_invoicing_plans")
    chapters = relationship(
        "ProgressInvoicingChapter",
        cascade="all, delete-orphan",
        order_by="ProgressInvoicingChapter.order",
        collection_class=ordering_list("order"),
    )

    _caerp_service = PlanService

    def sync_with_task(self, task=None):
        """
        Generates the TaskLine/TaskLineGroup based on the current ProgressInvoicingPlan
        """
        return self._caerp_service.sync_with_task(self, task)

    def gen_cancelinvoice_plan(self, cancelinvoice):
        instance = self.__class__(business=self.business, task=cancelinvoice)
        for chapter in self.chapters:
            instance.chapters.append(chapter.gen_cancelinvoice_chapter(instance))
        return instance

    def has_deposit(self):
        result = False
        for chapter_status in self.business.progress_invoicing_chapter_statuses:
            for product_status in chapter_status.product_statuses:
                if product_status.has_deposit():
                    result = True
                    break
        return result

    def fill(self, request):
        """
        Fill the progress invoicing plan with the data from the task
        """
        for chapter in self.chapters:
            chapter.fill(request)

    def get_company_id(self):
        return self.task.company_id


class ProgressInvoicingChapter(DBBASE, TimeStampedMixin):
    __tablename__ = TABLE_PREFIX + "chapter"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
    )
    order = Column(Integer, default=1)
    # Fks
    status_id = Column(
        ForeignKey(TABLE_PREFIX + "chapter_status.id", ondelete="SET NULL")
    )
    plan_id = Column(ForeignKey(TABLE_PREFIX + "plan.id", ondelete="CASCADE"))
    # NB : C'est la cascade depuis l'abstract qui va supprimer l'élément
    task_line_group_id = Column(ForeignKey("task_line_group.id", ondelete="SET NULL"))
    # Relationships
    plan = relationship(ProgressInvoicingPlan, back_populates="chapters")
    status = relationship(
        "ProgressInvoicingChapterStatus", back_populates="invoiced_elements"
    )
    task_line_group = relationship(
        "TaskLineGroup", back_populates="progress_invoicing_chapter"
    )
    products = relationship(
        "ProgressInvoicingBaseProduct",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="ProgressInvoicingBaseProduct.order",
        collection_class=ordering_list("order"),
    )

    _caerp_service = ChapterService

    @property
    def task(self):
        return getattr(self.plan, "task", None)

    def sync_with_task(self, task=None):
        """
        Generates the TaskLine/TaskLineGroup based on the current ProgressInvoicingPlan
        """
        return self._caerp_service.sync_with_task(self, task)

    def gen_cancelinvoice_chapter(self, cinv_plan):
        instance = self.__class__(
            status=self.status,
        )
        for product in self.products:
            instance.products.append(product.gen_cancelinvoice_product())
        return instance

    def __json__(self, request):
        """
        Json representation of a chapter
        Collects data from related elements
        """
        result = {
            "id": self.id,
            "plan_id": self.plan_id,
            "title": "",
            "description": "",
            "products": [],
        }
        source_task_line_group = getattr(self.status, "source_task_line_group", None)
        if source_task_line_group:
            result["title"] = source_task_line_group.title
            result["description"] = source_task_line_group.description
        return result

    def fill(self, request):
        for product in self.products:
            product.fill(request)

    def get_company_id(self):
        return self.plan.get_company_id()


class ProgressInvoicingBaseProduct(DBBASE, TimeStampedMixin):
    __tablename__ = TABLE_PREFIX + "base_product"
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
    order = Column(Integer, default=1)

    already_invoiced = Column(Numeric(5, 2, asdecimal=False), nullable=True)
    percentage = Column(Numeric(5, 2, asdecimal=False), nullable=True)

    # Fks
    base_status_id = Column(
        ForeignKey(TABLE_PREFIX + "base_product_status.id", ondelete="SET NULL")
    )
    chapter_id = Column(ForeignKey(TABLE_PREFIX + "chapter.id", ondelete="CASCADE"))
    # NB : C'est la cascade depuis le chapitre qui va supprimer l'élément
    task_line_id = Column(ForeignKey("task_line.id", ondelete="SET NULL"))

    # Relationships
    status = relationship(
        "ProgressInvoicingBaseProductStatus", back_populates="invoiced_elements"
    )
    task_line = relationship("TaskLine", back_populates="progress_invoicing_product")
    chapter = relationship(ProgressInvoicingChapter, back_populates="products")

    @property
    def task(self):
        return getattr(self.chapter, "task", None)

    @property
    def plan(self):
        return getattr(self.chapter, "plan", None)

    def sync_with_task(self, task_line_group=None):
        """
        Generates the TaskLine/TaskLineGroup based on the current ProgressInvoicingPlan
        """
        return self._caerp_service.sync_with_task(self, task_line_group)

    def on_before_commit(self, request, state="update", attributes=None):
        """
        Méthode lancée avant de commiter la transaction qui modifie l'élément courant
        """
        self._caerp_service.on_before_commit(request, self, state, attributes)

    def total_ht(self) -> int:
        """
        Copute the total_ht corresponding to the current percentages
        """
        return self._caerp_service.total_ht(self)

    def gen_cancelinvoice_product(self):
        percentage = self.percentage or 0
        instance = self.__class__(
            status=self.status,
            already_invoiced=self.status.invoiced_percentage(),
            percentage=-1 * percentage,
        )
        return instance

    def get_percent_left(self):
        percentage = self.percentage or 0
        already_invoiced = self.already_invoiced or 0
        return math_utils.round(100 - percentage - already_invoiced, 2)

    def fill(self, request):
        already_invoiced = self.already_invoiced or 0
        self.percentage = 100 - already_invoiced
        request.dbsession.merge(self)

    def __json__(self, request):
        result = {"id": self.id, "chapter_id": self.chapter_id, "type_": self.type_}
        already_invoiced = self.already_invoiced or 0
        result["already_invoiced"] = math_utils.round(already_invoiced, 2)
        result["percentage"] = math_utils.round(self.percentage, 2)
        result["percent_left"] = self.get_percent_left()
        # Devrait être systématiquement True dans le cas où on est en prod
        if self.status:
            # Devrait être systématiquement True dans le cas où on est en prod
            if self.task_line:
                result["description"] = self.task_line.description
                result["tva_amount"] = math_utils.integer_to_amount(
                    self.task_line.tva_amount(), 5
                )
                result["total_ttc"] = math_utils.integer_to_amount(
                    self.task_line.total(), 5
                )
                result["total_ht"] = math_utils.integer_to_amount(
                    self.task_line.total_ht(), 5
                )

            result["has_deposit"] = self.status.has_deposit()
            result["total_ht_to_invoice"] = math_utils.integer_to_amount(
                self.status.total_ht_to_invoice(), 5
            )
            result["total_tva_to_invoice"] = math_utils.integer_to_amount(
                self.status.tva_to_invoice(), 5
            )
            result["total_ttc_to_invoice"] = math_utils.integer_to_amount(
                self.status.total_ttc_to_invoice(), 5
            )
            result["total_ht_left"] = math_utils.integer_to_amount(
                self.status.total_ht_left(), 5
            )
        return result

    def get_company_id(self):
        return self.chapter.get_company_id()


class ProgressInvoicingProduct(ProgressInvoicingBaseProduct):
    __tablename__ = TABLE_PREFIX + "product"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": __tablename__,
    }
    id = Column(
        ForeignKey(TABLE_PREFIX + "base_product.id", ondelete="CASCADE"),
        primary_key=True,
    )
    _caerp_service = ProductService


class ProgressInvoicingWork(ProgressInvoicingBaseProduct):
    __tablename__ = TABLE_PREFIX + "work"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": __tablename__,
    }
    id = Column(
        ForeignKey(TABLE_PREFIX + "base_product.id", ondelete="CASCADE"),
        primary_key=True,
    )
    locked = Column(Boolean(), default=True)
    items = relationship(
        "ProgressInvoicingWorkItem",
        back_populates="work",
        cascade="all, delete-orphan",
        order_by="ProgressInvoicingWorkItem.order",
        collection_class=ordering_list("order"),
    )
    _caerp_service = WorkService

    def gen_cancelinvoice_product(self):
        result = super().gen_cancelinvoice_product()
        result.locked = self.locked
        for item in self.items:
            result.items.append(item.gen_cancelinvoice_work_item())
        return result

    def __json__(self, request):
        result = super().__json__(request)
        result["locked"] = self.locked
        return result

    def get_percent_left(self):
        if self.locked:
            return super().get_percent_left()
        else:
            return None

    def unlock(self):
        return self._caerp_service.unlock(self)

    def fill(self, request):
        if self.locked:
            super().fill(request)
        else:
            for item in self.items:
                item.fill(request)


class ProgressInvoicingWorkItem(DBBASE, TimeStampedMixin):
    __tablename__ = TABLE_PREFIX + "work_item"
    __table_args__ = default_table_args

    id = Column(
        Integer,
        primary_key=True,
    )
    order = Column(Integer, default=1)

    _already_invoiced = Column(Numeric(5, 2, asdecimal=False), default=0)

    _percentage = Column(Numeric(5, 2, asdecimal=False), default=0)

    # Fks
    work_id = Column(ForeignKey(TABLE_PREFIX + "work.id", ondelete="CASCADE"))
    base_status_id = Column(
        ForeignKey(TABLE_PREFIX + "work_item_status.id", ondelete="SET NULL")
    )
    # Relationships
    status = relationship(
        "ProgressInvoicingWorkItemStatus", back_populates="invoiced_elements"
    )
    work = relationship("ProgressInvoicingWork")
    _caerp_service = WorkItemService

    @hybrid_property
    def already_invoiced(self):
        if self.work.locked:
            return self.work.already_invoiced
        else:
            return self._already_invoiced

    @already_invoiced.setter
    def already_invoiced(self, value):
        self._already_invoiced = value

    @hybrid_property
    def percentage(self):
        if self.work.locked:
            return self.work.percentage
        else:
            return self._percentage

    @percentage.setter
    def percentage(self, value):
        self._percentage = value

    @property
    def task(self):
        return getattr(self.work, "task", None)

    @property
    def plan(self):
        return getattr(self.work, "plan", None)

    def on_before_commit(self, request, state="update", attributes=None):
        """
        Méthode lancée avant de commiter la transaction qui modifie l'élément courant
        """
        self._caerp_service.on_before_commit(request, self, state, attributes)

    def total_ht(self) -> int:
        """
        Copute the total_ht corresponding to the current percentages
        """
        return self._caerp_service.total_ht(self)

    def total_tva(self, ht=None) -> int:
        """
        Compute the amount of Tva

        :param int ht: HT already computed (to avoid too much compute)
        """
        self._caerp_service.total_tva(self, ht)

    def total_ttc(self, ht=None) -> int:
        """
        Compute the total ttc

        :param int ht: HT already computed (to avoid too much compute)
        """
        return self._caerp_service.total_ttc(self, ht)

    def gen_cancelinvoice_work_item(self):
        percentage = self._percentage or 0
        return self.__class__(
            _already_invoiced=self.status.invoiced_percentage(),
            _percentage=-1 * percentage,
            status=self.status,
        )

    def get_percent_left(self):
        if self.work.locked:
            return self.work.get_percent_left()
        else:
            percentage = self._percentage or 0
            already_invoiced = self._already_invoiced or 0
            return math_utils.round(100 - percentage - already_invoiced, 2)

    def fill(self, request):
        already_invoiced = self._already_invoiced or 0
        self.percentage = 100 - already_invoiced
        request.dbsession.merge(self)

    def __json__(self, request):
        result = {
            "id": self.id,
            "work_id": self.work_id,
        }
        result["already_invoiced"] = self.already_invoiced
        result["percentage"] = math_utils.round(self.percentage, 2)
        result["_percentage"] = math_utils.round(self.percentage, 2)
        result["percent_left"] = self.get_percent_left()

        source_work_item = getattr(self.status, "price_study_work_item", None)
        if source_work_item is not None:
            result["description"] = source_work_item.description
            result["quantity"] = source_work_item.total_quantity
            result["unity"] = source_work_item.unity
            result["unit_ht"] = source_work_item.ht
            result["total_ht"] = math_utils.integer_to_amount(self.total_ht(), 5)

        if self.status:
            result["has_deposit"] = self.status.has_deposit()
            result["total_ht_to_invoice"] = math_utils.integer_to_amount(
                self.status.total_ht_to_invoice(), 5
            )
            result["total_tva_to_invoice"] = math_utils.integer_to_amount(
                self.status.tva_to_invoice(), 5
            )
            result["total_ttc_to_invoice"] = math_utils.integer_to_amount(
                self.status.total_ttc_to_invoice(), 5
            )
            result["total_ht_left"] = math_utils.integer_to_amount(
                self.status.total_ht_left(), 5
            )
        return result

    def get_company_id(self):
        return self.work.get_company_id()
