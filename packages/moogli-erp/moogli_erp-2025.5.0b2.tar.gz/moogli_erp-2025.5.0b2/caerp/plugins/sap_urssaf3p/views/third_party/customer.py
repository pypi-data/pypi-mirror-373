import logging
import typing
import colander

from pyramid.httpexceptions import HTTPFound

from caerp_base.consts import CIVILITE_OPTIONS
from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.models.third_party import Customer
from caerp.models.status import StatusLogEntry
from caerp.plugins.sap_urssaf3p.models.customer import UrssafCustomerRegistrationStatus
from caerp.plugins.sap_urssaf3p.serializers import serialize_customer
from caerp.plugins.sap_urssaf3p.api_client import (
    HTTPBadRequest,
    PermanentError,
    TemporaryError,
    get_urssaf_api_client,
)
from caerp.views.third_party.customer import (
    controller,
    rest_api,
    routes,
    views as customer_views,
)
from caerp.views.third_party.customer.base import get_customer_url
from caerp.utils.widgets import (
    POSTButton,
)
from caerp.plugins.sap_urssaf3p.forms.customer import (
    get_urssaf_individual_customer_schema,
)
from caerp.views.third_party.customer.lists import CustomersListView


logger = logging.getLogger(__name__)


class UrssafCustomerController(controller.CustomerAddEditController):
    def get_urssaf_schema(self):
        return get_urssaf_individual_customer_schema().bind(request=self.request)

    def get_schemas(self) -> typing.Dict[str, colander.Schema]:
        result = super().get_schemas()
        result["urssaf_data"] = self.get_urssaf_schema()
        return result

    def get_schema(self, submitted: dict) -> colander.Schema:
        if "urssaf_data" in submitted:
            return self.get_urssaf_schema()
        return super().get_schema(submitted)

    def get_default_type(self) -> str:
        return "individual"

    def to_json(self, customer: Customer) -> dict:
        result = super().to_json(customer)
        if customer.urssaf_data is not None:
            result["urssaf_data"] = customer.urssaf_data.__json__(self.request)
        return result

    def after_add_edit(
        self, customer: Customer, edit: bool, attributes: dict
    ) -> Customer:
        """
        post_format hook implementation
        """
        result = super().after_add_edit(customer, edit, attributes)
        if "urssaf_data" not in attributes and result.urssaf_data:
            # Ref #3616 : On supprime les données urssaf si elles ne sont pas
            # dans les données envoyées
            result.urssaf_data = None
        return result

    def historize_status(self, registration_status: UrssafCustomerRegistrationStatus):
        """Historise le statut du client auprès de l'URSSAF.

        :param UrssafCustomerRegistrationStatus registration_status: le statut du
        client auprès de l'URSSAF.
        """
        history = StatusLogEntry(
            node_id=registration_status.id,
            user_id=registration_status.user_id,
            comment=registration_status.comment,
            status=registration_status.status,
            datetime=registration_status.status_date,
            state_manager_key="urssaf3p_registration_status",
        )
        self.request.dbsession.add(history)
        self.request.dbsession.flush()

    def set_registration_status(self, customer: Customer, status, comment=""):
        urssaf_data = customer.urssaf_data
        data_properties = dict(
            status=status,
            user=self.request.identity,
            comment=comment,
            parent=customer,
        )

        if not urssaf_data.registration_status:
            urssaf_data.registration_status = UrssafCustomerRegistrationStatus(
                **data_properties
            )
            self.request.dbsession.add(urssaf_data.registration_status)
            # required to get the id of the registration_status:
            self.request.dbsession.flush()
        else:
            for k, v in data_properties.items():
                setattr(urssaf_data.registration_status, k, v)

            self.request.dbsession.merge(urssaf_data.registration_status)

        self.historize_status(urssaf_data.registration_status)
        return urssaf_data.registration_status

    def request_subscription(self, customer: Customer):
        """
        Demande l'enregistrement du client auprès de l'Urssaf

        :raises: Exception
        :raises: TemporaryError in case of connection failed
        :raises: PermanentError in case of authentication error
        :raises: HTTPBadRequest if the data is not well formed
        """
        if not customer.urssaf_data:
            raise Exception(
                "Données manquantes pour l'enregistrement auprès de l'URSSAF"
            )
        serialized = serialize_customer(customer)
        api = get_urssaf_api_client(self.request.registry.settings)
        client_id = api.inscrire_client(serialized)
        customer.urssaf_data.client_id = client_id
        self.request.dbsession.merge(customer.urssaf_data)
        self.set_registration_status(
            customer,
            "wait",
            "Vous devez contacter votre client pour vous assurer qu'il a accepté"
            " la demande de l'URSSAF avant de cliquer sur Valider.",
        )
        return client_id

    def validate_subscription(self, customer: Customer, success_msg=""):
        """Validation manuelle de l'inscription auprès de l'URSSAF"""
        self.set_registration_status(customer, "valid", success_msg)

    def unvalidate_subscription(self, customer: Customer, success_msg=""):
        """Validation manuelle de l'inscription auprès de l'URSSAF"""
        self.set_registration_status(customer, "disabled", success_msg)


class UrssafCustomerRestView(rest_api.CustomerRestView):
    controller_class = UrssafCustomerController

    def form_config(self):
        result = super().form_config()
        # On renvoie une liste des options de civilités "réduites"
        # En avance immédiate on n'utilise pas de Monsieur et Madame ...
        result["options"]["sap_civilite_options"] = [
            {"id": c[0], "label": c[1]} for c in CIVILITE_OPTIONS[1:]
        ]
        result["options"]["address_completion"] = True
        return result


class UrssafCustomerView(customer_views.CustomerView):
    def stream_more_actions(self):
        if self.context.urssaf_data:
            if self.context.urssaf_data.get_status() is None:
                yield POSTButton(
                    url=get_customer_url(self.request, suffix="/urssaf_request"),
                    label=("Inscrire"),
                    title="Inscrire ce client sur le service Avance Immédiate de "
                    "l’URSSAF",
                    icon="arrow-right",
                )
            elif self.context.urssaf_data.get_status() == "wait":
                yield POSTButton(
                    url=get_customer_url(self.request, suffix="/urssaf_validate"),
                    label=("Activer"),
                    title="Activer le service Avance Immédiate de l’URSSAF pour ce "
                    "client",
                    icon="check",
                )
            elif self.context.urssaf_data.get_status() == "valid":
                yield POSTButton(
                    url=get_customer_url(self.request, suffix="/urssaf_invalidate"),
                    label=("Désactiver"),
                    title="Désactiver le service Avance Immédiate de l’URSSAF pour ce "
                    "client",
                    icon="times",
                    css="negative",
                )

    def __call__(self):
        result = super().__call__()
        result["more_actions"] = self.stream_more_actions()
        return result

    def registration_request_view(self):
        controller = UrssafCustomerController(self.request, edit=True)
        try:
            controller.request_subscription(self.context)
            self.session.flash(
                f"Le client a l'identifiant urssaf {self.context.urssaf_data.client_id}"
            )
        except TemporaryError:
            self.session.flash(
                "Erreur temporaire de connexion à l'API de l'URSSAF, "
                "veuillez ré-essayer plus tard",
                queue="error",
            )
            return HTTPFound(get_customer_url(self.request))
        except HTTPBadRequest as exc:
            message = (
                f"Erreur renvoyée par l'URSSAF : {exc.code} - {exc.message}"
                f" : {exc.description}"
            )
            self.session.flash(message, queue="error")
            return HTTPFound(get_customer_url(self.request))
        except PermanentError as exc:
            self.session.flash(
                "Erreur permanente : il semble que l'accès de MoOGLi à l'API de l'URSSAF "
                "soit mal configuré, veuillez contacter votre administrateur",
                queue="error",
            )
            return HTTPFound(get_customer_url(self.request))
        except Exception as exc:
            logger.exception(exc)
            self.session.flash(str(exc), queue="error")
            return HTTPFound(get_customer_url(self.request, _query={"action": "edit"}))
        else:
            return HTTPFound(get_customer_url(self.request))

    def registration_validate_view(self):
        """
        View called to enable the urssaf payment service for this user

        View called when the customer has validated its urssaf subscription
        In that case the MoOGLi user manually validate the subscription
        """
        msg = (
            f"Le service d'avance immédiate a été activée. Vous pouvez désormais "
            f"utiliser le service d'avance immédiate pour encaisser votre client "
            f"{self.context.label}"
        )
        controller = UrssafCustomerController(self.request, edit=True)
        controller.validate_subscription(self.context, success_msg=msg)
        self.session.flash(msg)
        return HTTPFound(get_customer_url(self.request))

    def registration_invalidate_view(self):
        """
        View called to disable the urssaf payment service for this user
        """
        msg = (
            f"Vous devrez désormais encaisser directement votre client "
            f"{self.context.label}"
        )
        controller = UrssafCustomerController(self.request, edit=True)
        controller.unvalidate_subscription(self.context, success_msg=msg)
        self.session.flash(msg)
        return HTTPFound(get_customer_url(self.request))


def includeme(config):
    config.add_rest_service(
        factory=UrssafCustomerRestView,
        route_name=routes.CUSTOMER_REST_ROUTE,
        collection_route_name=routes.API_COMPANY_CUSTOMERS_ROUTE,
        collection_context=Company,
        context=Customer,
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_customer"],
        add_rights=PERMISSIONS["context.add_customer"],
        delete_rights=PERMISSIONS["context.delete_customer"],
        collection_view_rights=PERMISSIONS["company.view"],
    )
    # On change le template
    config.add_tree_view(
        UrssafCustomerView,
        parent=CustomersListView,
        route_name=routes.CUSTOMER_ITEM_ROUTE,
        renderer="caerp:plugins/sap_urssaf3p/templates/customers/view.mako",
        request_method="GET",
        permission=PERMISSIONS["company.view"],
        layout="customer",
        context=Customer,
    )
    # Vue spécifique pour la mise en route des requêtes d'inscription
    # auprès de l'urssaf
    for action in ("request", "validate", "invalidate"):
        route = "/customers/{id}/urssaf_%s" % action
        config.add_route(route, route, traverse="/customers/{id}")
        config.add_view(
            UrssafCustomerView,
            route_name=route,
            context=Customer,
            request_method="POST",
            attr="registration_{}_view".format(action),
            permission=PERMISSIONS["context.edit_customer"],
        )
    # Form config for customer add/edit
    for route, perm, context in (
        (routes.CUSTOMER_REST_ROUTE, "context.edit_customer", Customer),
        (routes.API_COMPANY_CUSTOMERS_ROUTE, "context.add_customer", Company),
    ):
        config.add_view(
            UrssafCustomerRestView,
            attr="form_config",
            route_name=route,
            context=context,
            renderer="json",
            request_param="form_config",
            permission=PERMISSIONS[perm],
        )
