import os
from caerp.views.admin.main import (
    MAIN_ROUTE,
    MainIndexView,
)
from caerp.views.admin.tools import BaseAdminIndexView


COMPANIES_INDEX_URL = os.path.join(MAIN_ROUTE, "companies")


class MainCompaniesIndex(BaseAdminIndexView):
    title = "Gestion des enseignes"
    description = "Configurer les éléments relatifs aux enseignes de la CAE"
    route_name = COMPANIES_INDEX_URL


def includeme(config):
    config.add_route(COMPANIES_INDEX_URL, COMPANIES_INDEX_URL)
    config.add_admin_view(MainCompaniesIndex, parent=MainIndexView)
    config.include(".company_activities")
    config.include(".internal_companies")
    config.include(".companies_label")
