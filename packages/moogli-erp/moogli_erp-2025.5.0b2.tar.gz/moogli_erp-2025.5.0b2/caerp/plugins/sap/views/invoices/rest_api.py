from caerp.consts.permissions import PERMISSIONS
from caerp.models.task.invoice import Invoice
from caerp.views.invoices.rest_api import (
    CancelInvoiceRestView,
    InvoiceRestView,
    InvoiceStatusRestView,
)

from ..mixins import SAPTaskRestViewMixin
from ...forms.tasks.invoice import validate_sap_invoice


class SAPInvoiceStatusRestView(InvoiceStatusRestView):
    # backend validation
    validation_function = staticmethod(validate_sap_invoice)


class SAPInvoiceRestView(SAPTaskRestViewMixin, InvoiceRestView):
    def _more_form_sections(self, sections):
        sections = InvoiceRestView._more_form_sections(self, sections)
        sections["composition"]["classic"]["lines"]["date"] = {"edit": True}
        # On cache les options d'affichage (obligatoires pour le SAP)
        sections["display_options"] = {}
        return sections


class SAPCancelInvoiceRestView(SAPTaskRestViewMixin, CancelInvoiceRestView):
    def _more_form_sections(self, sections):
        sections = CancelInvoiceRestView._more_form_sections(self, sections)
        sections["composition"]["classic"]["lines"]["date"] = {"edit": True}
        sections["display_options"] = {}
        return sections


def add_invoice_views(config):
    # Status View
    config.add_view(
        SAPInvoiceStatusRestView,
        route_name="/api/v1/invoices/{id}",
        request_param="action=status",
        permission=PERMISSIONS["context.edit_invoice"],
        request_method="POST",
        renderer="json",
        context=Invoice,
    )

    config.add_view(
        SAPInvoiceRestView,
        attr="form_config",
        route_name="/api/v1/invoices/{id}",
        renderer="json",
        request_param="form_config",
        permission=PERMISSIONS["company.view"],
        context=Invoice,
    )


def add_cancelinvoice_views(config):
    config.add_view(
        SAPCancelInvoiceRestView,
        attr="form_config",
        route_name="/api/v1/cancelinvoices/{id}",
        renderer="json",
        request_param="form_config",
        permission=PERMISSIONS["company.view"],
    )


def includeme(config):
    add_invoice_views(config)
    add_cancelinvoice_views(config)
