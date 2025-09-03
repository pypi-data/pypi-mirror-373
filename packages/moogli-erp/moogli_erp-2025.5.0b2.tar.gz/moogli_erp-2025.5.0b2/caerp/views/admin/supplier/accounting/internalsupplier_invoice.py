import os
import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.supplier.accounting import (
    SUPPLIER_ACCOUNTING_URL,
    SUPPLIER_INFO_MESSAGE,
    SupplierAccountingIndex,
)

logger = logging.getLogger(__name__)
CONFIG_URL = os.path.join(SUPPLIER_ACCOUNTING_URL, "internalinvoice")


class InternalSupplierAccountingConfigView(BaseConfigView):
    title = "Module Fournisseur interne"
    description = "Configurer la génération des écritures Fournisseur interne"
    route_name = CONFIG_URL

    validation_msg = "Les informations ont bien été enregistrées"
    keys = [
        "internalcae_general_supplier_account",
        "internalcae_third_party_supplier_account",
        "internalcode_journal_frns",
        "internalbookentry_supplier_invoice_label_template",
        "internalcode_journal_paiements_frns",
        "internalbookentry_supplier_payment_label_template",
    ]
    schema = get_config_schema(keys)
    info_message = SUPPLIER_INFO_MESSAGE
    permission = PERMISSIONS["global.config_accounting"]


def add_routes(config):
    config.add_route(CONFIG_URL, CONFIG_URL)


def includeme(config):
    add_routes(config)
    config.add_admin_view(
        InternalSupplierAccountingConfigView,
        parent=SupplierAccountingIndex,
    )
