import os
import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema

from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.sale.accounting import (
    ACCOUNTING_INDEX_URL,
    SaleAccountingIndex,
)

logger = logging.getLogger(__name__)
CONFIG_URL = os.path.join(ACCOUNTING_INDEX_URL, "common")


class ConfigView(BaseConfigView):
    """
    Cae information configuration
    """

    title = "Commun Factures / Factures internes"
    description = "Configurer les écritures d'export des ventes"
    route_name = CONFIG_URL

    keys = (
        "bookentry_sales_group_customer_entries",
        "bookentry_sales_customer_account_by_tva",
    )
    schema = get_config_schema(keys)
    info_message = ""
    permission = PERMISSIONS["global.config_accounting"]


def add_routes(config):
    config.add_route(CONFIG_URL, CONFIG_URL)


def includeme(config):
    add_routes(config)
    config.add_admin_view(
        ConfigView,
        parent=SaleAccountingIndex,
    )
