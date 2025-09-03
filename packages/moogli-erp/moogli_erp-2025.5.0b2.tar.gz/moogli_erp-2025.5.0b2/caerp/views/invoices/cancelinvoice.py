"""
    View for assets
"""
import logging
import os

from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.tasks.invoice import get_add_edit_cancelinvoice_schema
from caerp.models.task import CancelInvoice
from caerp.resources import task_preview_css
from caerp.utils.datetimes import format_date
from caerp.utils.widgets import ViewLink
from caerp.views import BaseEditView, add_panel_page_view
from caerp.views.business.business import BusinessOverviewView
from caerp.views.task.utils import get_task_url
from caerp.views.task.views import (
    TaskDeleteView,
    TaskEditView,
    TaskFilesView,
    TaskFileUploadView,
    TaskGeneralView,
    TaskMoveToPhaseView,
    TaskPdfView,
    TaskPreviewView,
    TaskSetDraftView,
    TaskSetMetadatasView,
    TaskSetProductsView,
)

from .invoice import InvoiceAccountingView
from .routes import (
    CINV_ITEM_ACCOUNTING_ROUTE,
    CINV_ITEM_FILES_ROUTE,
    CINV_ITEM_GENERAL_ROUTE,
    CINV_ITEM_PREVIEW_ROUTE,
    CINV_ITEM_ROUTE,
)

log = logging.getLogger(__name__)


class CancelInvoiceEditView(TaskEditView):
    route_name = "/cancelinvoices/{id}"

    @property
    def title(self):
        customer = self.context.customer
        customer_label = customer.label
        if customer.code is not None:
            customer_label += " ({0})".format(customer.code)

        return (
            "Modification de l’{tasktype_label} « {task.name} » "
            "avec le client {customer}".format(
                task=self.context,
                customer=customer_label,
                tasktype_label=self.context.get_type_label().lower(),
            )
        )

    def get_js_app_options(self) -> dict:
        options = super().get_js_app_options()
        options.update(
            {
                "invoicing_mode": self.context.invoicing_mode,
            }
        )
        return options


class CancelInvoiceDeleteView(TaskDeleteView):
    msg = "L'avoir {context.name} a bien été supprimé."


# VUE pour les factures validées
def get_title(invoice):
    if invoice.official_number is not None:
        return f"Avoir numéro {invoice.official_number}"
    else:
        return "Avoir en attente de validation"


class CancelInvoiceGeneralView(TaskGeneralView):
    route_name = CINV_ITEM_GENERAL_ROUTE
    file_route_name = CINV_ITEM_FILES_ROUTE

    @property
    def title(self):
        return get_title(self.current())


class CancelInvoicePreviewView(TaskPreviewView):
    route_name = CINV_ITEM_PREVIEW_ROUTE

    @property
    def title(self):
        return get_title(self.current())


class CancelInvoiceAccountingView(InvoiceAccountingView):
    route_name = CINV_ITEM_ACCOUNTING_ROUTE

    @property
    def title(self):
        return get_title(self.current())


class CancelInvoiceFilesView(TaskFilesView):
    route_name = CINV_ITEM_FILES_ROUTE

    @property
    def title(self):
        return get_title(self.current())


class CancelInvoicePdfView(TaskPdfView):
    pass


class CancelInvoiceSetTreasuryiew(BaseEditView):
    """
    View used to set treasury related informations

    context

        An invoice

    perms

        context.set_treasury_invoice
    """

    factory = CancelInvoice
    schema = get_add_edit_cancelinvoice_schema(
        includes=("financial_year",),
        title="Modifier l'année fiscale de la facture d'avoir",
    )

    def redirect(self, appstruct):
        return HTTPFound(
            get_task_url(self.request, suffix="/accounting"),
        )

    def before(self, form):
        BaseEditView.before(self, form)
        self.request.actionmenu.add(
            ViewLink(
                label="Revenir à la facture",
                url=get_task_url(self.request, suffix="/accounting"),
            )
        )

    @property
    def title(self):
        return "Avoir numéro {0} en date du {1}".format(
            self.context.official_number,
            format_date(self.context.date),
        )


class CancelInvoiceSetMetadatasView(TaskSetMetadatasView):
    """
    View used for editing invoice metadatas
    """

    @property
    def title(self):
        return "Modification de l’{tasktype_label} {task.name}".format(
            task=self.context,
            tasktype_label=self.context.get_type_label().lower(),
        )


class CancelInvoiceSetProductsView(TaskSetProductsView):
    @property
    def title(self):
        return "Configuration des codes produits pour l’avoir {0.name}".format(
            self.context
        )


def add_routes(config):
    """
    Add module related routes
    """
    for extension in ("html", "pdf", "preview"):
        route = f"{CINV_ITEM_ROUTE}.{extension}"
        config.add_route(route, route, traverse="/tasks/{id}")

    for action in (
        "addfile",
        "delete",
        "set_treasury",
        "set_products",
        "set_metadatas",
        "set_draft",
        "move",
    ):
        route = os.path.join(CINV_ITEM_ROUTE, action)
        config.add_route(route, route, traverse="/tasks/{id}")


def includeme(config):
    add_routes(config)

    # Here it's only company.view to allow redirection to the html view
    config.add_tree_view(
        CancelInvoiceEditView,
        parent=BusinessOverviewView,
        renderer="tasks/form.mako",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )

    config.add_view(
        CancelInvoiceDeleteView,
        route_name="/cancelinvoices/{id}/delete",
        permission=PERMISSIONS["context.delete_cancelinvoice"],
        require_csrf=True,
        request_method="POST",
        context=CancelInvoice,
    )

    config.add_view(
        CancelInvoicePdfView,
        route_name="/cancelinvoices/{id}.pdf",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )

    add_panel_page_view(
        config,
        "task_pdf_content",
        js_resources=(task_preview_css,),
        route_name="/cancelinvoices/{id}.preview",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )

    config.add_view(
        TaskFileUploadView,
        route_name="/cancelinvoices/{id}/addfile",
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.add_file"],
        context=CancelInvoice,
    )

    config.add_view(
        CancelInvoiceSetTreasuryiew,
        route_name="/cancelinvoices/{id}/set_treasury",
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.set_treasury_cancelinvoice"],
        context=CancelInvoice,
    )
    config.add_view(
        CancelInvoiceSetMetadatasView,
        route_name="/cancelinvoices/{id}/set_metadatas",
        renderer="tasks/duplicate.mako",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )
    config.add_view(
        TaskSetDraftView,
        route_name="/cancelinvoices/{id}/set_draft",
        permission=PERMISSIONS["context.set_draft_cancelinvoice"],
        require_csrf=True,
        request_method="POST",
        context=CancelInvoice,
    )
    config.add_view(
        CancelInvoiceSetProductsView,
        route_name="/cancelinvoices/{id}/set_products",
        permission=PERMISSIONS["context.set_treasury_cancelinvoice"],
        renderer="base/formpage.mako",
        context=CancelInvoice,
    )
    config.add_view(
        TaskMoveToPhaseView,
        route_name="/cancelinvoices/{id}/move",
        permission=PERMISSIONS["company.view"],
        require_csrf=True,
        request_method="POST",
        context=CancelInvoice,
    )

    config.add_tree_view(
        CancelInvoiceGeneralView,
        parent=BusinessOverviewView,
        layout="cancelinvoice",
        renderer="tasks/cancelinvoice/general.mako",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )
    config.add_tree_view(
        CancelInvoicePreviewView,
        parent=BusinessOverviewView,
        layout="cancelinvoice",
        renderer="tasks/preview.mako",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )
    config.add_tree_view(
        CancelInvoiceAccountingView,
        parent=BusinessOverviewView,
        layout="cancelinvoice",
        renderer="tasks/cancelinvoice/accounting.mako",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )
    config.add_tree_view(
        CancelInvoiceFilesView,
        parent=BusinessOverviewView,
        layout="cancelinvoice",
        renderer="tasks/files.mako",
        permission=PERMISSIONS["company.view"],
        context=CancelInvoice,
    )
