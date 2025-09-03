"""
Entry point for sap-plugin specific stuff

SAP stands for "Service à la Personne"
"""
import caerp
from caerp.utils.menu import (
    AppMenuDropDown,
    AppMenuItem,
)


def hack_admin_menu(config):
    config.registry.admin_menu.add(
        AppMenuDropDown(order=3, name="sap", label="Services à la personne")
    )
    config.registry.admin_menu.add(
        AppMenuItem(
            order=1,
            label="Attestations fiscales",
            route_name="/sap/attestations",
            route_id_key="user_id",
        ),
        "sap",
    )
    config.registry.admin_menu.add(
        AppMenuItem(
            order=1,
            label="Stats nova",
            route_name="/sap/nova",
            route_id_key="user_id",
        ),
        "sap",
    )


def includeme(config):
    config.include(".populate")
    config.include(".models")
    config.include(".panels")
    # Ugly
    # add_view fails in an hard to debug way within testing context.
    if not caerp._called_from_test:
        hack_admin_menu(config)
        config.include(".views.invoices.rest_api")
        config.include(".views.estimations.rest_api")
        config.include(".views.payment")
        config.include(".views.attestation")
        config.include(".views.nova")
        config.include(".views.admin.sap")
