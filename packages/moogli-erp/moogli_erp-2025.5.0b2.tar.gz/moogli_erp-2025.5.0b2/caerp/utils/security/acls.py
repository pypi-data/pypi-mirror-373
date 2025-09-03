"""
    Root factory <=> Acl handling
"""

import datetime
import logging
from typing import Iterable, List, Tuple

from caerp_base.models.base import DBSESSION
from caerp_celery.models import Job
from pyramid.authorization import ALL_PERMISSIONS, Allow, Authenticated, Deny, Everyone
from pyramid.threadlocal import get_current_request
from sqlalchemy import select
from sqlalchemy.orm import undefer_group

from caerp.compute import math_utils
from caerp.consts.access_rights import ACCESS_RIGHTS
from caerp.consts.permissions import PERMISSIONS
from caerp.models.accounting.accounting_closures import AccountingClosure
from caerp.models.accounting.balance_sheet_measures import (
    ActiveBalanceSheetMeasureType,
    BalanceSheetMeasureGrid,
    PassiveBalanceSheetMeasureType,
)
from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule
from caerp.models.accounting.general_ledger_account_wordings import (
    GeneralLedgerAccountWording,
)
from caerp.models.accounting.income_statement_measures import (
    IncomeStatementMeasureGrid,
    IncomeStatementMeasureType,
    IncomeStatementMeasureTypeCategory,
)
from caerp.models.accounting.operations import AccountingOperationUpload
from caerp.models.accounting.treasury_measures import (
    TreasuryMeasureGrid,
    TreasuryMeasureType,
    TreasuryMeasureTypeCategory,
)
from caerp.models.activity import Activity
from caerp.models.career_path import CareerPath
from caerp.models.career_stage import CareerStage
from caerp.models.company import Company
from caerp.models.competence import (
    CompetenceGrid,
    CompetenceGridItem,
    CompetenceGridSubItem,
)
from caerp.models.config import ConfigFiles
from caerp.models.custom_documentation import CustomDocumentation
from caerp.models.expense.payment import ExpensePayment
from caerp.models.expense.sheet import BaseExpenseLine, ExpenseSheet
from caerp.models.expense.types import ExpenseType
from caerp.models.export.accounting_export_log import AccountingExportLogEntry
from caerp.models.files import File, Template, TemplatingHistory
from caerp.models.form_options import FormFieldDefinition
from caerp.models.indicators import (
    CustomBusinessIndicator,
    Indicator,
    SaleFileRequirement,
)
from caerp.models.node import Node
from caerp.models.notification import Notification
from caerp.models.options import ConfigurableOption
from caerp.models.price_study import (
    BasePriceStudyProduct,
    PriceStudy,
    PriceStudyChapter,
    PriceStudyDiscount,
    PriceStudyWorkItem,
)
from caerp.models.progress_invoicing import (
    ProgressInvoicingBaseProduct,
    ProgressInvoicingChapter,
    ProgressInvoicingPlan,
    ProgressInvoicingWorkItem,
)
from caerp.models.project import Phase, Project
from caerp.models.project.business import Business, BusinessPaymentDeadline
from caerp.models.project.types import BusinessType, ProjectType
from caerp.models.sale_product.base import BaseSaleProduct, SaleProductStockOperation
from caerp.models.sale_product.category import SaleProductCategory
from caerp.models.sale_product.work_item import WorkItem
from caerp.models.sepa import BaseSepaWaitingPayment, SepaCreditTransfer
from caerp.models.smtp import SmtpSettings
from caerp.models.statistics import StatisticCriterion, StatisticEntry, StatisticSheet
from caerp.models.status import StatusLogEntry
from caerp.models.supply import (
    BaseSupplierInvoicePayment,
    InternalSupplierInvoice,
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierInvoiceSupplierPayment,
    SupplierInvoiceUserPayment,
    SupplierOrder,
    SupplierOrderLine,
)
from caerp.models.task import (
    BankRemittance,
    BaseTaskPayment,
    CancelInvoice,
    Estimation,
    InternalCancelInvoice,
    InternalEstimation,
    InternalInvoice,
    InternalPayment,
    Invoice,
    Payment,
)
from caerp.models.task.estimation import PaymentLine
from caerp.models.task.insurance import TaskInsuranceOption
from caerp.models.task.mentions import TaskMention
from caerp.models.task.task import (
    DiscountLine,
    PostTTCLine,
    Task,
    TaskLine,
    TaskLineGroup,
)
from caerp.models.third_party.customer import Customer
from caerp.models.third_party.supplier import Supplier
from caerp.models.training.trainer import TrainerDatas
from caerp.models.tva import Tva
from caerp.models.user import Group, User, UserDatas
from caerp.models.workshop import Timeslot, Workshop
from caerp.plugins.sap.models.sap import SAPAttestation
from caerp.services.company import find_company_id_from_model
from caerp.services.third_party.supplier import is_supplier_deletable

FILE_PARENT_VIEW_PERMS = (
    PERMISSIONS["context.list_files"],
    PERMISSIONS["context.view_file"],
)
FILE_PARENT_EDIT_PERMS = (
    PERMISSIONS["context.add_file"],
    PERMISSIONS["context.edit_file"],
    PERMISSIONS["context.delete_file"],
)


def get_access_right(name: str) -> str:
    """
    return the access right principal used in acl
    Also ensures name exists in ACCESS_RIGHTS
    """
    name = ACCESS_RIGHTS[name]["name"]
    return f"access_right:{name}"


class RootFactory(dict):
    """
    Ressource factory, returns the appropriate resource regarding
    the request object
    """

    __name__ = "root"
    # item structure :
    # traversal_name, object_name, factory
    leaves = (
        (
            "activities",
            "activity",
            Activity,
        ),
        (
            "accounting_operation_uploads",
            "accounting_operation_upload",
            AccountingOperationUpload,
        ),
        (
            "companies",
            "company",
            Company,
        ),
        (
            "competences",
            "competence",
            CompetenceGrid,
        ),
        (
            "competence_items",
            "competence_item",
            CompetenceGridItem,
        ),
        (
            "competence_subitems",
            "competence_subitem",
            CompetenceGridSubItem,
        ),
        (
            "configurable_options",
            "configurable_options",
            ConfigurableOption,
        ),
        (
            "customers",
            "customer",
            Customer,
        ),
        (
            "suppliers",
            "supplier",
            Supplier,
        ),
        (
            "discount_lines",
            "discount_line",
            DiscountLine,
        ),
        (
            "post_ttc_lines",
            "post_ttc_line",
            PostTTCLine,
        ),
        (
            "expenses",
            "expense",
            ExpenseSheet,
        ),
        (
            "expenselines",
            "expenseline",
            BaseExpenseLine,
        ),
        (
            "expense_types",
            "expense_type",
            ExpenseType,
        ),
        (
            "expense_payments",
            "expense_payment",
            ExpensePayment,
        ),
        (
            "form_field_definitions",
            "form_field_definition",
            FormFieldDefinition,
        ),
        ("supplier_invoices", "supplier_invoice", SupplierInvoice),
        (
            "supplier_invoicelines",
            "supplier_invoiceline",
            SupplierInvoiceLine,
        ),
        ("supplier_payments", "supplier_payment", BaseSupplierInvoicePayment),
        ("supplier_orders", "supplier_order", SupplierOrder),
        ("supplier_orderlines", "supplier_orderline", SupplierOrderLine),
        (
            "files",
            "file",
            File,
        ),
        ("groups", "group", Group),
        ("nodes", "node", Node),
        (
            "statuslogentries",
            "statuslogentry",
            StatusLogEntry,
        ),
        (
            "tasks",
            "task",
            Task,
        ),
        (
            "income_statement_measure_grids",
            "income_statement_measure_grid",
            IncomeStatementMeasureGrid,
        ),
        (
            "income_statement_measure_types",
            "income_statement_measure_type",
            IncomeStatementMeasureType,
        ),
        (
            "income_statement_measure_type_categories",
            "income_statement_measure_type_category",
            IncomeStatementMeasureTypeCategory,
        ),
        (
            "closure_list",
            "closures_list",
            AccountingClosure,
        ),
        (
            "general_ledger_account_wordings_list",
            "general_ledger_account_wording_list",
            GeneralLedgerAccountWording,
        ),
        (
            "custom_invoice_book_entry_modules",
            "custom_invoice_book_entry_module",
            CustomInvoiceBookEntryModule,
        ),
        (
            "indicators",
            "indicator",
            Indicator,
        ),
        (
            "jobs",
            "job",
            Job,
        ),
        (
            "base_task_payments",
            "base_task_payment",
            BaseTaskPayment,
        ),
        (
            "payments",
            "payment",
            Payment,
        ),
        (
            "payment_lines",
            "payment_line",
            PaymentLine,
        ),
        (
            "phases",
            "phase",
            Phase,
        ),
        (
            "projects",
            "project",
            Project,
        ),
        ("project_types", "project_type", ProjectType),
        # Catalogue produit
        (
            "base_sale_products",
            "base_sale_product",
            BaseSaleProduct,
        ),
        (
            "sale_categories",
            "sale_category",
            SaleProductCategory,
        ),
        (
            "work_items",
            "work_item",
            WorkItem,
        ),
        (
            "stock_operations",
            "stock_operation",
            SaleProductStockOperation,
        ),
        # étude de prix
        ("price_studies", "price_study", PriceStudy),
        (
            "price_study_chapters",
            "price_study_chapter",
            PriceStudyChapter,
        ),
        (
            "base_price_study_products",
            "base_price_study_product",
            BasePriceStudyProduct,
        ),
        (
            "price_study_discounts",
            "price_study_discount",
            PriceStudyDiscount,
        ),
        (
            "price_study_work_items",
            "price_study_work_item",
            PriceStudyWorkItem,
        ),
        # Avancement
        ("progress_invoicing_plans", "progress_invoicing_plan", ProgressInvoicingPlan),
        (
            "progress_invoicing_chapters",
            "progress_invoicing_chapter",
            ProgressInvoicingChapter,
        ),
        (
            "progress_invoicing_base_products",
            "progress_invoicing_base_product",
            ProgressInvoicingBaseProduct,
        ),
        (
            "progress_invoicing_work_items",
            "progress_invoicing_work_item",
            ProgressInvoicingWorkItem,
        ),
        (
            "sepa_credit_transfers",
            "sepa_credit_transfer",
            SepaCreditTransfer,
        ),
        ("sepa_waiting_payments", "sepa_waiting_payment", BaseSepaWaitingPayment),
        # Statistiques
        (
            "statistics",
            "statistic",
            StatisticSheet,
        ),
        (
            "statistic_entries",
            "statistic_entry",
            StatisticEntry,
        ),
        (
            "statistic_criteria",
            "statistic_criterion",
            StatisticCriterion,
        ),
        # Notifications
        ("notifications", "notification", Notification),
        ("businesses", "business", Business),
        (
            "business_payment_deadlines",
            "business_payment_deadline",
            BusinessPaymentDeadline,
        ),
        ("business_types", "business_type", BusinessType),
        ("tasks", "task", Task),
        ("task_lines", "task_line", TaskLine),
        ("task_line_groups", "task_line_group", TaskLineGroup),
        ("task_mentions", "task_mention", TaskMention),
        ("task_insurance_options", "task_insurance_option", TaskInsuranceOption),
        (
            "templates",
            "template",
            Template,
        ),
        (
            "templatinghistory",
            "templatinghistory",
            TemplatingHistory,
        ),
        (
            "balance_sheet_measure_grids",
            "balance_sheet__measure_grid",
            BalanceSheetMeasureGrid,
        ),
        (
            "active_balance_sheet_measure_types",
            "active_balance_sheet_measure_type",
            ActiveBalanceSheetMeasureType,
        ),
        (
            "passive_balance_sheet_measure_types",
            "passive_balance_sheet_measure_type",
            PassiveBalanceSheetMeasureType,
        ),
        (
            "treasury_measure_grids",
            "treasury_measure_grid",
            TreasuryMeasureGrid,
        ),
        (
            "treasury_measure_types",
            "treasury_measure_type",
            TreasuryMeasureType,
        ),
        (
            "treasury_measure_type_categories",
            "treasury_measure_type_category",
            TreasuryMeasureTypeCategory,
        ),
        (
            "timeslots",
            "timeslot",
            Timeslot,
        ),
        (
            "tvas",
            "tva",
            Tva,
        ),
        (
            "users",
            "user",
            User,
        ),
        (
            "workshops",
            "workshop",
            Workshop,
        ),
        (
            "career_stages",
            "career_stage",
            CareerStage,
        ),
        (
            "career_path",
            "career_path",
            CareerPath,
        ),
        (
            "bank_remittances",
            "bank_remittance",
            BankRemittance,
        ),
        (
            "custom_documentations",
            "custom_documentation",
            CustomDocumentation,
        ),
        ("smtp_settings", "smtp_setting", SmtpSettings),
    )
    subtrees = ()

    def __acl__(self):
        """
        Default permissions
        """
        return [(Allow, Authenticated, PERMISSIONS["global.authenticated"])]

    def __init__(self, request):
        self.request = request

        logger = logging.getLogger(__name__)

        for traversal_name, object_name, factory in self.leaves:
            self[traversal_name] = TraversalDbAccess(
                self,
                traversal_name,
                object_name,
                factory,
                logger,
                request,
            )

        for traversal_name, subtree in self.subtrees:
            self[traversal_name] = subtree

        self["configfiles"] = TraversalDbAccess(
            self,
            "configfiles",
            "config_file",
            ConfigFiles,
            logger,
            request,
            id_key="key",
            public=True,
        )

    @classmethod
    def register_subtree(cls, traversal_name, subtree):
        cls.subtrees = cls.subtrees + ((traversal_name, subtree),)


class TraversalNode(dict):
    """
    Class representing a simple traversal node
    """

    def __acl__(self):
        """
        Default permissions
        """
        acl = []
        return acl


class TraversalDbAccess:
    """
    Class handling access to dbrelated objects
    """

    __acl__ = []
    dbsession = None

    def __init__(
        self,
        parent,
        traversal_name,
        object_name,
        factory,
        logger,
        request,
        id_key="id",
        public=False,
    ):
        self.__parent__ = parent
        self.factory = factory
        self.object_name = object_name
        self.__name__ = traversal_name
        self.id_key = id_key
        self.logger = logger
        self.public = public
        self.request = request

    def __getitem__(self, key):
        if not self.request.identity and not self.public:
            from pyramid.httpexceptions import HTTPForbidden

            self.logger.info("HTTP Forbidden view the user is not connected")
            raise HTTPForbidden()
        self.logger.debug("Retrieving the context of type : {}".format(self.__name__))
        self.logger.debug("With ID : {}".format(key))
        return self._get_item(self.factory, key, self.object_name)

    def _get_item(self, klass, key, object_name):
        dbsession = self.request.dbsession
        obj = dbsession.execute(
            select(klass)
            .options(undefer_group("edit"))
            .filter(getattr(klass, self.id_key) == key)
        ).scalar()

        if obj is None:
            self.logger.debug("No object found")
            raise KeyError

        self.logger.debug(obj)
        obj.__name__ = object_name
        # NB : Log Important qui force le chargement de la "vraie" classe de
        # l'objet pour le cas du polymorphisme, si l'objet est un Invoice, et
        # que le traversal récupère un Task, il sera automatiquement casté
        # comme une Invoice par le log ci-dessous
        return obj


def get_current_login():
    """
    Return the Login instance of the current authenticated user
    """
    request = get_current_request()
    user = request.identity
    result = None
    if user is not None:
        result = user.login
    return result


def get_base_acl(self):
    """
    return the base acl
    """
    return [
        (
            Allow,
            Authenticated,
            "global.authenticated",
        )
    ]


def _get_admin_user_base_acl(self):
    """
    Build acl for user account management for admins

    :returns: A list of user acls
    """
    # User : view/add/delete/edit
    # Login : view/add/delete/edit
    # TrainerDatas : view/add/delete/edit
    # UserDatas : view/add/delete/edit

    # Holidays

    user_perms = (
        PERMISSIONS["context.view_user"],
        PERMISSIONS["context.edit_user"],
        PERMISSIONS["context.delete_user"],
    )
    login_perms = (
        PERMISSIONS["context.view_login"],
        PERMISSIONS["context.add_login"],
        PERMISSIONS["context.edit_login"],
        PERMISSIONS["context.delete_login"],
    )
    trainerdatas_perms = (
        PERMISSIONS["context.view_trainerdata"],
        PERMISSIONS["context.edit_trainerdata"],
        PERMISSIONS["context.disable_trainerdata"],
        PERMISSIONS["context.delete_trainerdata"],
    ) + FILE_PARENT_EDIT_PERMS
    userdatas_perms = (
        PERMISSIONS["context.view_userdata"],
        PERMISSIONS["context.edit_userdata"],
        PERMISSIONS["context.delete_userdata"],
    )
    acl = [
        (Allow, get_access_right("global_create_user"), user_perms + login_perms),
        (Allow, get_access_right("global_supervisor_training"), trainerdatas_perms),
    ]
    for rights in ("global_userdata_details", "global_userdata_restricted"):
        acl.append((Allow, f"access_right:{rights}", userdatas_perms))

    acl.append(
        (
            Allow,
            get_access_right("global_userdata_details"),
            FILE_PARENT_VIEW_PERMS + FILE_PARENT_EDIT_PERMS,
        )
    )
    return acl


def _get_user_base_acl(self):
    """
    Build acl for user account management for the owner

    :returns: The list of user acls
    """
    result = []
    if self.login and self.login.active:
        perms = (
            PERMISSIONS["context.view_user"],
            PERMISSIONS["context.edit_user"],
            PERMISSIONS["context.edit_login"],
            PERMISSIONS["context.view_file"],
            PERMISSIONS["context.add_holiday"],
            PERMISSIONS["context.edit_holiday"],
            PERMISSIONS["context.list_holidays"],
            PERMISSIONS["context.edit_competence"],
            PERMISSIONS["context.list_competences"],
            PERMISSIONS["context.view_userdata_files"],
        )

        # FIXME On doit plutôt vérifier que le user en cours a la permission 'es_trainer'
        if "trainer" in self.login.groups:
            perms += (
                PERMISSIONS["context.view_trainerdata"],
                PERMISSIONS["context.edit_trainerdata"],
            ) + FILE_PARENT_EDIT_PERMS
        result = [(Allow, self.login.login, perms)]
    return result


def get_user_acl(self):
    """
    Collect acl for a user context
    :returns: A list of user aces (in the format expected by Pyramid)
    """
    if self.id <= 0:
        return (Deny, Everyone, ALL_PERMISSIONS)

    acl = []

    acl.extend(_get_admin_user_base_acl(self))
    acl.extend(_get_user_base_acl(self))
    return acl


def get_career_path_acl(self):
    """
    Collect acl for a CareerPath context
    :returns: A list of user aces (in the format expected by Pyramid)
    """
    acl = get_user_acl(self.userdatas.user)
    return acl


def get_userdatas_acl(self):
    acl = get_user_acl(self.user)
    return acl


def get_event_acl(self, type_: str) -> List[Tuple[str, str, Iterable[str]]]:
    """
    Compute acl for the Event base class
    """
    return [
        (
            Allow,
            user.login.login,
            (
                PERMISSIONS[f"context.view_{type_}"],
                PERMISSIONS["context.view_file"],
            ),
        )
        for user in self.participants
    ]


def get_activity_acl(self):
    """
    Return acl for activities : companies can also view
    """
    acl = get_event_acl(self, "activity")
    admin_perms = (
        PERMISSIONS["context.view_activity"],
        PERMISSIONS["context.edit_activity"],
        PERMISSIONS["context.view_file"],
        PERMISSIONS["context.edit_file"],
        PERMISSIONS["context.delete_file"],
    )

    acl.append((Allow, get_access_right("global_accompagnement"), admin_perms))

    for company in self.companies:
        acl.append(
            (
                Allow,
                "company:{}".format(company.id),
                (
                    PERMISSIONS["context.view_activity"],
                    PERMISSIONS["context.view_file"],
                ),
            )
        )
    return acl


def get_workshop_acl(self):
    """
    Return ACL for workshops
    """
    acl = get_event_acl(self, "workshop")
    # Prior to default ACL because we want to forbid self-signin on closed
    # workshops even for admins.
    if self.signup_mode == "open":
        acl.append(
            (
                Allow,
                Authenticated,
                (
                    PERMISSIONS["context.signup_workshop"],
                    PERMISSIONS["context.signout_workshop"],
                    PERMISSIONS["context.view_workshop"],
                ),
            )
        )
    else:
        acl.append(
            (
                Deny,
                Everyone,
                (
                    PERMISSIONS["context.signup_workshop"],
                    PERMISSIONS["context.signout_workshop"],
                ),
            )
        )

    trainers_perms = (
        PERMISSIONS["context.view_workshop"],
        PERMISSIONS["context.duplicate_workshop"],
        PERMISSIONS["context.edit_workshop"],
        PERMISSIONS["context.view_file"],
        PERMISSIONS["context.edit_file"],
    )

    acl.append((Allow, get_access_right("global_accompagnement"), trainers_perms))
    acl.append((Allow, get_access_right("global_supervisor_training"), trainers_perms))

    acl.extend((Allow, user.login.login, trainers_perms) for user in self.trainers)

    if self.company_manager is not None:
        for employee in self.company_manager.employees:
            if employee.login:
                # FIXME On doit plutôt vérifier que l'employé en question a la permission 'es_trainer'
                if "trainer" in employee.login.groups:
                    acl.append((Allow, employee.login.login, trainers_perms))

    return acl


def get_timeslot_acl(self):
    """
    Return ACL for timeslots
    """
    if self.workshop:
        return get_workshop_acl(self.workshop)
    return []


def get_company_acl(self):
    """
    Compute the company's acl
    """
    acl = []
    perms = []

    for access_right_name, perm_suffix in (
        (ACCESS_RIGHTS["es_trainer"]["name"], "training"),
        (ACCESS_RIGHTS["es_constructor"]["name"], "construction"),
    ):
        if self.has_member_with_access_right(access_right_name):
            perms.append(PERMISSIONS[f"context.add_{perm_suffix}"])
            perms.append(PERMISSIONS[f"context.view_{perm_suffix}"])

    perms.extend(
        [
            PERMISSIONS["company.view"],
            PERMISSIONS["context.edit_company"],
            PERMISSIONS["context.view_file"],
            # for logo and header
            PERMISSIONS["context.edit_file"],
            PERMISSIONS["context.add_file"],
            PERMISSIONS["context.delete_file"],
            PERMISSIONS["context.add_customer"],
            PERMISSIONS["context.add_supplier"],
            PERMISSIONS["context.add_project"],
            PERMISSIONS["context.add_sale_product"],
            PERMISSIONS["context.add_sale_product_category"],
            PERMISSIONS["context.add_supplier_order"],
            PERMISSIONS["context.add_supplier_invoice"],
            PERMISSIONS["context.add_estimation"],
            PERMISSIONS["context.add_invoice"],
            PERMISSIONS["context.add_expensesheet"],
            PERMISSIONS["context.view_salarysheet_pdf"],
            PERMISSIONS["context.view_treasury_pdf"],
            PERMISSIONS["context.view_incomestatement_pdf"],
        ]
    )

    if self.active:
        acl.append(
            (
                Deny,
                get_access_right("es_no_invoice_without_estimation"),
                PERMISSIONS["context.add_invoice"],
            )
        )
        acl.append((Allow, "company:{}".format(self.id), perms))

    acl.append((Allow, get_access_right("global_company_supervisor"), perms))
    acl.append((Allow, get_access_right("global_config_company"), perms))

    return acl


def get_project_acl(self):
    """
    Return acl for a project
    """
    acl = []

    perms = (
        FILE_PARENT_VIEW_PERMS
        + FILE_PARENT_EDIT_PERMS
        + (
            PERMISSIONS["context.edit_project"],
            PERMISSIONS["context.add_estimation"],
            PERMISSIONS["context.add_invoice"],
        )
    )
    if len(self.phases) > 1:
        perms += (PERMISSIONS["context.add_phase"],)

    if not self.has_tasks():
        perms += (PERMISSIONS["context.delete_project"],)
    else:
        acl.insert(0, (Deny, Everyone, (PERMISSIONS["context.delete_project"],)))

    if any([b.visible for b in self.businesses]):
        perms += (PERMISSIONS["context.list_businesses"],)

    admin_perms = perms[:]
    admin_perms += (PERMISSIONS["context.list_businesses"],)
    acl.append((Allow, get_access_right("global_company_supervisor"), admin_perms))

    acl.append((Allow, "company:{}".format(self.company_id), perms))

    return acl


def get_phase_acl(self):
    """
    Return acl for a phase
    """
    acl = []
    perms = (PERMISSIONS["context.edit_phase"],)
    if DBSESSION().query(Task.id).filter_by(phase_id=self.id).count() == 0:
        perms += (PERMISSIONS["context.delete_phase"],)
    else:
        acl.insert(0, (Deny, Everyone, (PERMISSIONS["context.delete_phase"])))

    company_id = self.project.company_id
    acl.append((Allow, "company:{}".format(company_id), perms))
    acl.append((Allow, get_access_right("global_company_supervisor"), perms))
    return acl


def get_business_acl(self):
    """
    Compute the acl for the Business object
    """
    acl = []
    perms = FILE_PARENT_VIEW_PERMS[:]
    admin_perms = FILE_PARENT_VIEW_PERMS[:]

    edit_perms = (
        PERMISSIONS["context.edit_business"],
        PERMISSIONS["context.add_invoice"],
        PERMISSIONS["context.py3o_template_business"],
        PERMISSIONS["context.add_estimation"],
    ) + FILE_PARENT_EDIT_PERMS
    admin_perms += edit_perms
    perms += edit_perms

    if not self.invoices:
        perms += (PERMISSIONS["context.delete_business"],)
        admin_perms += (PERMISSIONS["context.delete_business"],)

    if self.business_type.bpf_related:
        perms += (PERMISSIONS["context.edit_bpf"],)
        admin_perms += (PERMISSIONS["context.edit_bpf"],)

    acl.append((Allow, get_access_right("global_company_supervisor"), admin_perms))

    company_id = self.project.company_id
    acl.append((Allow, f"company:{company_id}", perms))

    return acl


def get_business_payment_deadline_acl(self):
    acl = []

    company_id = self.business.project.company_id

    # "ALL": on ne peut pas modifier le plan de paiement
    # "SUMMARY" : on peut modifier le contenu mais pas le nombre
    # "NONE" : on peut tout modifier
    # "ALL_NO_DATE" : on peut modifier les dates

    perms = (PERMISSIONS["context.edit_business_payment_deadline"],)
    perms += (PERMISSIONS["context.edit_business_payment_deadline.invoice_id"],)
    if (
        not (self.invoiced and self.invoice_id)
        and self.estimation.paymentDisplay != "ALL"
    ):
        perms += (PERMISSIONS["context.edit_business_payment_deadline.amount"],)
        if not self.date or self.estimation.paymentDisplay != "ALL_NO_DATE":
            perms += (PERMISSIONS["context.edit_business_payment_deadline.date"],)
            if self.estimation.paymentDisplay == "NONE":
                remaining_deadlines = [
                    deadline
                    for deadline in self.business.payment_deadlines
                    if not deadline.invoiced
                ]
                if len(remaining_deadlines) > 1:
                    perms += (PERMISSIONS["context.delete_business_payment_deadline"],)

    acl.append((Allow, f"company:{company_id}", perms))
    acl.append((Allow, get_access_right("global_company_supervisor"), perms))

    return acl


# invoice/estimation/cancelinvoice/supplier_order/supplier_invoice
def _get_user_status_acl(
    self, type_, include_duplicate=True
) -> List[Tuple[str, str, Iterable[str]]]:
    """
    Return the common status related acls
    """
    perms = FILE_PARENT_VIEW_PERMS + FILE_PARENT_EDIT_PERMS

    if include_duplicate:
        perms += (PERMISSIONS[f"context.duplicate_{type_}"],)

    # Some classes holds their validation status un `validation_status` other
    # in `status`
    try:
        validation_status = self.validation_status
    except AttributeError:
        validation_status = self.status

    if validation_status in ("draft", "invalid"):
        perms += (
            PERMISSIONS[f"context.edit_{type_}"],
            PERMISSIONS[f"context.set_wait_{type_}"],
            PERMISSIONS[f"context.delete_{type_}"],
            PERMISSIONS[f"context.set_draft_{type_}"],
        )
    if validation_status in ("wait",):
        perms += (PERMISSIONS[f"context.set_draft_{type_}"],)

    return [
        (Allow, "company:{}".format(self.company_id), perms),
        (Allow, get_access_right("global_company_supervisor"), perms),
    ]


def _get_admin_status_acl(
    self, type_: str, include_duplicate=True
) -> List[Tuple[str, str, Iterable[str]]]:
    """
    Définit les actions que l'on peut mener si on a le Role
    "global_validate_{type_}"
    """
    perms = FILE_PARENT_EDIT_PERMS + FILE_PARENT_VIEW_PERMS

    if include_duplicate:
        perms += (PERMISSIONS[f"context.duplicate_{type_}"],)
    try:
        validation_status = self.validation_status
    except AttributeError:
        validation_status = self.status

    if validation_status in ("draft", "wait", "invalid"):
        perms += (
            PERMISSIONS[f"context.edit_{type_}"],
            PERMISSIONS[f"context.validate_{type_}"],
            PERMISSIONS[f"context.delete_{type_}"],
            PERMISSIONS[f"context.set_draft_{type_}"],
        )
        if validation_status == "wait":
            perms += (PERMISSIONS[f"context.invalidate_{type_}"],)
        else:
            perms += (PERMISSIONS[f"context.set_wait_{type_}"],)

    return [
        (Allow, f"access_right:global_validate_{type_}", perms),
    ]


def _get_estimation_main_acl(self):
    """
    Définit les droits généraux d'un devis
    """
    if self.status != "valid":
        return []

    perms = (PERMISSIONS["context.set_signed_status_estimation"],)

    if self.signed_status != "aborted":
        if not self.business.visible:
            perms += (PERMISSIONS["context.geninv_estimation"],)
    return [
        (Allow, "company:{}".format(self.company_id), perms),
        (Allow, get_access_right("global_company_supervisor"), perms),
        (Allow, get_access_right("global_validate_estimation"), perms),
    ]


def get_internal_estimation_specific_acl(self):
    acl = []
    # On autorise le client interne à signer le devis
    if self.signed_status != "signed":
        acl.append(
            (
                Allow,
                "company:{}".format(self.customer.source_company_id),
                (PERMISSIONS["context.set_signed_status_estimation"],),
            )
        )
    # On n'a pas de commande fournisseur associée
    if not self.supplier_order_id:
        # Laisse le temps à celery de générer la commande fournisseur interne
        # (pour éviter les doublons)
        now = datetime.datetime.now()
        if self.status_date < now - datetime.timedelta(minutes=1):
            # Ici celery n'a pas générer la commande fournisseur interne
            # pour une raison ou une autre
            acl.append(
                (
                    Deny,
                    Everyone,
                    (PERMISSIONS["context.geninv_estimation"],),
                )
            )
            acl.append(
                (
                    Allow,
                    get_access_right("global_company_supervisor"),
                    (PERMISSIONS["context.gen_supplier_order_estimation"],),
                )
            )
            acl.append(
                (
                    Allow,
                    get_access_right("global_validate_estimation"),
                    (PERMISSIONS["context.gen_supplier_order_estimation"],),
                )
            )
    return acl


def get_estimation_default_acl(self):
    """
    Return acl for the estimation handling

    :returns: A pyramid acl list
    :rtype: list
    """
    acl = []  # Le cas particulier pour les factures internes
    if self.status == "valid" and self.internal:
        acl.extend(get_internal_estimation_specific_acl(self))

    # Les acl pour les statuts de validation
    acl.extend(_get_admin_status_acl(self, "estimation"))
    acl.extend(_get_user_status_acl(self, "estimation"))
    # Les acl pour les statuts de signature
    acl.extend(_get_estimation_main_acl(self))

    # Auto validation avec et sans montant limite
    if self.status != "valid":
        acl.append(
            (
                Allow,
                get_access_right("es_validate_estimation"),
                (PERMISSIONS["context.edit_estimation"],),
            )
        )
        # Cette partie devrait idéalement être gérée en dehors des acl
        login = get_current_login()
        if login:
            estimation_limit_amount = login.estimation_limit_amount
            total = math_utils.integer_to_amount(self.total_ht(), 5)
            if estimation_limit_amount is None or total <= estimation_limit_amount:
                acl.append(
                    (
                        Allow,
                        get_access_right("es_validate_estimation"),
                        PERMISSIONS["context.validate_estimation"],
                    )
                )
    return acl


def _get_invoice_urssaf3p_acl(self: "Invoice"):
    acl = []
    if (
        self.customer.urssaf_data
        and self.customer.urssaf_data.registration_status
        and self.customer.urssaf_data.registration_status.status == "valid"
        # no support of partial payment
        and self.total() == self.topay()
        # cannot request more than once
        and self.urssaf_payment_request is None
    ):
        perms = ["context.request_urssaf3p_invoice"]
        acl = [
            (Allow, get_access_right("global_record_payment_invoice"), perms),
            (Allow, f"company:{self.company_id}", perms),
        ]
    return acl


def get_invoice_default_acl(self):
    """
    Return the acl for invoices

    :returns: A pyramid acl list
    :rtype: list
    """
    acl = []
    if self.invoicing_mode == self.PROGRESS_MODE:
        acl.append(
            (
                Deny,
                Everyone,
                PERMISSIONS["context.duplicate_invoice"],
            )
        )

    acl.extend(_get_admin_status_acl(self, "invoice"))

    if self.status == "valid":
        if self.paid_status != "resulted":
            for i in "global_accountant", "global_record_payment_invoice":
                acl.append(
                    (
                        Allow,
                        get_access_right(i),
                        (PERMISSIONS["context.add_payment_invoice"],),
                    )
                )
            if self.total() > 0:
                for i in (
                    "global_accountant",
                    "global_record_payment_invoice",
                    "global_validate_invoice",
                    "global_company_supervisor",
                ):
                    acl.append(
                        (
                            Allow,
                            get_access_right(i),
                            (PERMISSIONS["context.gen_cancelinvoice_invoice"],),
                        )
                    )

        elif self.total() > 0 and not self.internal:
            # Ici on autorise la génération d'avoir pour des factures encaissées
            # mais pas dans le cas des factures internes
            # On autorise également la génération d'encaissement
            for i in (
                "global_accountant",
                "global_record_payment_invoice",
            ):
                acl.append(
                    (
                        Allow,
                        get_access_right(i),
                        (
                            PERMISSIONS["context.gen_cancelinvoice_invoice"],
                            PERMISSIONS["context.add_payment_invoice"],
                        ),
                    )
                )

        if self.internal and not self.supplier_invoice_id:
            # Laisse le temps à celery de générer la facture fournisseur interne
            now = datetime.datetime.now()
            if self.status_date < now - datetime.timedelta(minutes=1):
                perm = (PERMISSIONS["context.gen_supplier_invoice_invoice"],)
                for i in (
                    "global_company_supervisor",
                    "global_accountant",
                    "global_validate_invoice",
                    "global_record_payment_invoice",
                ):
                    acl.append((Allow, get_access_right(i), perm))

        acl.append(
            (
                Allow,
                get_access_right("global_accountant"),
                (PERMISSIONS["context.set_treasury_invoice"],),
            )
        )

    # Statuts spécifiques ES
    # Auto validation avec et sans montant limite
    if self.status != "valid":
        login = get_current_login()
        if login is not None:
            invoice_limit_amount = login.invoice_limit_amount
            total = math_utils.integer_to_amount(self.total_ht(), 5)
            acl.append(
                (
                    Allow,
                    get_access_right("es_validate_invoice"),
                    PERMISSIONS["context.edit_invoice"],
                ),
            )
            if invoice_limit_amount is None or total <= invoice_limit_amount:
                acl.append(
                    (
                        Allow,
                        get_access_right("es_validate_invoice"),
                        (PERMISSIONS["context.validate_invoice"],),
                    )
                )

    acl.append(
        (
            Deny,
            get_access_right("es_no_invoice_without_estimation"),
            (PERMISSIONS["context.duplicate_invoice"],),
        )
    )
    acl.extend(_get_user_status_acl(self, "invoice"))

    if self.status == "valid" and self.paid_status != "resulted" and self.total() > 0:
        if not self.internal:
            acl.append(
                (
                    Allow,
                    get_access_right("es_record_payment_invoice"),
                    (PERMISSIONS["context.add_payment_invoice"],),
                )
            )

        acl.append(
            (
                Allow,
                "company:{}".format(self.company_id),
                (PERMISSIONS["context.gen_cancelinvoice_invoice"],),
            )
        )
        acl.extend(_get_invoice_urssaf3p_acl(self))

    if self.status == "valid" and self.paid_status == "resulted":
        acl.append(
            (
                Allow,
                get_access_right("es_cancel_resulted_invoice"),
                (PERMISSIONS["context.gen_cancelinvoice_invoice"],),
            )
        )

    return acl


def get_cancelinvoice_default_acl(self):
    """
    Return the acl for cancelinvoices
    """
    acl = []
    acl.extend(_get_admin_status_acl(self, "cancelinvoice", include_duplicate=False))

    if self.status == "valid":
        acl.append(
            (
                Allow,
                get_access_right("global_accountant"),
                (PERMISSIONS["context.set_treasury_cancelinvoice"],),
            )
        )

        if self.internal and not self.supplier_invoice_id:
            # Laisse le temps à celery de générer la facture fournisseur interne
            now = datetime.datetime.now()
            if self.status_date < now - datetime.timedelta(minutes=1):
                acl.append(
                    (
                        Allow,
                        get_access_right("global_validate_cancelinvoice"),
                        (PERMISSIONS["context.gen_supplier_invoice_invoice"],),
                    )
                )

    if self.status != "valid":
        acl.append(
            (
                Allow,
                get_access_right("es_validate_cancelinvoice"),
                (PERMISSIONS["context.validate_cancelinvoice"],),
            )
        )

    acl.extend(_get_user_status_acl(self, "cancelinvoice", include_duplicate=False))
    return acl


def get_task_line_group_acl(self):
    """
    Return the task line acl
    """
    return self.task.__acl__()


def get_task_line_acl(self):
    """
    Return the task line acl
    """
    return self.group.__acl__()


def get_discount_line_acl(self):
    """
    Return the acls for accessing the discount line
    """
    return self.task.__acl__()


def get_post_ttc_line_acl(self):
    """
    Return the acls for accessing the post-TTC line
    """
    return self.task.__acl__()


def get_payment_line_acl(self):
    """
    Return the acls for accessing a payment line
    """
    return self.task.__acl__()


def get_expense_sheet_default_acl(self: ExpenseSheet):
    """
    Compute the expense Sheet acl

    :returns: Pyramid acl
    :rtype: list
    """
    acl = _get_admin_status_acl(self, "expensesheet")
    acl.extend(_get_user_status_acl(self, "expensesheet"))
    acl.append(
        (Allow, "company:{}".format(self.company_id), ("context.add_expensesheet",)),
    )
    acl.append(
        (
            Allow,
            get_access_right("global_company_supervisor"),
            ("context.add_expensesheet",),
        ),
    )

    admin_perms = (PERMISSIONS["context.set_justified_expensesheet"],)
    acl.append((Allow, get_access_right("global_validate_expensesheet"), admin_perms))

    if self.status == "valid" and self.paid_status != "resulted":
        # Si la NDD n'est pas payée :
        # cas 1 :
        # on a déjà un paiement en attente :
        # on peut le supprimer

        # cas 2 : on a pas encore de paiement en attente et il reste
        # des dépenses à payer:
        # on peut ajouter un paiement ou un paiement en attente

        if not self.has_waiting_payment() and self.amount_waiting_for_payment() > 0:
            perms = (
                PERMISSIONS["context.add_payment_expensesheet"],
                PERMISSIONS["context.add_to_sepa_expensesheet"],
            )
            acl.append(
                (Allow, get_access_right("global_record_payment_expensesheet"), perms)
            )

    return acl


def get_base_sepa_waiting_payment_acl(self):
    acl = get_base_acl(self)
    if self.paid_status == self.WAIT_STATUS:
        acl.append(
            (
                Allow,
                get_access_right("global_record_payment_expensesheet"),
                (PERMISSIONS["context.delete_sepa_waiting_payment"],),
            )
        )
        acl.append(
            (
                Allow,
                get_access_right("global_record_payment_supplier_invoice"),
                (PERMISSIONS["context.delete_sepa_waiting_payment"],),
            )
        )
    return acl


def get_expenseline_acl(self):
    """
    Return the default acl for an expenseline
    """
    return get_expense_sheet_default_acl(self.sheet)


def get_supplier_order_default_acl(self) -> List[Tuple[str, str, Iterable[str]]]:
    """ """
    acl = []

    if self.internal:
        acl.append((Deny, Everyone, (PERMISSIONS["context.duplicate_supplier_order"],)))
        acl.append((Deny, Everyone, (PERMISSIONS["context.edit_supplier_order"],)))
        acl.append((Deny, Everyone, (PERMISSIONS["context.edit_file"],)))

    acl.extend(_get_admin_status_acl(self, "supplier_order"))
    acl.extend(_get_user_status_acl(self, "supplier_order"))

    # Allow or deny autovalidation
    if self.status in ("draft", "wait", "invalid"):
        login = get_current_login()
        if login is not None:
            supplier_order_limit_amount = login.supplier_order_limit_amount
            total = math_utils.integer_to_amount(self.total_ht)

            if (
                supplier_order_limit_amount is None
                or total <= supplier_order_limit_amount
            ):
                autovalidate = (
                    Allow,
                    get_access_right("es_validate_supplier_order"),
                    PERMISSIONS["context.validate_supplier_order"],
                )
                acl.append(autovalidate)
    return acl


def get_supplier_order_line_acl(self):
    return get_supplier_order_default_acl(self.supplier_order)


def get_supplier_invoice_acl(self) -> List[Tuple[str, str, Iterable[str]]]:
    """ """
    acl = []
    if self.internal:
        acl.append(
            (
                Deny,
                Everyone,
                PERMISSIONS["context.delete_supplier_invoice"],
            )
        )
        acl.append((Deny, Everyone, PERMISSIONS["context.duplicate_supplier_invoice"]))
        acl.append(
            (Deny, Everyone, PERMISSIONS["context.add_payment_supplier_invoice"])
        )
    acl.extend(_get_admin_status_acl(self, "supplier_invoice"))
    acl.extend(_get_user_status_acl(self, "supplier_invoice"))

    if self.status == "valid":
        if self.paid_status != "resulted":
            if not self.has_waiting_payment():
                perms = (PERMISSIONS["context.add_payment_supplier_invoice"],)
                if not self.internal:
                    # On regarde si il y a une part entrepreneur ou fournisseur à payer
                    # Le traitement de quelle part on doit payer est fait directement
                    # dans la vue
                    amount_waiting_for_payment = 0
                    if self.cae_percentage > 0:
                        amount_waiting_for_payment += (
                            self.cae_amount_waiting_for_payment()
                        )
                    if self.cae_percentage < 100:
                        amount_waiting_for_payment += (
                            self.worker_amount_waiting_for_payment()
                        )
                    if amount_waiting_for_payment > 0:
                        perms += (PERMISSIONS["context.add_to_sepa_supplier_invoice"],)
                acl.append(
                    (Allow, get_access_right("global_record_payment_invoice"), perms)
                )

        acl.append(
            (
                Allow,
                get_access_right("global_accountant"),
                PERMISSIONS["context.set_treasury_supplier_invoice"],
            )
        )

    # Allow or deny autovalidation
    if self.status in ("draft", "wait", "invalid"):
        login = get_current_login()
        if login is not None:
            supplier_invoice_limit_amount = login.supplier_invoice_limit_amount
            total = math_utils.integer_to_amount(self.total_ht)

            if (
                supplier_invoice_limit_amount is None
                or total <= supplier_invoice_limit_amount
            ):
                autovalidate = (
                    Allow,
                    get_access_right("es_validate_supplier_invoice"),
                    PERMISSIONS["context.validate_supplier_invoice"],
                )
                acl.append(autovalidate)
    return acl


def get_supplier_invoice_line_acl(self):
    return get_supplier_invoice_acl(self.supplier_invoice)


def _get_sap_attestation_acl(self) -> List[Tuple[str, str, Iterable[str]]]:
    acl = []

    admin_perms = (
        PERMISSIONS["context.add_file"],
        PERMISSIONS["context.edit_file"],
        PERMISSIONS["context.view_file"],
    )
    company_perms = (PERMISSIONS["context.view_file"],)

    acl.append((Allow, get_access_right("global_company_supervisor"), admin_perms))

    acl.append((Allow, f"company:{self.customer.company_id}", company_perms))
    return acl


def _get_base_payment_acl(
    self,
    type_: str,
    has_es_payment_record_group: bool = False,
    free_edition: bool = True,
) -> List[Tuple[str, str, Iterable[str]]]:
    """
    Compute the acl for a model implementing PaymentModelMixin

    :has_es_payment_record_group: Y a-t-il un groupe pour les ES permettant
    la saisie de paiements

    :free_edition: Y a-t-il la possibilité de modifier et supprimer le paiement
    librement, si non, le paiement ne peut être supprimé que le jour où il a été
    créé et ne peut être modifié si il est passé en compta
    """
    admin_perms = ()
    if free_edition or not self.exported:
        admin_perms += (PERMISSIONS["context.edit_payment"],)

    if free_edition or (
        self.created_at.date() == datetime.date.today() and not self.exported
    ):
        admin_perms += (PERMISSIONS["context.delete_payment"],)

    if self.amount > 0:
        admin_perms += (PERMISSIONS["context.gen_inverse_payment"],)

    acl: List = [
        (
            Allow,
            get_access_right(f"global_record_payment_{type_}"),
            admin_perms,
        )
    ]

    if has_es_payment_record_group:
        # On ne veut pas qu'un entrepreneur modifie un paiement exporté en compta
        if not self.exported:
            acl.append(
                (Allow, get_access_right("es_record_payment_invoice"), admin_perms)
            )

    return acl


def get_task_payment_default_acl(self):
    return _get_base_payment_acl(
        self, "invoice", has_es_payment_record_group=True, free_edition=False
    )


def get_expense_payment_acl(self):
    return _get_base_payment_acl(
        self, "expensesheet", has_es_payment_record_group=False
    )


def get_supplier_payment_acl(self):
    return _get_base_payment_acl(
        self, "supplier_invoice", has_es_payment_record_group=False
    )


def get_customer_acl(self):
    """
    Compute the customer's acl
    """
    acl = []
    perms = (PERMISSIONS["context.edit_customer"],)

    if not self.has_tasks():
        perms += (PERMISSIONS["context.delete_customer"],)
    else:
        acl.insert(0, (Deny, Everyone, (PERMISSIONS["context.delete_customer"],)))

    if not self.archived:
        perms += (
            PERMISSIONS["context.add_estimation"],
            PERMISSIONS["context.add_invoice"],
        )
    acl.append((Allow, "company:{}".format(self.company_id), perms))
    acl.append((Allow, get_access_right("global_company_supervisor"), perms))

    return acl


def get_supplier_acl(self, request):
    """
    Compute the supplier's acl
    """
    acl = []
    perms = (PERMISSIONS["context.edit_supplier"],)

    if is_supplier_deletable(request, self):
        perms += (PERMISSIONS["context.delete_supplier"],)
    else:
        acl.insert(0, (Deny, Everyone, (PERMISSIONS["context.delete_supplier"],)))

    acl.append((Allow, "company:{}".format(self.company_id), perms))
    acl.append((Allow, get_access_right("global_company_supervisor"), perms))

    return acl


def get_file_acl(self):
    """
    Compute the acl for a file object
    a file object's acl are simply the parent's
    """
    acl = []
    if isinstance(self.parent, UserDatas):
        acl = self.parent.user.__acl__
    elif self.parent is not None:
        acl = self.parent.__acl__
    # Exceptions: headers and logos are not attached throught the Node's parent
    # rel
    elif self.company_header_backref is not None:
        acl = self.company_header_backref.__acl__
    elif self.company_logo_backref is not None:
        acl = self.company_logo_backref.__acl__
    elif self.sepa_credit_transfer_backref is not None:
        acl = self.sepa_credit_transfer_backref.__acl__
    elif self.user_photo_backref is not None:
        acl = ((Allow, Authenticated, PERMISSIONS["context.view_file"]),)

    if acl and callable(acl):
        acl = acl()

    return acl


def get_product_category_acl(self):
    perms = (
        PERMISSIONS["context.edit_sale_product_category"],
        PERMISSIONS["context.delete_sale_product_category"],
    )
    acl = []
    acl.append((Allow, "company:{}".format(self.company_id), perms))
    acl.append((Allow, get_access_right("global_company_supervisor"), perms))

    return acl


def get_sale_product_acl(self):
    perms = (
        PERMISSIONS["context.add_stock_operation"],
        PERMISSIONS["context.edit_sale_product"],
    )
    if not self.is_locked():
        perms += (PERMISSIONS["context.delete_sale_product"],)

    if self.company.has_member_with_access_right(ACCESS_RIGHTS["es_trainer"]["name"]):
        perms += (PERMISSIONS["context.add_training_product"],)

    return [
        (Allow, "company:{}".format(self.company_id), perms),
        (Allow, get_access_right("global_company_supervisor"), perms),
    ]


def get_stock_operation_acl(self):
    return get_sale_product_acl(self.base_sale_product)


def get_work_item_acl(self):
    return get_sale_product_acl(self.sale_product_work)


def get_price_study_acl(self: PriceStudy):
    """
    Collect PriceStudy acl
    """
    perms = ()

    # C'est sale ce bout de code là, on devrait traiter ce cas là autrement
    if self.is_editable():
        perms += (PERMISSIONS["context.edit_price_study"],)

    admin_perms = perms[:]

    if self.is_admin_editable():
        admin_perms += (PERMISSIONS["context.edit_price_study"],)

    return [
        (Allow, "company:{}".format(self.task.company_id), perms),
        (Allow, get_access_right("global_company_supervisor"), admin_perms),
    ]


def get_price_study_product_acl(self):
    """
    Collect BasePriceStudyProduct context acl
    """
    return get_price_study_acl(self.price_study)


def get_progress_invoicing_plan_acl(self):
    perms = ()
    admin_perms = ()
    if self.task.status != "valid":
        admin_perms += (PERMISSIONS["context.edit_progress_invoicing_plan"],)
        if self.task.status != "wait":
            perms += (PERMISSIONS["context.edit_progress_invoicing_plan"],)

    return [
        (Allow, "company:{}".format(self.task.company_id), perms),
        (Allow, get_access_right("global_company_supervisor"), admin_perms),
    ]


def get_competence_acl(self):
    """
    Return acl for the Competence Grids objects
    """
    acl = []
    # CompetenceGridItem and CompetenceGridSubItem have properties pointing to the login
    login = self.contractor.login.login
    acl.append(
        (
            Allow,
            login,
            (
                PERMISSIONS["context.view_competence"],
                PERMISSIONS["context.edit_competence"],
            ),
        )
    )
    acl.append(
        (
            Allow,
            get_access_right("global_accompagnement"),
            (
                PERMISSIONS["context.view_competence"],
                PERMISSIONS["context.edit_competence"],
            ),
        )
    )
    return acl


def get_accounting_measure_acl(self):
    """
    Compile the default acl for TreasuryMeasureGrid and
    IncomeStatementMeasureGrid objects
    """
    if self.company is not None:
        return get_company_acl(self.company)
    return []


def get_indicator_acl(self) -> List[Tuple[str, str, Iterable[str]]]:
    """
    Compile Indicator acl
    """

    admin_perms = (PERMISSIONS["context.view_indicator"],)

    if self.status == self.DANGER_STATUS:
        admin_perms += (PERMISSIONS["context.force_indicator"],)

    else:
        admin_perms += (PERMISSIONS["context.validate_indicator"],)
    return [
        (
            Allow,
            get_access_right(group),
            admin_perms,
        )
        for group in [
            "global_company_supervisor",
            "global_validate_estimation",
            "global_validate_invoice",
            "global_accountant",
        ]
    ]


def get_statuslogentry_acl(self):
    acl = []
    base_perms = [
        PERMISSIONS["context.view_statuslogentry"],
    ]
    # Entries triggered by status change are autogenerated and cannot be edited.
    if self.status == "":
        owner_perms = [
            PERMISSIONS["context.edit_statuslogentry"],
            PERMISSIONS["context.delete_statuslogentry"],
        ]
    else:
        owner_perms = []

    if self.user and self.user.login:
        acl.append([Allow, self.user.login.login, base_perms + owner_perms])
    acl.append(
        [Allow, get_access_right("global_config_company"), base_perms + owner_perms]
    )

    if self.visibility == "public":
        company_id = self.get_company_id()
        acl.append([Allow, f"company:{company_id}", base_perms])

    if self.visibility != "private":
        acl.append([Allow, get_access_right("global_company_supervisor"), base_perms])
    return acl


def get_custom_business_indicator_acl(self) -> List[Tuple[str, str, Iterable[str]]]:
    """
    Compute acl for CustomBusinessIndicator management
    """
    user_perms = (PERMISSIONS["context.view_indicator"],)

    acl = get_indicator_acl(self)
    if not self.status == self.SUCCESS_STATUS:
        user_perms += (PERMISSIONS["context.force_indicator"],)

    company_id = self.business.project.company_id
    if company_id:
        acl.append((Allow, "company:{}".format(company_id), user_perms))

    return acl


def get_sale_file_requirement_acl(self):
    """
    Compile acl for SaleFileRequirement instances
    """
    # Si le parent est validé et l'indicateur est ok, on ne peut plus modifier
    perms = (PERMISSIONS["context.view_indicator"],)

    locked = False
    if self.status == self.SUCCESS_STATUS and self.file_id is not None:
        if hasattr(self.node, "status") and self.node.status == "valid":
            locked = True

    if not locked:
        acl = get_indicator_acl(self)
        if self.file_id is None:
            perms += (PERMISSIONS["context.add_file"],)

        else:
            perms += (PERMISSIONS["context.edit_file"],)

    else:
        acl = []

    # NOTE : appel à éviter mais ici ça fonctionne
    request = get_current_request()
    company_id = find_company_id_from_model(request, self)
    if company_id:
        acl.append((Allow, "company:{}".format(company_id), perms))

    acl.append((Allow, get_access_right("global_company_supervisor"), perms))
    return acl


def get_notification_acl(self: Notification):
    return [
        [
            Allow,
            f"user:{self.user_id}",
            [
                PERMISSIONS["context.view_notification"],
                PERMISSIONS["context.edit_notification"],
                PERMISSIONS["context.delete_notification"],
            ],
        ]
    ]


def _get_acl_forward_function(attr_path: List[str]):
    """
    Forward la responsabilité des acls à un objet accessible via une attr_path
    """

    def result(self):
        related = self
        for key in attr_path:
            related = getattr(related, key)
            if not related:
                raise Exception("No object found")
        return related.__acl__()

    return result


def get_smtp_settings_acl(self):
    perms = (
        PERMISSIONS["context.view"],
        PERMISSIONS["context.edit"],
    )
    if self.company_id:
        return [
            (Allow, f"company:{self.company_id}", perms),
            (Allow, get_access_right("global_config_company"), perms),
        ]
    else:
        return [
            (Allow, get_access_right("global_config_cae"), perms),
        ]


def get_sepa_credit_transfer_acl(self):
    perms = (
        PERMISSIONS["context.view"],
        PERMISSIONS["context.view_file"],
    )
    if self.status != self.CLOSED_STATUS:
        perms += (PERMISSIONS["context.edit"],)
    return [(Allow, get_access_right("global_accountant"), perms)]


def set_models_acl():
    """
    Add acl to the db objects used as context

    Here acl are set globally, but we'd like to set things more dynamically
    when different access_right will be implemented
    """
    Activity.__default_acl__ = get_activity_acl
    AccountingOperationUpload.__acl__ = get_base_acl
    Business.__default_acl__ = get_business_acl
    BusinessPaymentDeadline.__acl__ = get_business_payment_deadline_acl
    BusinessType.__acl__ = get_base_acl
    CustomInvoiceBookEntryModule.__acl__ = get_base_acl
    CancelInvoice.__default_acl__ = get_cancelinvoice_default_acl
    Company.__acl__ = get_company_acl
    CompetenceGrid.__acl__ = get_competence_acl
    CompetenceGridItem.__acl__ = get_competence_acl
    CompetenceGridSubItem.__acl__ = get_competence_acl
    ConfigFiles.__default_acl__ = [(Allow, Everyone, PERMISSIONS["context.view_file"])]
    ConfigurableOption.__acl__ = get_base_acl
    Customer.__default_acl__ = get_customer_acl
    Supplier.__default_acl__ = get_supplier_acl
    DiscountLine.__acl__ = get_discount_line_acl
    PostTTCLine.__acl__ = get_post_ttc_line_acl
    Estimation.__default_acl__ = get_estimation_default_acl
    ExpenseSheet.__default_acl__ = get_expense_sheet_default_acl
    ExpensePayment.__acl__ = get_expense_payment_acl
    File.__default_acl__ = get_file_acl
    FormFieldDefinition.__acl__ = get_base_acl
    InternalEstimation.__default_acl__ = get_estimation_default_acl
    InternalInvoice.__default_acl__ = get_invoice_default_acl
    InternalCancelInvoice.__default_acl__ = get_cancelinvoice_default_acl
    InternalSupplierInvoice.__acl__ = get_supplier_invoice_acl
    Invoice.__default_acl__ = get_invoice_default_acl
    Indicator.__acl__ = get_indicator_acl
    CustomBusinessIndicator.__acl__ = get_custom_business_indicator_acl
    SaleFileRequirement.__acl__ = get_sale_file_requirement_acl
    Job.__default_acl__ = []
    Payment.__acl__ = get_task_payment_default_acl
    InternalPayment.__acl__ = get_task_payment_default_acl
    PaymentLine.__acl__ = get_payment_line_acl
    Phase.__acl__ = get_phase_acl
    Project.__default_acl__ = get_project_acl
    ProjectType.__acl__ = get_base_acl
    # Catalogue produit
    BaseSaleProduct.__acl__ = get_sale_product_acl
    SaleProductStockOperation.__acl__ = get_stock_operation_acl
    SaleProductCategory.__acl__ = get_product_category_acl
    WorkItem.__acl__ = get_work_item_acl

    # étude de prix
    PriceStudy.__acl__ = get_price_study_acl
    BasePriceStudyProduct.__acl__ = get_price_study_product_acl
    PriceStudyWorkItem.__acl__ = _get_acl_forward_function(
        ["price_study_work", "price_study"]
    )
    PriceStudyDiscount.__acl__ = _get_acl_forward_function(["price_study"])
    PriceStudyChapter.__acl__ = _get_acl_forward_function(["price_study"])
    ProgressInvoicingPlan.__acl__ = get_progress_invoicing_plan_acl
    ProgressInvoicingChapter.__acl__ = _get_acl_forward_function(["plan"])
    ProgressInvoicingBaseProduct.__acl__ = _get_acl_forward_function(["plan"])
    ProgressInvoicingWorkItem.__acl__ = _get_acl_forward_function(["plan"])
    # Notifications
    Notification.__acl__ = get_notification_acl
    # stats
    StatisticSheet.__acl__ = get_base_acl
    StatisticEntry.__acl__ = get_base_acl
    StatisticCriterion.__acl__ = get_base_acl
    SupplierOrder.__acl__ = get_supplier_order_default_acl
    SupplierOrderLine.__acl__ = get_supplier_order_line_acl
    SupplierInvoice.__acl__ = get_supplier_invoice_acl
    SupplierInvoiceLine.__acl__ = get_supplier_invoice_line_acl
    SupplierInvoiceSupplierPayment.__acl__ = get_supplier_payment_acl
    SupplierInvoiceUserPayment.__acl__ = get_supplier_payment_acl
    TaskLine.__acl__ = get_task_line_acl
    TaskLineGroup.__acl__ = get_task_line_group_acl
    TaskMention.__acl__ = get_base_acl
    TaskInsuranceOption.__acl__ = get_base_acl
    Template.__default_acl__ = get_base_acl
    TemplatingHistory.__acl__ = get_base_acl
    Timeslot.__default_acl__ = get_timeslot_acl
    BalanceSheetMeasureGrid.__acl__ = get_accounting_measure_acl
    ActiveBalanceSheetMeasureType.__acl__ = get_base_acl
    PassiveBalanceSheetMeasureType.__acl__ = get_base_acl
    TreasuryMeasureGrid.__acl__ = get_accounting_measure_acl
    TreasuryMeasureType.__acl__ = get_base_acl
    TreasuryMeasureTypeCategory.__acl__ = get_base_acl
    TrainerDatas.__default_acl__ = _get_acl_forward_function(["user"])
    IncomeStatementMeasureGrid.__acl__ = get_accounting_measure_acl
    IncomeStatementMeasureType.__acl__ = get_base_acl
    IncomeStatementMeasureTypeCategory.__acl__ = get_base_acl
    AccountingClosure.__acl__ = get_base_acl
    AccountingExportLogEntry.__acl__ = get_base_acl
    GeneralLedgerAccountWording.__acl__ = get_base_acl
    User.__acl__ = get_user_acl
    UserDatas.__acl__ = get_userdatas_acl

    Workshop.__acl__ = get_workshop_acl

    StatusLogEntry.__acl__ = get_statuslogentry_acl

    Tva.__acl__ = get_base_acl
    BaseExpenseLine.__acl__ = get_expenseline_acl
    ExpenseType.__acl__ = get_base_acl
    CareerStage.__acl__ = get_base_acl
    CareerPath.__acl__ = get_career_path_acl
    BankRemittance.__acl__ = get_base_acl
    SAPAttestation.__acl__ = _get_sap_attestation_acl
    CustomDocumentation.__acl__ = get_base_acl
    SmtpSettings.__acl__ = get_smtp_settings_acl

    SepaCreditTransfer.__acl__ = get_sepa_credit_transfer_acl
    BaseSepaWaitingPayment.__acl__ = get_base_sepa_waiting_payment_acl
