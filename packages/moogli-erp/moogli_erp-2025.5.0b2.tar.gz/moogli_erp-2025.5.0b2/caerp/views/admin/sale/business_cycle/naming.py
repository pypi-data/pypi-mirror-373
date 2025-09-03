import logging
import os

from deform_extensions import AccordionFormWidget
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin.sale.naming import (
    get_label_override_set_schema,
    mk_field_name,
)
from caerp.models.project.naming import LabelOverride
from caerp.models.project.types import BusinessType
from caerp.views.admin.sale.business_cycle import (
    BUSINESS_URL,
    BusinessCycleIndexView,
)
from caerp.views.admin.tools import BaseAdminFormView

logger = logging.getLogger(__name__)


BUSINESS_TYPE_TASK_NAME_URL = os.path.join(BUSINESS_URL, "task_type_label_override")


class LabelOverrideSetView(BaseAdminFormView):
    title = "Nommage"
    description = (
        "Permet de configurer certains éléments de langage"
        " en fonction du type d'affaire (ex: un « devis » peut"
        " s'appeller « bon de livraison » dans le contexte d'un chantier)"
    )

    validation_msg = "Vos modifications ont été enregistrées"

    route_name = BUSINESS_TYPE_TASK_NAME_URL
    use_csrf_token = True

    add_template_vars = ["help_message"]

    help_message = """
    Pour chaque type d'affaire, il est possible d'outrepasser le nom par défaut
    (exemple : « devis ») tel qu'affiché dans les écrans d'enDi comme sur les
    PDF qu'il produit).<br /><br />


    Cet écran permet de paramétrer type d'affaire par type d'affaire le nom à
    employer pour chaque type de document de vente.

    <br /><br />
    Si les champs sont vides, le nom par défaut sera utilisé.
    """
    permission = PERMISSIONS["global.config_sale"]

    def get_schema(self):
        return get_label_override_set_schema()

    def get_appstruct(self):
        query = LabelOverride.query()
        initial_appstruct = {}
        for item in query:
            dict_k = mk_field_name(item.business_type, item.label_key)
            initial_appstruct[dict_k] = item.label_value
        return initial_appstruct

    def before(self, form):
        super().before(form)
        form.widget = AccordionFormWidget()
        form.set_appstruct(self.get_appstruct())

    def submit_success(self, appstruct):
        appstruct.pop("csrf_token")
        # We remove all entities…
        LabelOverride.query().delete()

        # … And then recreate them from form data
        for name, value in appstruct.items():
            id_and_key = name.split("-", 1)[1]
            business_type_id, label_key = id_and_key.split("+", 1)
            obj = LabelOverride(
                label_value=value,
                business_type=BusinessType.get(business_type_id),
                label_key=label_key,
            )
            self.dbsession.add(obj)

        self.dbsession.flush()
        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.current_route_path())


def includeme(config):
    config.add_route(BUSINESS_TYPE_TASK_NAME_URL, BUSINESS_TYPE_TASK_NAME_URL)
    config.add_admin_view(
        LabelOverrideSetView,
        parent=BusinessCycleIndexView,
    )
