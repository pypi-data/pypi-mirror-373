import os

from caerp.consts.permissions import PERMISSIONS

from caerp.forms.admin import get_config_schema
from caerp.models.payments import (
    PaymentMode,
    BankAccount,
    Bank,
)
from caerp.views.admin.tools import (
    get_model_admin_view,
    BaseConfigView,
    BaseAdminIndexView,
)
from . import (
    ACCOUNTING_INDEX_URL,
    SaleAccountingIndex,
)

RECEIPT_URL = os.path.join(ACCOUNTING_INDEX_URL, "receipts")
RECEIPT_CONFIG_URL = os.path.join(RECEIPT_URL, "config")


class ReceiptIndexView(BaseAdminIndexView):
    title = "Comptabilité : Encaissements"
    description = "Configurer les exports comptables, les comptes bancaires \
de la CAE, et les banques des clients"
    route_name = RECEIPT_URL
    permission = PERMISSIONS["global.config_accounting"]


class MainReceiptConfig(BaseConfigView):
    title = "Informations générales"
    route_name = RECEIPT_CONFIG_URL

    keys = (
        "receipts_active_tva_module",
        "receipts_grouping_strategy",
        "bookentry_payment_label_template",
        "internalcode_journal_encaissement",
        "internalbank_general_account",
        "internalbookentry_payment_label_template",
    )
    schema = get_config_schema(keys)
    validation_msg = "L'export comptable des encaissement a bien été \
configuré"
    info_message = """\
  Configurer l'export des encaissements (le code journal\
  utilisé est celui de la banque associé à chaque encaissement)\
<br/ >\
<h4>Variables utilisables dans les gabarits de libellés</h4>\
    <p>Il est possible de personaliser les libellés comptables à l'aide \
    d'un gabarit. Plusieurs variables sont disponibles :</p>\
    <ul>\
    <li><code>{invoice.customer.label}</code> : nom du client émetteur du \
    paiement</li>\
    <li><code>{invoice.customer.code}</code> : code du client émetteur du \
    paiement</li>\
    <li><code>{invoice.official_number}</code> : numéro de facture (pour \
    tronquer à 9 caractères : <code>{invoice.official_number:.9}</code>)</li>\
    <li><code>{company.name}</code> : nom de l'enseigne destinataire du \
    paiement</li>\
    <li><code>{company.code_compta}</code> : code analytique de l'enseigne \
    destinataire du paiement</li>\
    <li><code>{payment.bank_remittance_id}</code> : identifiant de la remise \
    en banque</li>\
    </ul>
    <p>NB : Penser à séparer les variables, par exemple par des espaces, \
    sous peine de libellés peu lisibles.</p>\
"""
    permission = PERMISSIONS["global.config_accounting"]


PaymentModeAdminView = get_model_admin_view(
    PaymentMode,
    r_path=RECEIPT_URL,
    can_disable=False,
    permission=PERMISSIONS["global.config_accounting"],
)

BankAdminView = get_model_admin_view(
    Bank, r_path=RECEIPT_URL, permission=PERMISSIONS["global.config_accounting"]
)

BankAccountAdminView = get_model_admin_view(
    BankAccount, r_path=RECEIPT_URL, permission=PERMISSIONS["global.config_accounting"]
)


def add_routes(config):
    config.add_route(RECEIPT_URL, RECEIPT_URL)
    config.add_route(RECEIPT_CONFIG_URL, RECEIPT_CONFIG_URL)
    for view in PaymentModeAdminView, BankAdminView, BankAccountAdminView:
        config.add_route(view.route_name, view.route_name)


def add_views(config):
    config.add_admin_view(
        ReceiptIndexView,
        parent=SaleAccountingIndex,
    )
    for view in (
        MainReceiptConfig,
        PaymentModeAdminView,
        BankAdminView,
        BankAccountAdminView,
    ):
        config.add_admin_view(
            view,
            parent=ReceiptIndexView,
        )


def includeme(config):
    add_routes(config)
    add_views(config)
