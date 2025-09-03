import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.tools import (
    BaseConfigView,
)
from caerp.forms.admin import (
    get_config_schema,
)
from caerp.views.admin.expense import (
    EXPENSE_URL,
    ExpenseIndexView,
)


EXPENSE_ACCOUNTING_URL = os.path.join(EXPENSE_URL, "accounting")
EXPENSE_PAYMENT_ACCOUNTING_URL = os.path.join(EXPENSE_URL, "payment_accounting")

EXPENSE_INFO_MESSAGE = """
<h4>Variables utilisables dans les gabarits de libellés</h4>\
    <p>Il est possible de personaliser les libellés comptables à l'aide d'un gabarit. Plusieurs variables sont disponibles :</p>\
    <ul>\
    <li><code>{beneficiaire}</code> : nom/prénoms de la personne ayant avancé les frais</li>\
    <li><code>{beneficiaire_LASTNAME}</code> : nom, en capitales, de la personne ayant avancé les frais</li>\
    <li><code>{code_compta}</code> : code analytique de l'enseigne concernée</li>\
    <li><code>{titre}</code> : titre de la note de dépenses (si renseigné)</li>\
    <li>\
        <code>{expense_date}</code> : date de la note de dépenses, qu'il est posisble de formatter de différentes manières :\
        <ul>\
        <li><code>{expense_date:%-m %Y}</code> : produira <code>6 2017</code> pour Juin 2017</li>\
        <li><code>{expense_date:%-m/%Y}</code> : produira <code>6/2017</code> pour Juin 2017</li>\
        <li><code>{expense_date:%m/%Y}</code> : produira <code>06/2017</code> pour Juin 2017</li>\
        </ul>\
    </li>\
    </ul>

    <p><strong>Si le dégroupage de l'export des notes de dépenses est activé</strong>, sont également disponibles :
    </p>\

    <ul>\
        <li>\
         <code>{expense_description}</code> : \
         description de la dépense telle que saisie par l'entrepreneur
        </li>\
        <li>\
          <code>{supplier_label}</code> : \
          nom du fournisseur tel que saisi par l'entrepreneur, si renseigné
        </li>\
        <li>\
          <code>{invoice_number}</code> : \
          numéro de facture, tel que saisi par l'entrepreneur, si renseigné
        </li>\
    </ul>\

    <p>NB : Penser à séparer les variables, par exemple par des espaces, sous peine de libellés peu lisibles.</p>\
    """


class ExpenseAccountingView(BaseConfigView):
    title = "Export comptable des notes de dépenses"
    route_name = EXPENSE_ACCOUNTING_URL
    keys = (
        "bookentry_expense_label_template",
        "code_journal_ndf",
        "compte_cg_ndf",
        "ungroup_expenses_ndf",
    )
    schema = get_config_schema(keys)
    validation_msg = "L'export comptable des notes de dépenses a bien été \
configuré"
    redirect_route_name = EXPENSE_URL
    info_message = EXPENSE_INFO_MESSAGE
    permission = PERMISSIONS["global.config_accounting"]


class ExpensePaymentAccountingView(BaseConfigView):
    title = "Export comptable des décaissements \
(paiement des notes de dépenses)"
    route_name = EXPENSE_PAYMENT_ACCOUNTING_URL
    keys = (
        "bookentry_expense_payment_main_label_template",
        "bookentry_expense_payment_waiver_label_template",
        "code_journal_waiver_ndf",
        "compte_cg_waiver_ndf",
        "code_tva_ndf",
    )
    schema = get_config_schema(keys)
    validation_msg = "L'export comptable des décaissements a bien été \
configuré"
    redirect_route_name = EXPENSE_URL
    info_message = EXPENSE_INFO_MESSAGE
    permission = PERMISSIONS["global.config_accounting"]


def includeme(config):
    config.add_route(EXPENSE_ACCOUNTING_URL, EXPENSE_ACCOUNTING_URL)
    config.add_route(EXPENSE_PAYMENT_ACCOUNTING_URL, EXPENSE_PAYMENT_ACCOUNTING_URL)
    config.add_admin_view(
        ExpenseAccountingView,
        parent=ExpenseIndexView,
    )
    config.add_admin_view(
        ExpensePaymentAccountingView,
        parent=ExpenseIndexView,
    )
