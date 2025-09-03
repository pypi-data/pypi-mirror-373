import os
import logging
from caerp.views.admin import (
    AdminIndexView,
    BASE_URL as BASE_ROUTE,
)
from caerp.views.admin.tools import BaseAdminIndexView

MAIN_ROUTE = os.path.join(BASE_ROUTE, "main")

logger = logging.getLogger(__name__)


class MainIndexView(BaseAdminIndexView):
    route_name = MAIN_ROUTE
    title = "Configuration générale"
    description = "Configurer les informations générales (message d'accueil, \
types de fichier, e-mail de contact, signatures numérisées)"


def includeme(config):
    config.add_route(MAIN_ROUTE, MAIN_ROUTE)
    config.add_admin_view(MainIndexView, parent=AdminIndexView)
    config.include(".cae")
    config.include(".site")
    config.include(".contact")
    config.include(".file_types")
    config.include(".digital_signatures")
    config.include(".companies")
    config.include(".cae_places")
    config.include(".roles")
    config.include(".rgpd")
    config.include(".smtp")
