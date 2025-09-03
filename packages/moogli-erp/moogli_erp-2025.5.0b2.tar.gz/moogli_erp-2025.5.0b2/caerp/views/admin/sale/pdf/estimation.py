import os
from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.sale.pdf import (
    PdfIndexView,
    PDF_URL,
)

ESTIMATION_ROUTE = os.path.join(PDF_URL, "estimation")


class EstimationConfigView(BaseConfigView):
    title = "Informations spécifiques aux devis"
    description = "Configurer les champs spécifiques aux devis dans les \
sorties PDF"
    keys = [
        "coop_estimationheader",
    ]
    schema = get_config_schema(keys)
    validation_msg = "Vos modifications ont été enregistrées"
    route_name = ESTIMATION_ROUTE
    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    config.add_route(ESTIMATION_ROUTE, ESTIMATION_ROUTE)
    config.add_admin_view(
        EstimationConfigView,
        parent=PdfIndexView,
    )
