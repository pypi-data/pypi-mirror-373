import os
import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.main import (
    MainIndexView,
    MAIN_ROUTE,
)

RGPD_ROUTE = os.path.join(MAIN_ROUTE, "rgpd")

logger = logging.getLogger(__name__)


class AdminRGPDView(BaseConfigView):
    title = "Conformité au RGPD"
    description = (
        "Configurer l’adresse mail du correspondant RGPD et les durées de rétention "
        "des données prévues par votre charte RGPD."
    )
    info_message = (
        "<p>Configurer ici les durées de rétention des données personnelles "
        "et l’adresse mail du correspondant RGPD de votre entreprise. </p>"
        "<br />"
        "Un automate vérifie une fois par semaine :"
        "<ul>"
        "<li>Si un compte est encore actif alors qu’il n’est pas utilisé;</li>"
        "<li>Si des données de gestion sociale devraient être anonymisées;</li>"
        "<li>Si des données de clients particuliers devraient être anonymisées.</li>"
        "</ul><br />"
        "<p>Pour chacun de ces trois points, si des données sont conservées "
        "au-delà des délais prévus, l’automate envoie un e-mail de notification "
        " contenant un lien vers les différents éléments concernés.</p><br/>"
        "<strong>NB</strong> : L’automate ne supprime et ne modifie aucune donnée au "
        "sein de l’application."
    )
    route_name = RGPD_ROUTE
    keys = (
        "rgpd_manager_email",
        "rgpd_accounts_retention_days",
        "rgpd_userdatas_retention_days",
        "rgpd_customers_retention_days",
    )
    permission = PERMISSIONS["global.rgpd_management"]

    def get_schema(self):
        return get_config_schema(self.keys)


def includeme(config):
    config.add_route(RGPD_ROUTE, RGPD_ROUTE)
    config.add_admin_view(
        AdminRGPDView,
        parent=MainIndexView,
    )
