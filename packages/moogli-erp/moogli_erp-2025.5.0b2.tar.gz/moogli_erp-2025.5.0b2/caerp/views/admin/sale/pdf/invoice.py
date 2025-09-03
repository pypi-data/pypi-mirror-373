import os
from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.sale.pdf import (
    PdfIndexView,
    PDF_URL,
)

INVOICE_ROUTE = os.path.join(PDF_URL, "invoice")


class InvoiceConfigView(BaseConfigView):
    title = "Informations spécifiques aux factures"
    description = "Configurer les champs spécifiques aux factures dans les \
sorties PDF"
    keys = ["coop_invoiceheader"]
    schema = get_config_schema(keys)
    validation_msg = "Vos modifications ont été enregistrées"
    route_name = INVOICE_ROUTE
    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    config.add_route(INVOICE_ROUTE, INVOICE_ROUTE)
    config.add_admin_view(
        InvoiceConfigView,
        parent=PdfIndexView,
    )
