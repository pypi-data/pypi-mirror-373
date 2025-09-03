import logging
from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.models.status import StatusLogEntry
from caerp.models.supply import (
    SupplierOrder,
    SupplierOrderLine,
    InternalSupplierOrder,
)
from caerp.forms.supply.supplier_order import (
    get_supplier_order_edit_schema,
    validate_supplier_order,
)

from caerp.views.supply.utils import get_supplier_doc_url
from ..base_rest_api import (
    BaseRestSupplierDocumentView,
    BaseRestLineView,
    BaseSupplierValidationStatusView,
    SupplierStatusLogEntryRestView,
)
from .routes import (
    API_STATUS_LOG_ENTRY_ITEM_ROUTE,
    API_COLLECTION_ROUTE,
    API_ITEM_ROUTE,
    API_LINE_COLLECTION_ROUTE,
    API_LINE_ITEM_ROUTE,
    API_STATUS_LOG_ENTRIES_ROUTE,
)


logger = logging.getLogger(__name__)


class RestSupplierOrderView(BaseRestSupplierDocumentView):
    model_class = SupplierOrder

    def get_schema(self, submited):
        return get_supplier_order_edit_schema(self.context.internal)

    def _get_form_sections(self):
        editable = bool(
            self.request.has_permission(PERMISSIONS["context.edit_supplier_order"])
        )
        sections = {
            "general": {
                "edit": editable,
                "supplier_id": {"edit": editable},
                "cae_percentage": {"edit": editable},
            },
            "lines": {
                "edit": editable,
                "add": editable,
                "delete": editable,
                "ht": {"edit": editable},
                "tva": {"edit": editable},
            },
        }
        return sections

    def _get_other_actions(self):
        """
        Return the description of other available actions :
            duplicate
            ...
        """
        result = []

        if self.request.has_permission(PERMISSIONS["context.delete_supplier_order"]):
            result.append(self._delete_btn())

        if self.request.has_permission(PERMISSIONS["context.duplicate_supplier_order"]):
            result.append(self._duplicate_btn())

        return result

    def _get_duplicate_targets_options(self):
        query = self.get_writable_instances()
        result = [
            {
                "label": "{}{}".format(
                    order.name, " (commande courante)" if order == self.context else ""
                ),
                "id": order.id,
            }
            for order in query
        ]
        return result

    def _add_form_options(self, form_config):
        form_config = super(RestSupplierOrderView, self)._add_form_options(
            form_config,
        )
        orders_options = self._get_duplicate_targets_options()
        form_config["options"]["supplier_orders"] = orders_options
        form_config["options"]["suppliers"] = self._get_suppliers_options()
        return form_config


class RestInternalSupplierOrderView(RestSupplierOrderView):
    def _get_suppliers_options(self):
        return [
            {
                "label": self.context.supplier.label,
                "value": self.context.supplier_id,
            }
        ]

    def _add_form_options(self, form_config):
        form_config = BaseRestSupplierDocumentView._add_form_options(self, form_config)
        form_config["options"]["supplier_orders"] = []
        form_config["options"]["suppliers"] = self._get_suppliers_options()
        return form_config

    def _get_form_sections(self):
        sections = RestSupplierOrderView._get_form_sections(self)
        sections["lines"]["add"] = False
        sections["lines"]["delete"] = False
        sections["lines"]["ht"]["edit"] = False
        sections["lines"]["tva"]["edit"] = False
        sections["general"]["cae_percentage"]["edit"] = False
        sections["general"]["supplier_id"]["edit"] = False
        return sections


class RestSupplierOrderLineView(BaseRestLineView):
    model_class = SupplierOrderLine
    fk_field_to_container = "supplier_order_id"
    duplicate_permission = PERMISSIONS["context.edit_supplier_order"]


class RestSupplierOrderValidationStatusView(BaseSupplierValidationStatusView):
    validation_function = staticmethod(validate_supplier_order)

    def get_redirect_url(self):
        return get_supplier_doc_url(self.request)


def includeme(config):
    config.add_rest_service(
        RestSupplierOrderView,
        API_ITEM_ROUTE,
        collection_route_name=API_COLLECTION_ROUTE,
        collection_context=Company,
        context=SupplierOrder,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.add_supplier_order"],
        edit_rights=PERMISSIONS["context.edit_supplier_order"],
        delete_rights=PERMISSIONS["context.delete_supplier_order"],
    )

    # Form configuration view
    config.add_view(
        RestSupplierOrderView,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        renderer="json",
        request_param="form_config",
        context=SupplierOrder,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        RestInternalSupplierOrderView,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        renderer="json",
        request_param="form_config",
        context=InternalSupplierOrder,
        permission=PERMISSIONS["company.view"],
    )

    # # Status view
    config.add_view(
        RestSupplierOrderValidationStatusView,
        route_name=API_ITEM_ROUTE,
        request_param="action=validation_status",
        request_method="POST",
        renderer="json",
        context=SupplierOrder,
        # More fine permission is checked in-view
        permission=PERMISSIONS["company.view"],
    )

    # Line views
    config.add_rest_service(
        RestSupplierOrderLineView,
        API_LINE_ITEM_ROUTE,
        collection_route_name=API_LINE_COLLECTION_ROUTE,
        collection_context=SupplierOrder,
        context=SupplierOrderLine,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_supplier_order"],
        edit_rights=PERMISSIONS["context.edit_supplier_order"],
        delete_rights=PERMISSIONS["context.delete_supplier_order"],
    )
    config.add_view(
        RestSupplierOrderLineView,
        attr="duplicate",
        route_name=API_LINE_ITEM_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        renderer="json",
        context=SupplierOrderLine,
        permission=PERMISSIONS["context.duplicate_supplier_order"],
    )
    config.add_rest_service(
        SupplierStatusLogEntryRestView,
        API_STATUS_LOG_ENTRY_ITEM_ROUTE,
        collection_route_name=API_STATUS_LOG_ENTRIES_ROUTE,
        collection_context=SupplierOrder,
        context=StatusLogEntry,
        collection_view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
    )
