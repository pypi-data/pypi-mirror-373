import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import (
    BaseConfigView,
    BaseAdminIndexView,
)

from . import (
    ACCOUNTING_INDEX_URL,
    SaleAccountingIndex,
)


SALE_NUMBERING_CONFIG_URL = os.path.join(ACCOUNTING_INDEX_URL, "numbering")
INVOICE_NUMBERING_URL = os.path.join(SALE_NUMBERING_CONFIG_URL, "invoice")


class SaleNumberingIndex(BaseAdminIndexView):
    title = "Comptabilité : Numérotation des factures"
    description = "Configurer la numérotation des différents type de facture"
    route_name = SALE_NUMBERING_CONFIG_URL
    permission = PERMISSIONS["global.config_accounting"]


class SalesNumberingConfigView(BaseConfigView):
    title = "Numérotation des factures"
    description = "Configurer la manière dont sont numérotées les factures"

    route_name = INVOICE_NUMBERING_URL

    validation_msg = "Les informations ont bien été enregistrées"

    keys = (
        "invoice_number_template",
        "allow_unchronological_invoice_sequence",
        "global_invoice_sequence_init_value",
        "year_invoice_sequence_init_value",
        "year_invoice_sequence_init_date",
        "month_invoice_sequence_init_value",
        "month_invoice_sequence_init_date",
    )

    schema = get_config_schema(keys)

    info_message = """Il est possible de personaliser le gabarit du numéro \
    de facture.<br/ >\
<p>Plusieurs variables et séquences chronologiques sont à disposition.</p>\
<h4>Variables :</h4>\
<ul>\
<li><code>{YYYY}</code> : année, sur 4 digits</li>\
<li><code>{YY}</code> : année, sur 2 digits</li>\
<li><code>{MM}</code> : mois, sur 2 digits</li>\
<li><code>{ANA}</code> : code analytique de l'enseigne</li>\
</ul>\
<h4>Numéros de séquence :</h4>\
<ul>\
<li><code>{SEQGLOBAL}</code> : numéro de séquence global (aucun ràz)</li>\
<li><code>{SEQYEAR}</code> : numéro de séquence annuel (ràz chaque année)</li>\
<li>\
<code>{SEQMONTH}</code> : numéro de séquence mensuel (ràz chaque mois)\
</li>\
<li>\
<code>{SEQMONTHANA}</code>: numéro de séquence par enseigne et par mois \
(ràz chaque mois)</li>\
</ul>\
<br/ >\
<p>Dans le cas d'une migration depuis un autre outil de gestion, il est possible \
d'initialiser les séquences à une valeur différente de zéro.</p>\
<p>La valeur définie ici correspond à la dernière déjà utilisée, \
la numérotation reprendra au numéro suivant.</p>\
    """
    permission = PERMISSIONS["global.config_accounting"]


def add_routes(config):
    config.add_route(SALE_NUMBERING_CONFIG_URL, SALE_NUMBERING_CONFIG_URL)
    config.add_route(INVOICE_NUMBERING_URL, INVOICE_NUMBERING_URL)


def includeme(config):
    add_routes(config)
    config.add_admin_view(
        SaleNumberingIndex,
        parent=SaleAccountingIndex,
    )
    config.add_admin_view(
        SalesNumberingConfigView,
        parent=SaleNumberingIndex,
    )
