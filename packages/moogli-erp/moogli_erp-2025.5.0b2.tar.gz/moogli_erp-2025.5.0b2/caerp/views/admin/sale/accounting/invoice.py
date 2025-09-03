import os

import logging
from deform_extensions import GridFormWidget

from caerp.consts.permissions import PERMISSIONS
from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule
from caerp.forms.admin import get_config_schema

from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminDisableView,
    BaseAdminDeleteView,
    BaseAdminEditView,
    BaseAdminAddView,
    BaseAdminIndexView,
    BaseConfigView,
)
from caerp.views.admin.sale.accounting import (
    ACCOUNTING_INDEX_URL,
    SaleAccountingIndex,
)
from caerp.views.render_api import format_float
from caerp.forms.admin.sale.bookeeping import (
    get_admin_book_entry_schema,
)
from caerp.utils.widgets import Link, POSTButton


logger = logging.getLogger(__name__)
INDEX_URL = os.path.join(ACCOUNTING_INDEX_URL, "invoice")
CONFIG_URL = os.path.join(INDEX_URL, "config")

MODULE_COLLECTION_URL = os.path.join(INDEX_URL, "modules")
MODULE_ITEM_URL = os.path.join(MODULE_COLLECTION_URL, "{id}")


class IndexView(BaseAdminIndexView):
    title = "Factures"
    description = "Configurer les écritures des factures de vente"
    route_name = INDEX_URL
    permission = PERMISSIONS["global.config_accounting"]


class ConfigView(BaseConfigView):
    """
    Cae information configuration
    """

    title = "Informations générales et modules prédéfinis"
    description = (
        "Configuration du code journal et des modules prédéfinis (Export des"
        " factures, RG Externe, RG Interne)"
    )
    route_name = CONFIG_URL

    validation_msg = "Les informations ont bien été enregistrées"
    keys = (
        "code_journal",
        "numero_analytique",
        "compte_frais_annexes",
        "compte_cg_banque",
        "bookentry_facturation_label_template",
        "cae_general_customer_account",
        "cae_third_party_customer_account",
        "compte_rrr",
        "compte_cg_tva_rrr",
        "code_tva_rrr",
        "compte_rg_interne",
        "taux_rg_interne",
        "compte_rg_externe",
        "taux_rg_client",
        "bookentry_rg_interne_label_template",
        "bookentry_rg_client_label_template",
        "sage_facturation_not_used",
        "sage_rginterne",
        "sage_rgclient",
    )
    schema = get_config_schema(keys)
    info_message = """Configurez les exports comptables de votre CAE.</br >
<h4>Champs indispensables aux exports</h4>\
    <ul>\
        <li>Code journal</li>\
        <li>Numéro analytique de la CAE</li>\
        <li>Compte banque de l'entrepreneur</li>\
    </ul>
<h4>Champs relatifs aux frais et remises</h4>\
    <ul>\
      <li>Compte de frais annexes</li>\
      <li>Compte RRR (Rabais, Remises et Ristournes)</li>\
    </ul>
<h4>Configurez et activez des modules de retenues optionnels</h4>\
        <ul>\
    <li>Module RG Externe (spécifique bâtiment)</li>\
    <li>Module RG Interne (spécifique bâtiment)</li>\
    </ul>
<h4>Variables utilisables dans les gabarits de libellés</h4>\
    <p>Il est possible de personaliser les libellés comptables à l'aide d'un\
    gabarit. Plusieurs variables sont disponibles :</p>\
    <ul>\
      <li><code>{invoice.customer.label}</code> : nom du client facturé</li>\
      <li><code>{invoice.customer.code}</code> : code du client facturé</li>\
      <li><code>{company.code_compta}</code> : code analytique \
      de l'enseigne établissant la facture</li>\
      <li><code>{invoice.official_number}</code> : numéro de facture \
      (pour tronquer à 9 caractères : \
      <code>{invoice.official_number:.9}</code>)</li>\
      <li><code>{company.name}</code> : nom de l'enseigne établissant \
      la facture</li>\
    </ul>\
    <p>NB : Penser à séparer les variables, par exemple par des espaces, \
    sous peine de libellés peu lisibles.</p>\
    """
    permission = PERMISSIONS["global.config_accounting"]


class ModuleListView(AdminCrudListView):
    title = "Module de contribution"
    description = "Configuration des modules de contribution"
    route_name = MODULE_COLLECTION_URL
    item_route_name = MODULE_ITEM_URL
    columns = ["Nom du module", "Taux", "Provision ?", "Actif"]
    factory = CustomInvoiceBookEntryModule
    doctype = "invoice"
    permission = PERMISSIONS["global.config_accounting"]

    @property
    def help_msg(self):
        return """
            Configurer des écritures personnalisées pour les exports
 de factures
        """

    def stream_columns(self, item):
        title = item.title
        if not item.custom:
            icon = self.get_icon("lock")
            title += " (Créé par MoOGLi {})".format(icon)
        yield title
        yield "{} %".format(format_float(item.percentage))
        if item.is_provision:
            yield self.get_icon("check")
        else:
            yield self.get_icon("times")
        if item.enabled:
            yield self.get_icon("check")
        else:
            yield self.get_icon("times")

    def stream_actions(self, item):
        yield Link(self._get_item_url(item), "Voir/Modifier", icon="pen", css="icon")
        if item.enabled:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Désactiver",
                title=(
                    "Ces écritures ne seront pas produites lors des "
                    "exports comptables"
                ),
                icon="times",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Activer",
                title=("Ces écritures seront produites lors des exports" " comptables"),
                icon="check",
                css="icon",
            )

        if not item.enabled and item.custom:
            yield POSTButton(
                self._get_item_url(item, action="delete"),
                "Supprimer",
                icon="trash-alt",
                css="icon negative",
            )

    def load_items(self):
        """
        Return the sqlalchemy models representing current queried elements
        :rtype: SQLAlchemy.Query object
        """
        return (
            self.factory.query()
            .filter_by(active=True)
            .filter_by(doctype=self.doctype)
            .order_by(getattr(self.factory, "enabled").desc())
            .all()
        )

    def more_template_vars(self, result):
        result["help_msg"] = self.help_msg
        return result


MODULE_GRID = (
    (("title", 12),),
    (
        ("compte_cg_debit", 6),
        ("compte_cg_credit", 6),
    ),
    (("percentage", 6),),
    (("label_template", 12),),
    (("is_provision", 12),),
    (("enabled", 12),),
)


class ModuleAddView(BaseAdminAddView):
    route_name = MODULE_COLLECTION_URL
    factory = CustomInvoiceBookEntryModule
    schema = get_admin_book_entry_schema()
    help_msg = factory.help_msg
    doctype = "invoice"
    permission = PERMISSIONS["global.config_accounting"]

    def before(self, form):
        """
        Launched before the form is used

        :param obj form: The form object
        """
        pre_filled = {"doctype": self.doctype}
        form.set_appstruct(pre_filled)
        form.widget = GridFormWidget(named_grid=MODULE_GRID)


class ModuleEditView(BaseAdminEditView):
    route_name = MODULE_ITEM_URL
    factory = CustomInvoiceBookEntryModule
    schema = get_admin_book_entry_schema()

    help_msg = factory.help_msg
    permission = PERMISSIONS["global.config_accounting"]

    def before(self, form):
        super(ModuleEditView, self).before(form)
        form.widget = GridFormWidget(named_grid=MODULE_GRID)

    @property
    def title(self):
        return "Modifier le module '{0}'".format(self.context.title)


class ModuleDisableView(BaseAdminDisableView):
    """
    View for CustomInvoiceBookEntryModule disable/enable
    """

    active_key = "enabled"
    route_name = MODULE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class ModuleDeleteView(BaseAdminDeleteView):
    """
    CustomInvoiceBookEntryModule deletion view
    """

    route_name = MODULE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


def add_routes(config):
    config.add_route(INDEX_URL, INDEX_URL)
    config.add_route(CONFIG_URL, CONFIG_URL)
    config.add_route(MODULE_COLLECTION_URL, MODULE_COLLECTION_URL)
    config.add_route(
        MODULE_ITEM_URL,
        MODULE_ITEM_URL,
        traverse="/custom_invoice_book_entry_modules/{id}",
    )


def includeme(config):
    add_routes(config)
    config.add_admin_view(IndexView, parent=SaleAccountingIndex)
    config.add_admin_view(ConfigView, parent=IndexView)
    config.add_admin_view(
        ModuleListView,
        parent=IndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        ModuleAddView,
        parent=ModuleListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        ModuleEditView,
        parent=ModuleListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ModuleDisableView,
        parent=ModuleListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        ModuleDeleteView,
        parent=ModuleListView,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )
