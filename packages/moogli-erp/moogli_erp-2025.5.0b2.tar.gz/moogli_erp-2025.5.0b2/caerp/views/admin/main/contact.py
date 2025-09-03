"""
View related to admin configuration
"""
import logging
import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import (
    BaseConfigView,
)
from caerp.views.admin.main import (
    MainIndexView,
    MAIN_ROUTE,
)

MAIN_CONTACT_ROUTE = os.path.join(MAIN_ROUTE, "contact")


logger = logging.getLogger(__name__)


class AdminContactView(BaseConfigView):
    """
    Admin welcome page
    """

    title = "Adresse e-mail de contact MoOGLi"
    description = "Configurer l'adresse utilisée par MoOGLi pour vous \
envoyer des messages (traitement des fichiers…)"

    route_name = MAIN_CONTACT_ROUTE
    keys = ("cae_admin_mail",)
    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_cae"]


def includeme(config):
    config.add_route(MAIN_CONTACT_ROUTE, MAIN_CONTACT_ROUTE)
    config.add_admin_view(
        AdminContactView,
        parent=MainIndexView,
    )
