import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.sale import SaleIndexView, SALE_URL
from caerp.views.admin.tools import BaseAdminIndexView


BUSINESS_URL = os.path.join(SALE_URL, "business_cycle")


class BusinessCycleIndexView(BaseAdminIndexView):
    title = "Cycle d’affaires"
    description = "Configurer les typologies de dossier (Chantier, \
formations…) et leurs pré-requis (mentions, documents…)"
    route_name = BUSINESS_URL
    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    config.add_route(BUSINESS_URL, BUSINESS_URL)
    config.add_admin_view(
        BusinessCycleIndexView,
        parent=SaleIndexView,
    )
    config.include(".project_type")
    config.include(".mentions")
    config.include(".naming")
    config.include(".file_types")
