import logging
import colander
from caerp.consts.permissions import PERMISSIONS
from sqlalchemy.orm import (
    contains_eager,
    load_only,
)

from caerp_base.models.base import DBSESSION
from caerp.forms.validation.tasks import get_list_schema
from caerp.models.company import Company
from caerp.models.task import (
    Task,
    Estimation,
    InternalEstimation,
    Invoice,
    InternalInvoice,
    CancelInvoice,
    InternalCancelInvoice,
)
from caerp.models.third_party.customer import Customer
from caerp.views import BaseListView


logger = logging.getLogger(__name__)


class TasksValidationView(BaseListView):
    sort_columns = dict(
        date=Task.date,
        status_date=Task.status_date,
        internal_number=Task.internal_number,
        customer=Customer.name,
        company=Company.name,
        ht=Task.ht,
        ttc=Task.ttc,
        tva=Task.tva,
    )
    add_template_vars = (
        "title",
        "task_types",
    )
    default_sort = "status_date"
    default_direction = "desc"
    task_classes = []
    task_types = None

    def get_schema(self):
        return get_list_schema(self.request)

    def query(self):
        query = DBSESSION().query(Task)
        query = query.with_polymorphic(self.task_classes)
        query = query.outerjoin(Task.customer)
        query = query.outerjoin(Task.company)
        query = query.options(
            contains_eager(Task.customer).load_only(
                Customer.company_name,
                Customer.code,
                Customer.id,
                Customer.firstname,
                Customer.lastname,
                Customer.civilite,
                Customer.type,
            )
        )
        query = query.options(
            contains_eager(Task.company).load_only(
                Company.name,
                Company.id,
                Company.follower_id,
            )
        )
        query = query.options(
            load_only(
                "_acl",
                "name",
                "date",
                "id",
                "ht",
                "tva",
                "ttc",
                "company_id",
                "customer_id",
                "internal_number",
                "status",
                "status_date",
            )
        )
        query = query.filter(Task.status == "wait")
        return query

    def filter_company(self, query, appstruct):
        company_id = appstruct.get("company_id")
        if company_id not in (None, colander.null):
            query = query.filter(Task.company_id == company_id)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            query = query.filter(Company.antenne_id == antenne_id)
        return query

    def filter_customer(self, query, appstruct):
        customer_id = appstruct.get("customer_id")
        if customer_id not in (None, colander.null):
            query = query.filter(Task.customer_id == customer_id)
        return query

    def filter_doctype(self, query, appstruct):
        type_ = appstruct.get("doctype")
        if type_ in self.task_types:
            query = query.filter(Task.type_ == type_)
        else:
            query = query.filter(Task.type_.in_(self.task_types))
        return query

    def filter_business_type_id(self, query, appstruct):
        business_type_id = appstruct.get("business_type_id")
        if business_type_id not in ("all", None):
            query = query.filter(Task.business_type_id == business_type_id)
        return query

    def filter_follower(self, query, appstruct):
        follower_id = appstruct.get("follower_id")
        if follower_id not in (None, colander.null):
            query = query.filter(Company.follower_id == follower_id)
        return query


class EstimationsValidationView(TasksValidationView):
    title = "Devis en attente de validation"

    task_classes = [Estimation, InternalEstimation]
    task_types = ("estimation", "internalestimation")

    def get_schema(self):
        return get_list_schema(self.request, excludes=("doctype",))


class InvoicesValidationView(TasksValidationView):
    title = "Factures et avoirs en attente de validation"
    task_classes = [Invoice, InternalInvoice, CancelInvoice, InternalCancelInvoice]
    task_types = Task.invoice_types


def includeme(config):
    config.add_route("validation_estimations", "validation/estimations")
    config.add_route("validation_invoices", "validation/invoices")
    config.add_view(
        EstimationsValidationView,
        route_name="validation_estimations",
        renderer="validation/tasks.mako",
        permission=PERMISSIONS["global.validate_estimation"],
    )
    config.add_view(
        InvoicesValidationView,
        route_name="validation_invoices",
        renderer="validation/tasks.mako",
        permission=PERMISSIONS["global.validate_invoice"],
    )
    config.add_admin_menu(
        parent="validation",
        order=0,
        label="Devis",
        href="/validation/estimations",
        permission=PERMISSIONS["global.validate_estimation"],
    )
    config.add_admin_menu(
        parent="validation",
        order=1,
        label="Factures",
        href="/validation/invoices",
        permission=PERMISSIONS["global.validate_invoice"],
    )
