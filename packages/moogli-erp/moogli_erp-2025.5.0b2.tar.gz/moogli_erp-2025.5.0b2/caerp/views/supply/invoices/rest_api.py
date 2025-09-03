import logging

from sqlalchemy import inspect

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.supply.supplier_invoice import (
    get_supplier_invoice_edit_schema,
    validate_supplier_invoice,
)
from caerp.models.company import Company
from caerp.models.sepa import (
    SupplierInvoiceSupplierSepaWaitingPayment,
    SupplierInvoiceUserSepaWaitingPayment,
)
from caerp.models.status import StatusLogEntry
from caerp.models.supply import (
    InternalSupplierInvoice,
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierOrder,
    SupplierOrderLine,
)
from caerp.utils.strings import format_amount
from caerp.views.sepa.routes import SEPA_WAITING_PAYMENT_ITEM_ROUTE

from ..base_rest_api import (
    BaseRestLineView,
    BaseRestSupplierDocumentView,
    BaseSupplierValidationStatusView,
    SupplierStatusLogEntryRestView,
)
from ..utils import get_supplier_doc_url
from .routes import (
    ADD_TO_SEPA_URL,
    API_COLLECTION_ROUTE,
    API_ITEM_ROUTE,
    API_LINE_COLLECTION_ROUTE,
    API_LINE_ITEM_ROUTE,
    API_STATUS_LOG_ENTRIES_ROUTE,
    API_STATUS_LOG_ENTRY_ITEM_ROUTE,
)

logger = logging.getLogger(__name__)


class RestSupplierInvoiceView(BaseRestSupplierDocumentView):
    model_class = SupplierInvoice

    def get_schema(self, submited):
        return get_supplier_invoice_edit_schema(self.context.internal)

    def post_format(self, entry, edit, attributes):
        entry = super(RestSupplierInvoiceView, self).post_format(
            entry, edit, attributes
        )
        history = inspect(entry).attrs.supplier_orders.history
        lines_query = SupplierInvoiceLine.query().filter(
            SupplierInvoiceLine.supplier_invoice_id == entry.id,
        )

        if history.deleted is not None:
            removed_orders_ids = [i.id for i in history.deleted]
            delete_query = lines_query.join("source_supplier_order_line").filter(
                SupplierOrderLine.supplier_order_id.in_(removed_orders_ids),
            )
            lines_to_delete = SupplierInvoiceLine.query().filter(
                SupplierInvoiceLine.id.in_([i.id for i in delete_query])
            )
            if lines_to_delete.count() > 0:
                lines_to_delete.delete(synchronize_session="fetch")

        if (history.added is not None) and (len(history.added) > 0):
            for order in history.added:
                entry.import_lines_from_order(order)

            entry.supplier_id = history.added[0].supplier_id
            entry.cae_percentage = history.added[0].cae_percentage

        return entry

    def _get_form_sections(self):
        editable = bool(
            self.request.has_permission(PERMISSIONS["context.edit_supplier_invoice"])
        )
        has_orders = bool(self.context.supplier_orders)
        sections = {
            "general": {
                "edit": editable,
                "date": {"edit": editable},
                "remote_invoice_number": {"edit": editable},
                "supplier_id": {"edit": not has_orders and editable},
                "cae_percentage": {"edit": not has_orders and editable},
                "payer_id": {},
                "supplier_orders": {"edit": editable},
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
        if self.request.has_permission(PERMISSIONS["context.delete_supplier_invoice"]):
            result.append(self._delete_btn())

        if self.request.has_permission(
            PERMISSIONS["context.duplicate_supplier_invoice"]
        ):
            result.append(self._duplicate_btn())

        if self.request.has_permission(
            PERMISSIONS["context.set_treasury_supplier_invoice"]
        ):
            result.append(self._set_types_btn())

        if self.request.has_permission(
            PERMISSIONS["context.add_payment_supplier_invoice"]
        ):
            if (
                self.context.cae_percentage > 0
                and self.context.supplier_paid_status != "resulted"
            ):
                result.append(self._supplier_payment_btn())
            if (
                self.context.cae_percentage < 100
                and self.context.worker_paid_status != "resulted"
            ):
                result.append(self._user_payment_btn())

        return result

    def _get_set_waiting_action(self, type_, mixed_percentage):
        labels = {"supplier": "fournisseur", "user": "entrepreneur"}
        if mixed_percentage:
            type_label = labels.get(type_)
            label = f"Mettre la part {type_label} en paiement"
        else:
            label = "Mettre en paiement"
        return {
            "widget": "anchor",
            "option": {
                "url": self.request.route_path(
                    ADD_TO_SEPA_URL, id=self.context.id, type=type_
                ),
                "label": label,
                "title": (
                    "Marquer cette facture fournisseur comme étant « À payer » afin"
                    " de l’inclure dans un ordre de virement SEPA"
                ),
                "css": "btn btn-primary",
                "icon": "euro-sign",
            },
        }

    def _get_cancel_waiting_payment(self, waiting_payment, mixed_percentage):
        labels = {
            SupplierInvoiceSupplierSepaWaitingPayment: " fournisseur",
            SupplierInvoiceUserSepaWaitingPayment: " entrepreneur",
        }
        if mixed_percentage:
            type_label = labels.get(waiting_payment.__class__)
            label = f"Annuler la mise en paiement de la part {type_label}"
        else:
            label = "Annuler la mise en paiement"

        return {
            "widget": "POSTButton",
            "option": {
                "url": self.request.route_path(
                    SEPA_WAITING_PAYMENT_ITEM_ROUTE,
                    id=waiting_payment.id,
                ),
                "label": label,
                "title": "Cette facture fournisseur ne sera plus marquée comme « À payer »",
                "css": "btn negative",
                "icon": "euro-slash",
            },
        }

    def _get_status_actions(self):
        actions = super()._get_status_actions()

        mixed_percentage = self.context.cae_percentage not in (0, 100)
        if self.request.has_permission(
            PERMISSIONS["context.add_to_sepa_supplier_invoice"]
        ):
            if self.context.cae_percentage > 0:
                supplier_waiting_for_payment = (
                    self.context.cae_amount_waiting_for_payment()
                )
                if supplier_waiting_for_payment > 0:
                    action = self._get_set_waiting_action("supplier", mixed_percentage)
                    actions.append(action)
            if self.context.cae_percentage < 100:
                user_waiting_for_payment = (
                    self.context.worker_amount_waiting_for_payment()
                )
                if user_waiting_for_payment > 0:
                    action = self._get_set_waiting_action("user", mixed_percentage)
                    actions.append(action)
            # TODO : traiter le cas où on en a 2 et les mettre dans un dropdown

        elif self.context.has_waiting_payment():
            if self.context.cae_percentage > 0:
                waiting_payment = self.context.get_supplier_waiting_payment()
                if waiting_payment:
                    action = self._get_cancel_waiting_payment(
                        waiting_payment, mixed_percentage
                    )
                    actions.append(action)

            if self.context.cae_percentage < 100:
                waiting_payment = self.context.get_user_waiting_payment()
                if waiting_payment:
                    action = self._get_cancel_waiting_payment(
                        waiting_payment, mixed_percentage
                    )
                    actions.append(action)
        return actions

    def _get_duplicate_targets_options(self):
        """
        Build the option list to target on which document we want to duplicate
        a line.
        """
        query = self.get_writable_instances()
        result = [
            {
                "label": "{}{}".format(
                    invoice.name,
                    " (facture courante)" if invoice == self.context else "",
                ),
                "id": invoice.id,
            }
            for invoice in query
        ]
        return result

    def _get_supplier_orders_options(self):
        # Returns available orders that belongs to the invoice company
        query = SupplierOrder.query().filter(
            SupplierOrder.company_id == self.context.company_id,
            (
                (SupplierOrder.supplier_invoice_id == self.context.id)
                | (SupplierOrder.supplier_invoice_id == None)  # noqa
            ),
        )

        result = [
            {
                "label": "{} ({}€ TTC)".format(
                    order.name, format_amount(order.total, grouping=False)
                ),
                "id": order.id,
                "supplier_id": order.supplier_id,
            }
            for order in query
        ]
        return result

    def _get_payers_options(self):
        assert isinstance(self.context, SupplierInvoice)

        # Returns active users or currently selected user
        for emp in self.context.company.employees:
            if (emp.login and emp.login.active) or (emp == self.context.payer):
                yield dict(label=emp.label, value=emp.id)

    def _add_form_options(self, form_config):
        form_config = super(RestSupplierInvoiceView, self)._add_form_options(
            form_config,
        )
        invoices_options = self._get_duplicate_targets_options()
        orders_options = self._get_supplier_orders_options()
        suppliers_options = self._get_suppliers_options()
        payers_options = list(self._get_payers_options())

        form_config["options"]["supplier_invoices"] = invoices_options
        form_config["options"]["supplier_orders"] = orders_options
        form_config["options"]["suppliers"] = suppliers_options
        form_config["options"]["payers"] = payers_options

        return form_config

    def _supplier_payment_btn(self):
        url = get_supplier_doc_url(
            self.request,
            suffix="add_supplier_payment",
        )
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": "Enregistrer manuellement un paiement fournisseur",
                "css": "btn icon only btn-primary",
                "icon": "euro-circle",
            },
        }

    def _user_payment_btn(self):
        url = get_supplier_doc_url(
            self.request,
            suffix="add_user_payment",
        )
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": "Enregistrer manuellement un remboursement entrepreneur",
                "css": "btn icon only  btn-primary",
                "icon": "euro-circle",
            },
        }

    def _set_types_btn(self):
        url = get_supplier_doc_url(
            self.request,
            suffix="set_types",
        )
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": "Configurer les comptes de charge de la facture",
                "css": "btn icon only",
                "icon": "cog",
            },
        }


class RestInternalSupplierInvoiceView(RestSupplierInvoiceView):
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
        form_config["options"]["suppliers"] = []
        form_config["options"]["supplier_invoices"] = []
        form_config["options"]["payers"] = []
        return form_config

    def _get_form_sections(self):
        sections = RestSupplierInvoiceView._get_form_sections(self)
        sections["lines"]["add"] = False
        sections["lines"]["delete"] = False
        sections["lines"]["ht"]["edit"] = False
        sections["lines"]["tva"]["edit"] = False
        sections["general"]["date"]["edit"] = False
        sections["general"]["remote_invoice_number"]["edit"] = False
        sections["general"].pop("supplier_id")
        sections["general"].pop("cae_percentage")
        sections["general"].pop("payer_id")
        sections["general"]["supplier_orders"]["edit"] = False
        return sections


class RestSupplierInvoiceLineView(BaseRestLineView):
    model_class = SupplierInvoiceLine
    fk_field_to_container = "supplier_invoice_id"
    duplicate_permission = PERMISSIONS["context.edit_supplier_invoice"]


class RestSupplierInvoiceValidationStatusView(BaseSupplierValidationStatusView):
    validation_function = staticmethod(validate_supplier_invoice)

    def get_redirect_url(self):
        return get_supplier_doc_url(self.request)


def includeme(config):
    """
    Add rest api views
    """

    config.add_rest_service(
        RestSupplierInvoiceView,
        API_ITEM_ROUTE,
        collection_route_name=API_COLLECTION_ROUTE,
        collection_context=Company,
        context=SupplierInvoice,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.add_supplier_invoice"],
        edit_rights=PERMISSIONS["context.edit_supplier_invoice"],
        delete_rights=PERMISSIONS["context.delete_supplier_invoice"],
    )

    # Form configuration view
    config.add_view(
        RestSupplierInvoiceView,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        renderer="json",
        request_param="form_config",
        context=SupplierInvoice,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        RestInternalSupplierInvoiceView,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        renderer="json",
        request_param="form_config",
        context=InternalSupplierInvoice,
        permission=PERMISSIONS["company.view"],
    )

    # # Status view
    config.add_view(
        RestSupplierInvoiceValidationStatusView,
        route_name=API_ITEM_ROUTE,
        request_param="action=validation_status",
        request_method="POST",
        renderer="json",
        context=SupplierInvoice,
        # More fine permission is checked in-view
        permission=PERMISSIONS["company.view"],
    )

    # Line views
    config.add_rest_service(
        RestSupplierInvoiceLineView,
        API_LINE_ITEM_ROUTE,
        collection_route_name=API_LINE_COLLECTION_ROUTE,
        collection_context=SupplierInvoice,
        context=SupplierInvoiceLine,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_supplier_invoice"],
        edit_rights=PERMISSIONS["context.edit_supplier_invoice"],
        delete_rights=PERMISSIONS["context.delete_supplier_invoice"],
    )
    config.add_view(
        RestSupplierInvoiceLineView,
        attr="duplicate",
        route_name=API_LINE_ITEM_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        renderer="json",
        context=SupplierInvoiceLine,
        permission=PERMISSIONS["context.duplicate_supplier_invoice"],
    )
    config.add_rest_service(
        SupplierStatusLogEntryRestView,
        API_STATUS_LOG_ENTRY_ITEM_ROUTE,
        collection_route_name=API_STATUS_LOG_ENTRIES_ROUTE,
        collection_view_rights=PERMISSIONS["company.view"],
        collection_context=SupplierInvoice,
        context=StatusLogEntry,
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
    )
