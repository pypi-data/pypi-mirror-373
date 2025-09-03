import colander
import logging

from typing import Dict, List

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.jsonschema import convert_to_jsonschema
from caerp.forms.third_party.customer import (
    CIVILITE_OPTIONS,
    get_list_schema,
)
from caerp.models.status import StatusLogEntry
from caerp.models.third_party import Customer
from caerp.models.company import Company
from caerp.views import (
    BaseRestView,
    RestListMixinClass,
)
from caerp.views.status.rest_api import StatusLogEntryRestView
from caerp.views.status.utils import get_visibility_options
from caerp.views.third_party.customer.routes import (
    API_COMPANY_CUSTOMERS_ROUTE,
    CUSTOMER_REST_ROUTE,
)
from caerp.views.third_party.customer.lists import CustomersListTools

from .controller import CustomerAddEditController


logger = logging.getLogger(__name__)


class CustomerRestView(RestListMixinClass, CustomersListTools, BaseRestView):
    """
    Customer rest view

    collection : context Root

        GET : return list of customers (company_id should be provided)
    """

    list_schema = get_list_schema()
    controller_class = CustomerAddEditController
    edit = False

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.edit = isinstance(context, Customer)
        self.controller = self.controller_class(self.request, edit=self.edit)

    def get_schema(self, submitted: dict) -> colander.Schema:
        return self.controller.get_schema(submitted)

    def query(self):
        return Customer.query().filter_by(company_id=self.context.id)

    def civilite_options(self) -> List[Dict]:
        return [{"id": c[0], "label": c[1]} for c in CIVILITE_OPTIONS]

    def default_customer_type(self) -> str:
        """Collect the default user type

        :return: One of the available customer type (company/individual)
        :rtype: str
        """
        return self.controller.get_default_type()

    def form_config(self):
        schemas = self.controller.get_schemas()
        for key, schema in schemas.items():
            schemas[key] = convert_to_jsonschema(schema)

        if isinstance(self.context, Company):
            company_id = self.context.id
        else:
            company_id = self.context.company_id

        return {
            "options": {
                "visibilities": get_visibility_options(self.request),
                "types": self.controller.get_available_types(),
                "civilite_options": self.civilite_options(),
                "is_admin": self.request.has_permission(
                    PERMISSIONS["global.manage_accounting"]
                ),
                "default_type": self.default_customer_type(),
                "address_completion": False,
                "company_id": company_id,
                "edit": self.edit,
            },
            "schemas": schemas,
        }

    def format_item_result(self, model):
        return self.controller.to_json(model)

    def format_collection(self, query):
        result = [self.controller.to_json(c) for c in query]
        return result

    def post_format(self, entry, edit, attributes):
        """
        Associate a newly created element to the parent company
        """
        return self.controller.after_add_edit(entry, edit, attributes)


def includeme(config):
    config.add_rest_service(
        factory=CustomerRestView,
        route_name=CUSTOMER_REST_ROUTE,
        collection_route_name=API_COMPANY_CUSTOMERS_ROUTE,
        collection_context=Company,
        context=Customer,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_customer"],
        add_rights=PERMISSIONS["context.add_customer"],
        delete_rights=PERMISSIONS["context.delete_customer"],
    )

    # Form config for customer add/edit
    for route, perm, context in (
        (CUSTOMER_REST_ROUTE, "context.edit_customer", Customer),
        (API_COMPANY_CUSTOMERS_ROUTE, "context.add_customer", Company),
    ):
        config.add_view(
            CustomerRestView,
            attr="form_config",
            route_name=route,
            renderer="json",
            request_param="form_config",
            context=context,
            permission=PERMISSIONS[perm],
        )

    config.add_rest_service(
        StatusLogEntryRestView,
        "/api/v1/customers/{eid}/statuslogentries/{id}",
        collection_route_name="/api/v1/customers/{id}/statuslogentries",
        collection_context=Customer,
        context=StatusLogEntry,
        collection_view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
    )
