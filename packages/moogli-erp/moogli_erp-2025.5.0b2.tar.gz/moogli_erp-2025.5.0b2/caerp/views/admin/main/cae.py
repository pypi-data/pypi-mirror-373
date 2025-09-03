"""
View related to Cae datas configuration
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

MAIN_CAE_ROUTE = os.path.join(MAIN_ROUTE, "cae")


logger = logging.getLogger(__name__)


class AdminCaeView(BaseConfigView):
    title = "Informations de la CAE"
    description = "Configurer les différentes informations spécifiques à \
votre CAE (Raison sociale, adresse, SIREN…)"
    route_name = MAIN_CAE_ROUTE
    keys = (
        "cae_business_name",
        "cae_legal_status",
        "cae_address",
        "cae_zipcode",
        "cae_city",
        "cae_tel",
        "cae_contact_email",
        "cae_business_identification",
        "cae_intercommunity_vat",
        "cae_vat_collect_mode",
    )
    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_cae"]


def includeme(config):
    config.add_route(MAIN_CAE_ROUTE, MAIN_CAE_ROUTE)
    config.add_admin_view(
        AdminCaeView,
        parent=MainIndexView,
    )
