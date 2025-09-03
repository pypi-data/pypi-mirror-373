from caerp.consts.permissions import PERMISSIONS
from caerp.models.task.estimation import Estimation
from caerp.views.estimations.rest_api import EstimationRestView

from ..mixins import SAPTaskRestViewMixin


class SAPEstimationRestView(SAPTaskRestViewMixin, EstimationRestView):
    def _more_form_sections(self, sections):
        sections = EstimationRestView._more_form_sections(self, sections)
        # En fait pour les devis on ne veut pas demander les dates d'exécution
        # sections["composition"]["classic"]["lines"]["date"] = {"edit": True}
        # On cache les options d'affichage (obligatoires pour le SAP)
        sections["display_options"] = {}
        return sections


def add_views(config):
    config.add_view(
        SAPEstimationRestView,
        attr="form_config",
        route_name="/api/v1/estimations/{id}",
        renderer="json",
        request_param="form_config",
        permission=PERMISSIONS["company.view"],
        context=Estimation,
    )


def includeme(config):
    add_views(config)
