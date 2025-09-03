import logging
import os

import colander
from pyramid.httpexceptions import HTTPForbidden

from caerp.compute.math_utils import convert_to_int
from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.state_managers import (
    check_signed_allowed,
    get_signed_allowed_actions,
    set_signed_status,
)
from caerp.exception import MessageException
from caerp.forms.tasks.estimation import (
    get_add_edit_paymentline_schema,
    get_edit_estimation_schema,
    validate_estimation,
)
from caerp.models.company import Company
from caerp.models.config import Config
from caerp.models.indicators import SaleFileRequirement
from caerp.models.status import StatusLogEntry
from caerp.models.task import Estimation, PaymentLine
from caerp.models.task.task import DiscountLine, PostTTCLine, TaskLine, TaskLineGroup
from caerp.utils.rest.apiv1 import Apiv1Resp
from caerp.views import BaseRestView
from caerp.views.status import StatusView
from caerp.views.task.rest_api import (
    DiscountLineRestView,
    PostTTCLineRestView,
    TaskAddRestView,
    TaskFileRequirementRestView,
    TaskFileRestView,
    TaskLineGroupRestView,
    TaskLineRestView,
    TaskRestView,
    TaskStatusLogEntryRestView,
    task_total_view,
)
from caerp.views.task.utils import get_field_definition, get_payment_conditions
from caerp.views.task.views import TaskStatusView

from .routes import API_ADD_ROUTE, API_COLLECTION_ROUTE, API_FILE_ROUTE, API_ITEM_ROUTE

logger = logging.getLogger(__name__)


PAYMENT_DISPLAY_OPTIONS = (
    {
        "value": "NONE",
        "label": "Les paiements ne sont pas affichés dans le PDF",
    },
    {
        "value": "SUMMARY",
        "label": "Le résumé des paiements apparaît dans le PDF",
    },
    {
        "value": "ALL",
        "label": "Le détail des paiements apparaît dans le PDF",
    },
    {
        "value": "ALL_NO_DATE",
        "label": ("Le détail des paiements, sans les dates, apparaît dans le PDF",),
    },
)


DEPOSIT_OPTIONS = (
    {"value": 0, "label": "Aucun", "default": True},
    {"value": 5, "label": "5%"},
    {"value": 10, "label": "10 %"},
    {"value": 20, "label": "20 %"},
    {"value": 30, "label": "30 %"},
    {"value": 40, "label": "40 %"},
    {"value": 50, "label": "50 %"},
    {"value": 60, "label": "60 %"},
    {"value": 70, "label": "70 %"},
    {"value": 80, "label": "80 %"},
    {"value": 90, "label": "90 %"},
)


PAYMENT_TIMES_OPTIONS = (
    {"value": -1, "label": "Configuration manuelle"},
    {"value": 1, "label": "1 fois", "default": True},
    {"value": 2, "label": "2 fois"},
    {"value": 3, "label": "3 fois"},
    {"value": 4, "label": "4 fois"},
    {"value": 5, "label": "5 fois"},
    {"value": 6, "label": "6 fois"},
    {"value": 7, "label": "7 fois"},
    {"value": 8, "label": "8 fois"},
    {"value": 9, "label": "9 fois"},
    {"value": 10, "label": "10 fois"},
    {"value": 11, "label": "11 fois"},
    {"value": 12, "label": "12 fois"},
)


class EstimationAddRestView(TaskAddRestView):
    """
    Estimation Add Rest View, Company is the current context

    .. http:get:: /api/v1/companies/(company_id)/estimations/add?form_config=1
        :noindex:

            Returns configuration informations for Estimation add form

        :query int: company_id (*required*) -- The id of the company

    .. http:post:: /api/v1/companies/(company_id)/estimations/add
        :noindex:

            Add a new estimation

        :query int: company_id (*required*) -- The if of the company
    """

    factory = Estimation


class EstimationRestView(TaskRestView):
    factory = Estimation

    def get_schema(self, submitted):
        """
        Return the schema for Estimation add/edition

        :param dict submitted: The submitted datas
        :returns: A colander.Schema
        """
        excludes = (
            "status",
            "children",
            "parent",
        )
        return get_edit_estimation_schema(excludes=excludes)

    def pre_format(self, appstruct, edit=False):
        """
        Preformat the posted appstruct to handle Estimation specific mechanisms
        """
        payment_times = appstruct.pop("payment_times", None)
        if payment_times is not None:
            self.payment_times = convert_to_int(payment_times, default=1)
            if self.payment_times == -1:
                appstruct["manualDeliverables"] = 1
            else:
                appstruct["manualDeliverables"] = 0
        else:
            self.payment_times = None
        return super().pre_format(appstruct, edit=edit)

    def _more_form_sections(self, sections):
        """
        Add estimation specific form sections to the sections returned to the
        end user

        :param dict sections: The sections to return
        :returns: The sections
        """
        sections["composition"]["classic"]["discounts"] = {"mode": "classic"}
        sections["composition"]["classic"]["post_ttc_lines"] = {}
        sections["payment_conditions"] = {"edit": True}
        sections["payments"] = {"edit": True}
        sections["common"].update(get_field_definition("validity_duration"))

        return sections

    def _more_form_options(self, form_options):
        """
        Add estimation specific form options to the options returned to the end
        user

        :param dict form_options: The options returned to the end user
        :returns: The form_options with new elements
        """
        duration = Config.get_value("estimation_validity_duration_default")
        form_options.update(
            {
                "payment_conditions": get_payment_conditions(self.request),
                "deposits": DEPOSIT_OPTIONS,
                "payment_times": PAYMENT_TIMES_OPTIONS,
                "payment_displays": PAYMENT_DISPLAY_OPTIONS,
                "estimation_validity_duration_default": duration,
            }
        )
        return form_options

    def _get_signed_status_button(self):
        """
        Return a signed_status toggle button
        """
        url = self.request.current_route_path(_query={"action": "signed_status"})
        widget = {
            "widget": "toggle",
            "options": {
                "url": url,
                "values": [],
                "name": "signed_status",
                "title": "Validation par le client",
            },
        }
        for action in get_signed_allowed_actions(self.request, self.context):
            widget["options"]["values"].append(action.__json__(self.request))

        return widget

    def _get_other_actions(self):
        """
        Return the description of other available actions :
            signed_status
            duplicate
            ...
        """
        result = []
        if self.request.has_permission(
            PERMISSIONS["context.set_signed_status_estimation"]
        ):
            result.append(self._get_signed_status_button())
        result.extend(TaskRestView._get_other_actions(self))
        return result

    def after_flush(self, entry, edit, attributes):
        super().after_flush(entry, edit, attributes)
        entry.update_payment_lines(self.request, self.payment_times)
        self.dbsession.merge(entry)
        self.dbsession.flush()
        return entry


class PaymentLineRestView(BaseRestView):
    """
    Rest views used to handle the estimation payment lines

    context is en Estimation (collection level) or PaymentLine (item level)

    Collection views

        GET

            Return all the items belonging to the parent task

        POST

            Add a new item

    Item views

        GET

            Return the Item

        PUT/PATCH

            Edit the item

        DELETE

            Delete the item
    """

    def get_schema(self, submitted):
        """
        Return the schema for PaymentLine add/edition

        :param dict submitted: The submitted datas
        :returns: A colander.Schema
        """
        excludes = ("task_id",)
        return get_add_edit_paymentline_schema(excludes=excludes)

    def collection_get(self):
        """
        View returning the task line groups attached to this estimation
        """
        return self.context.payment_lines

    def post_format(self, entry, edit, attributes):
        """
        Associate a newly created element to the parent task
        """
        if not edit:
            # On ajoute la ligne juste avant le solde (surtout pour les tests)
            self.context.payment_lines.insert(-1, entry)
        return entry

    def after_flush(self, entry, edit, attributes):
        entry.task.update_payment_lines(self.request)
        return entry

    def pre_delete(self):
        self.task = self.context.task

    def on_delete(self):
        self.task.update_payment_lines(self.request)


class EstimationStatusRestView(TaskStatusView):
    state_manager_key = "status"

    def _get_project_redirect(self):
        from caerp.views.project.routes import PROJECT_ITEM_ESTIMATION_ROUTE

        project_id = self.context.project_id
        result = self.request.route_path(PROJECT_ITEM_ESTIMATION_ROUTE, id=project_id)
        return result

    def _get_business_redirect(self):
        from caerp.views.business.routes import BUSINESS_ITEM_OVERVIEW_ROUTE

        business_id = self.context.business_id
        result = self.request.route_path(BUSINESS_ITEM_OVERVIEW_ROUTE, id=business_id)
        return result

    def get_parent_url(self):
        if self.context.project.project_type.name == "default":
            result = self._get_project_redirect()
        else:
            if self.context.business_id:
                result = self._get_business_redirect()
            else:
                result = self._get_project_redirect()
        return result

    def validate(self):
        try:
            validate_estimation(self.context, self.request)
        except colander.Invalid as err:
            logger.exception(
                "An error occured when validating this Estimation (id:%s)"
                % (self.request.context.id)
            )
            raise err
        return {}


class EstimationSignedStatusRestView(StatusView):
    def check_allowed(self, status):
        check_signed_allowed(self.request, self.context, status)

    def status_process(self, status, params):
        try:
            return set_signed_status(self.request, self.context, status, **params)
        except MessageException as err:
            # Erreur possible dans le cas de la facturation à l'avancement
            self.session.flash(err.message, queue="error")
            raise HTTPForbidden()

    def redirect(self):
        return Apiv1Resp(self.request, {"signed_status": self.context.signed_status})


class EstimationTaskLineGroupRestView(TaskLineGroupRestView):
    def after_flush(self, entry, edit, attributes):
        entry.task.update_payment_lines(self.request)
        return TaskLineGroupRestView.after_flush(self, entry, edit, attributes)

    def pre_delete(self):
        self.task = self.context.task

    def on_delete(self):
        self.task.update_payment_lines(self.request)
        return super().on_delete()


class EstimationTaskLineRestView(TaskLineRestView):
    def after_flush(self, entry, edit, attributes):
        entry.group.task.update_payment_lines(self.request)
        return TaskLineRestView.after_flush(self, entry, edit, attributes)

    def pre_delete(self):
        self.task = self.context.group.task

    def on_delete(self):
        self.task.update_payment_lines(self.request)
        return super().on_delete()


class EstimationDiscountLineRestView(DiscountLineRestView):
    def after_flush(self, entry, edit, attributes):
        entry.task.update_payment_lines(self.request)
        return DiscountLineRestView.after_flush(self, entry, edit, attributes)

    def pre_delete(self):
        self.task = self.context.task

    def on_delete(self):
        self.task.update_payment_lines(self.request)
        return super().on_delete()


def add_routes(config):
    """
    Add routes to the current configuration

    :param obj config: Pyramid config object
    """
    for collection in (
        "task_line_groups",
        "discount_lines",
        "post_ttc_lines",
        "payment_lines",
        "file_requirements",
        "total",
    ):
        route = os.path.join(API_ITEM_ROUTE, collection)
        config.add_route(route, route, traverse="/tasks/{id}")

    FILE_REQ_ITEM_ROUTE = os.path.join(
        API_COLLECTION_ROUTE, "{eid}", "file_requirements", "{id}"
    )
    config.add_route(
        FILE_REQ_ITEM_ROUTE,
        FILE_REQ_ITEM_ROUTE,
        traverse="/indicators/{id}",
    )

    config.add_route(
        "/api/v1/estimations/{eid}/task_line_groups/{id}",
        r"/api/v1/estimations/{eid}/task_line_groups/{id:\d+}",
        traverse="/task_line_groups/{id}",
    )
    config.add_route(
        "/api/v1/estimations/{eid}/task_line_groups/{id}/task_lines",
        r"/api/v1/estimations/{eid}/task_line_groups/{id:\d+}/task_lines",
        traverse="/task_line_groups/{id}",
    )
    config.add_route(
        "/api/v1/estimations/{eid}/task_line_groups/{tid}/task_lines/{id}",
        r"/api/v1/estimations/{eid}/task_line_groups/{tid}/task_lines" r"/{id:\d+}",
        traverse="/task_lines/{id}",
    )
    config.add_route(
        "/api/v1/estimations/{eid}/discount_lines/{id}",
        r"/api/v1/estimations/{eid}/discount_lines/{id:\d+}",
        traverse="/discount_lines/{id}",
    )
    config.add_route(
        "/api/v1/estimations/{eid}/post_ttc_lines/{id}",
        r"/api/v1/estimations/{eid}/post_ttc_lines/{id:\d+}",
        traverse="/post_ttc_lines/{id}",
    )
    config.add_route(
        "/api/v1/estimations/{eid}/payment_lines/{id}",
        r"/api/v1/estimations/{eid}/payment_lines/{id:\d+}",
        traverse="/payment_lines/{id}",
    )
    config.add_route(
        "/api/v1/estimations/{id}/statuslogentries",
        r"/api/v1/estimations/{id:\d+}/statuslogentries",
        traverse="/tasks/{id}",
    )
    config.add_route(
        "/api/v1/estimations/{eid}/statuslogentries/{id}",
        r"/api/v1/estimations/{eid:\d+}/statuslogentries/{id:\d+}",
        traverse="/statuslogentries/{id}",
    )


def add_views(config):
    """
    Add views to the current configuration
    """
    config.add_rest_service(
        EstimationRestView,
        API_ITEM_ROUTE,
        collection_route_name=API_COLLECTION_ROUTE,
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_estimation"],
        delete_rights=PERMISSIONS["context.delete_estimation"],
        context=Estimation,
        collection_context=Company,
    )
    # Form configuration view
    config.add_view(
        EstimationRestView,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        renderer="json",
        request_param="form_config",
        # NB : si le devis est validé On a besoin de cette vue pour les mémos
        permission=PERMISSIONS["company.view"],
        context=Estimation,
    )

    # Rest service for Estimation add
    config.add_rest_service(
        EstimationAddRestView,
        collection_route_name=API_ADD_ROUTE,
        view_rights=PERMISSIONS["context.add_estimation"],
        add_rights=PERMISSIONS["context.add_estimation"],
        collection_context=Company,
    )
    # Form configuration view
    config.add_view(
        EstimationAddRestView,
        attr="form_config",
        route_name=API_ADD_ROUTE,
        renderer="json",
        request_param="form_config",
        permission=PERMISSIONS["context.add_estimation"],
        context=Company,
    )
    # Status View
    config.add_view(
        EstimationStatusRestView,
        route_name=API_ITEM_ROUTE,
        request_param="action=status",
        permission=PERMISSIONS["context.edit_estimation"],
        request_method="POST",
        renderer="json",
        context=Estimation,
    )
    config.add_view(
        EstimationSignedStatusRestView,
        route_name=API_ITEM_ROUTE,
        request_param="action=signed_status",
        permission=PERMISSIONS["context.set_signed_status_estimation"],
        request_method="POST",
        renderer="json",
        context=Estimation,
    )

    # Task linegroup views
    config.add_rest_service(
        EstimationTaskLineGroupRestView,
        "/api/v1/estimations/{eid}/task_line_groups/{id}",
        collection_route_name="/api/v1/estimations/{id}/task_line_groups",
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_estimation"],
        edit_rights=PERMISSIONS["context.edit_estimation"],
        delete_rights=PERMISSIONS["context.edit_estimation"],
        context=TaskLineGroup,
        collection_context=Estimation,
    )
    config.add_view(
        TaskLineGroupRestView,
        route_name="/api/v1/estimations/{id}/task_line_groups",
        attr="post_load_groups_from_catalog_view",
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        permission=PERMISSIONS["context.edit_estimation"],
        context=Estimation,
    )
    # Task line views
    config.add_rest_service(
        EstimationTaskLineRestView,
        route_name="/api/v1/estimations/{eid}/task_line_groups/{tid}/task_lines/{id}",
        collection_route_name=(
            "/api/v1/estimations/{eid}/task_line_groups/{id}/task_lines"
        ),
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_estimation"],
        edit_rights=PERMISSIONS["context.edit_estimation"],
        delete_rights=PERMISSIONS["context.edit_estimation"],
        collection_context=TaskLineGroup,
        context=TaskLine,
    )
    config.add_view(
        TaskLineRestView,
        route_name="/api/v1/estimations/{eid}/task_line_groups/{id}/task_lines",
        attr="post_load_from_catalog_view",
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        permission=PERMISSIONS["context.edit_estimation"],
        context=TaskLineGroup,
    )
    # Discount line views
    config.add_rest_service(
        EstimationDiscountLineRestView,
        "/api/v1/estimations/{eid}/discount_lines/{id}",
        collection_route_name="/api/v1/estimations/{id}/discount_lines",
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_estimation"],
        edit_rights=PERMISSIONS["context.edit_estimation"],
        delete_rights=PERMISSIONS["context.edit_estimation"],
        collection_context=Estimation,
        context=DiscountLine,
    )
    config.add_view(
        DiscountLineRestView,
        route_name="/api/v1/estimations/{id}/discount_lines",
        attr="post_percent_discount_view",
        request_param="action=insert_percent",
        request_method="POST",
        renderer="json",
        permission=PERMISSIONS["context.edit_estimation"],
        context=Estimation,
    )
    config.add_rest_service(
        PostTTCLineRestView,
        "/api/v1/estimations/{eid}/post_ttc_lines/{id}",
        collection_route_name="/api/v1/estimations/{id}/post_ttc_lines",
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_estimation"],
        edit_rights=PERMISSIONS["context.edit_estimation"],
        delete_rights=PERMISSIONS["context.edit_estimation"],
        collection_context=Estimation,
        context=PostTTCLine,
    )
    # Payment lines views
    config.add_rest_service(
        PaymentLineRestView,
        "/api/v1/estimations/{eid}/payment_lines/{id}",
        collection_route_name="/api/v1/estimations/{id}/payment_lines",
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_estimation"],
        edit_rights=PERMISSIONS["context.edit_estimation"],
        delete_rights=PERMISSIONS["context.edit_estimation"],
        collection_context=Estimation,
        context=PaymentLine,
    )
    # File requirements views
    config.add_rest_service(
        TaskFileRequirementRestView,
        "/api/v1/estimations/{eid}/file_requirements/{id}",
        collection_route_name="/api/v1/estimations/{id}/file_requirements",
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        collection_context=Estimation,
        context=SaleFileRequirement,
    )
    config.add_view(
        TaskFileRequirementRestView,
        route_name="/api/v1/estimations/{eid}/file_requirements/{id}",
        attr="validation_status",
        permission=PERMISSIONS["context.validate_indicator"],
        request_method="POST",
        request_param="action=validation_status",
        renderer="json",
        context=SaleFileRequirement,
    )
    config.add_view(
        task_total_view,
        route_name="/api/v1/estimations/{id}/total",
        permission=PERMISSIONS["company.view"],
        request_method="GET",
        renderer="json",
        xhr=True,
        context=Estimation,
    )

    config.add_rest_service(
        TaskStatusLogEntryRestView,
        "/api/v1/estimations/{eid}/statuslogentries/{id}",
        collection_route_name="/api/v1/estimations/{id}/statuslogentries",
        collection_view_rights=PERMISSIONS["company.view"],
        collection_context=Estimation,
        context=StatusLogEntry,
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
    )

    config.add_view(
        TaskFileRestView,
        route_name=API_FILE_ROUTE,
        context=Estimation,
        permission=PERMISSIONS["context.add_file"],
        renderer="json",
        request_method="POST",
        attr="post",
    )


def includeme(config):
    add_routes(config)
    add_views(config)
