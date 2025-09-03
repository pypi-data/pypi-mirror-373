import os
from caerp.forms.admin import get_config_schema
from caerp.consts.permissions import PERMISSIONS
from .numbers import (
    SalesNumberingConfigView,
    SALE_NUMBERING_CONFIG_URL,
    SaleNumberingIndex,
)

INTERNAL_INVOICE_NUMBERING_URL = os.path.join(
    SALE_NUMBERING_CONFIG_URL, "internalinvoice"
)


class SalesInternalNumberingConfigView(SalesNumberingConfigView):
    title = "Numérotation des factures internes"
    description = (
        "Configurer la manière dont sont numérotées les factures " "internes à la CAE"
    )

    route_name = INTERNAL_INVOICE_NUMBERING_URL

    keys = (
        "internalinvoice_number_template",
        "global_internalinvoice_sequence_init_value",
        "year_internalinvoice_sequence_init_value",
        "year_internalinvoice_sequence_init_date",
        "month_internalinvoice_sequence_init_value",
        "month_internalinvoice_sequence_init_date",
    )

    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_accounting"]


def add_routes(config):
    config.add_route(INTERNAL_INVOICE_NUMBERING_URL, INTERNAL_INVOICE_NUMBERING_URL)


def includeme(config):
    add_routes(config)
    config.add_admin_view(
        SalesInternalNumberingConfigView,
        parent=SaleNumberingIndex,
    )
