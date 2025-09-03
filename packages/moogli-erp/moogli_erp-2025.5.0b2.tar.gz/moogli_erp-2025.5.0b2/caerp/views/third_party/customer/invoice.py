import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.models.task import Task
from caerp.models.third_party.customer import Customer
from caerp.views import TreeMixin
from caerp.views.company.routes import COMPANY_INVOICE_ADD_ROUTE
from caerp.views.invoices.lists import (
    CompanyInvoicesListView,
    CompanyInvoicesCsvView,
    CompanyInvoicesXlsView,
    CompanyInvoicesOdsView,
    filter_all_status,
)
from .routes import (
    CUSTOMER_ITEM_INVOICE_ROUTE,
    CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
)
from .lists import CustomersListView

logger = logging.getLogger(__name__)


class CustomerInvoiceListView(CompanyInvoicesListView, TreeMixin):
    """
    Invoice list for one given Customer
    """

    route_name = CUSTOMER_ITEM_INVOICE_ROUTE
    add_template_vars = CompanyInvoicesListView.add_template_vars + ("add_url",)
    fields_to_exclude = ("customer",)

    @property
    def add_url(self):
        return self.request.route_path(
            COMPANY_INVOICE_ADD_ROUTE,
            id=self.context.company_id,
            _query={"customer_id": self.context.id},
        )

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    @property
    def title(self):
        return "Factures du client {0}".format(self.context.label)

    def filter_customer(self, query, appstruct):
        self.populate_navigation()
        query = query.filter(Task.customer_id == self.context.id)
        return query


class CustomerInvoicesCsvView(CompanyInvoicesCsvView):
    fields_to_exclude = ("customer",)

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_customer(self, query, appstruct):
        logger.debug(" + Filtering by customer_id")
        return query.filter(Task.customer_id == self.context.id)

    filter_status = filter_all_status


class CustomerInvoicesXlsView(CompanyInvoicesXlsView):
    fields_to_exclude = ("customer",)

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_customer(self, query, appstruct):
        logger.debug(" + Filtering by customer_id")
        return query.filter(Task.customer_id == self.context.id)

    filter_status = filter_all_status


class CustomerInvoicesOdsView(CompanyInvoicesOdsView):
    fields_to_exclude = ("customer",)

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_customer(self, query, appstruct):
        logger.debug(" + Filtering by customer_id")
        return query.filter(Task.customer_id == self.context.id)

    filter_status = filter_all_status


def includeme(config):
    list_permission = "company.view"
    config.add_tree_view(
        CustomerInvoiceListView,
        parent=CustomersListView,
        renderer="customers/invoices.mako",
        layout="customer",
        context=Customer,
        permission=PERMISSIONS[list_permission],
    )
    config.add_view(
        CustomerInvoicesCsvView,
        route_name=CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=csv",
        context=Customer,
        permission=PERMISSIONS[list_permission],
    )

    config.add_view(
        CustomerInvoicesOdsView,
        route_name=CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=ods",
        context=Customer,
        permission=PERMISSIONS[list_permission],
    )

    config.add_view(
        CustomerInvoicesXlsView,
        route_name=CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=xls",
        context=Customer,
        permission=PERMISSIONS[list_permission],
    )
