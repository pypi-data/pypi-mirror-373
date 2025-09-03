"""
    Manage view :
        - last documents page
"""
import logging

from collections import namedtuple

from caerp.resources import dashboard_resources
from caerp.consts.permissions import PERMISSIONS


log = logging.getLogger(__name__)

ShortcutButton = namedtuple("ShortcutButton", ["url", "icon", "text", "title"])


def _get_validation_shortcuts(request) -> list:
    """
    Collect shortcuts for the company dashboard
    """
    buttons = []
    if request.has_permission(PERMISSIONS["global.validate_estimation"]):
        buttons.append(
            ShortcutButton(
                url="validation/estimations",
                icon="file-list",
                text="Devis",
                title="Voir les devis en attente de validation",
            )
        )
    if request.has_permission(PERMISSIONS["global.validate_invoice"]):
        buttons.append(
            ShortcutButton(
                url="validation/invoices",
                icon="file-invoice-euro",
                text="Factures",
                title="Voir les factures en attente de validation",
            )
        )
    if request.has_permission(PERMISSIONS["global.list_supplier_orders"]):
        buttons.append(
            ShortcutButton(
                url="validation/supplier_orders",
                icon="box",
                text="Commandes fournisseurs",
                title="Voir les commandes fournisseurs en attente de validation",
            )
        )
    if request.has_permission(PERMISSIONS["global.list_supplier_invoices"]):
        buttons.append(
            ShortcutButton(
                url="validation/supplier_invoices",
                icon="box-euro",
                text="Factures fournisseurs",
                title="Voir les factures fournisseurs en attente de validation",
            )
        )
    if request.has_permission(PERMISSIONS["global.list_expenses"]):
        buttons.append(
            ShortcutButton(
                url="validation/expenses",
                icon="credit-card",
                text="Notes de dépense",
                title="Voir les notes de dépense en attente de validation",
            )
        )

    return buttons


def manage(request):
    """
    The manage view
    """
    dashboard_resources.need()
    shortcuts = _get_validation_shortcuts(request)
    return dict(
        title="Mon tableau de bord",
        shortcuts=shortcuts,
    )


def includeme(config):
    config.add_route("manage", "/manage")
    config.add_view(
        manage,
        route_name="manage",
        renderer="manage.mako",
        permission=PERMISSIONS["global.access_ea"],
    )
