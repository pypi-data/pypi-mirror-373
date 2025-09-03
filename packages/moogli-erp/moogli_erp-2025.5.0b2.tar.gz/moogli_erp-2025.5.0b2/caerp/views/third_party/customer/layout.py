import logging
from caerp.consts.permissions import PERMISSIONS
from caerp.services.rgpd.customer import check_customer_expired
from caerp.utils.menu import (
    MenuItem,
    Menu,
)
from caerp.default_layouts import DefaultLayout
from caerp.utils.widgets import Link, POSTButton
from caerp.views.company.routes import (
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_INVOICE_ADD_ROUTE,
)
from .routes import (
    CUSTOMER_ITEM_BUSINESS_ROUTE,
    CUSTOMER_ITEM_ESTIMATION_ROUTE,
    CUSTOMER_ITEM_RGPD_CLEAN_ROUTE,
    CUSTOMER_ITEM_ROUTE,
    CUSTOMER_ITEM_INVOICE_ROUTE,
    CUSTOMER_ITEM_EXPENSES_ROUTE,
)


logger = logging.getLogger(__name__)


CustomerMenu = Menu(name="customermenu")


CustomerMenu.add(
    MenuItem(
        name="customer_general",
        label="Informations",
        title="Informations générales",
        route_name=CUSTOMER_ITEM_ROUTE,
        icon="info-circle",
    )
)


def deferred_permission(menu_item, kw):
    """
    Permet d'afficher ou masquer l'onglet "Affaires" via les permissions
    selon si le client a des affaires visibles ou pas
    """
    return kw["request"].context.has_visible_businesses()


CustomerMenu.add(
    MenuItem(
        name="customer_businesses",
        label="Affaires",
        title="Liste des affaires de ce client",
        route_name=CUSTOMER_ITEM_BUSINESS_ROUTE,
        icon="list-alt",
        perm=deferred_permission,
    )
)

CustomerMenu.add(
    MenuItem(
        name="customer_estimations",
        label="Devis",
        title="Liste des devis de ce client",
        route_name=CUSTOMER_ITEM_ESTIMATION_ROUTE,
        icon="file-list",
        perm=PERMISSIONS["company.view"],
    )
)

CustomerMenu.add(
    MenuItem(
        name="customer_invoices",
        label="Factures",
        title="Liste des factures de ce client",
        route_name=CUSTOMER_ITEM_INVOICE_ROUTE,
        icon="file-invoice-euro",
        perm=PERMISSIONS["company.view"],
    )
)

CustomerMenu.add(
    MenuItem(
        name="expenses",
        label="Achats liés",
        route_name=CUSTOMER_ITEM_EXPENSES_ROUTE,
        icon="box",
        perm=PERMISSIONS["company.view"],
    )
)


class Layout(DefaultLayout):
    """
    Layout for customer related pages

    Provide the main page structure for customer view
    """

    def __init__(self, context, request):
        DefaultLayout.__init__(self, context, request)
        self.current_customer_object = context

    @property
    def edit_url(self):
        return self.request.route_path(
            CUSTOMER_ITEM_ROUTE,
            id=self.current_customer_object.id,
            _query={"action": "edit"},
        )

    @property
    def details_url(self):
        return self.request.route_path(
            CUSTOMER_ITEM_ROUTE,
            id=self.current_customer_object.id,
        )

    @property
    def rgpd_clean_url(self):
        return self.request.route_path(
            CUSTOMER_ITEM_RGPD_CLEAN_ROUTE,
            id=self.current_customer_object.id,
        )

    @property
    def menu(self):
        CustomerMenu.set_current(self.current_customer_object)
        CustomerMenu.bind(current=self.current_customer_object)
        return CustomerMenu

    def stream_main_actions(self):
        if self.request.has_permission(PERMISSIONS["context.add_estimation"]):
            yield Link(
                self.request.route_path(
                    COMPANY_ESTIMATION_ADD_ROUTE,
                    id=self.context.company_id,
                    _query={"customer_id": self.context.id},
                ),
                "Devis",
                title="Créer un devis pour ce client",
                icon="file-list",
                css="btn btn-primary",
            )
        if self.request.has_permission(PERMISSIONS["context.add_invoice"]):
            yield Link(
                self.request.route_path(
                    COMPANY_INVOICE_ADD_ROUTE,
                    id=self.context.company_id,
                    _query={"customer_id": self.context.id},
                ),
                "Facture",
                title="Créer une facture pour ce client",
                icon="file-invoice-euro",
                css="btn btn-primary",
            )

    def stream_other_actions(self):
        yield Link(
            self.request.route_path(
                CUSTOMER_ITEM_ROUTE,
                id=self.context.id,
                _query={"action": "edit"},
            ),
            "",
            title="Modifier",
            icon="pen",
            css="btn",
        )
        if self.request.has_permission(PERMISSIONS["context.delete_customer"]):
            yield POSTButton(
                self.request.route_path(
                    CUSTOMER_ITEM_ROUTE,
                    id=self.context.id,
                    _query=dict(action="delete"),
                ),
                "Supprimer",
                title="Supprimer définitivement ce client",
                icon="trash-alt",
                css="negative",
                confirm="Êtes-vous sûr de vouloir supprimer ce client ?",
            )
        elif self.request.has_permission(PERMISSIONS["context.edit_customer"]):
            if self.context.archived:
                label = "Désarchiver"
                css = ""
            else:
                label = "Archiver"
                css = "negative"

            yield POSTButton(
                self.request.route_path(
                    CUSTOMER_ITEM_ROUTE,
                    id=self.context.id,
                    _query=dict(action="archive"),
                ),
                "",
                title=f"{label} ce client",
                icon="archive",
                css=css,
            )
        # TODO : est-ce qu'on définit une permission spécifique pour cette action?
        if self.request.context.type == "individual":
            if self.request.has_permission(
                PERMISSIONS["global.rgpd_management"]
            ) and check_customer_expired(self.request, self.request.context.id):
                yield Link(
                    self.rgpd_clean_url,
                    "[RGPD] : Anonymiser",
                    title="Supprimer les informations personnelles et anonymiser "
                    "ce client",
                    icon="mask",
                    css="btn negative",
                )


def includeme(config):
    config.add_layout(
        Layout,
        template="caerp:templates/customers/layout.mako",
        name="customer",
    )
