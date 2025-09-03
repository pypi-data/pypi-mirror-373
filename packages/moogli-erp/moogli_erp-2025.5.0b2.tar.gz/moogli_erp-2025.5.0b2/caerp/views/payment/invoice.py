import datetime
import logging
from typing import Dict

import colander
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.payment.invoice import (
    check_remittance,
    create_bank_remittance,
    format_bank_remittance_name,
)
from caerp.controllers.state_managers.payment import check_node_resulted
from caerp.events.document_events import StatusChangedEvent
from caerp.exception import BadRequest
from caerp.export.task_pdf import ensure_task_pdf_persisted
from caerp.forms import deform_options_to_js_options
from caerp.forms.jsonschema import convert_to_jsonschema
from caerp.forms.payments import (
    get_bank_account_options,
    get_customer_bank_options,
    get_payment_mode_options,
)
from caerp.forms.tasks.payment import get_cancel_payment_schema, get_payment_schema
from caerp.interfaces import IPaymentRecordService
from caerp.models.services.user import UserPrefsService
from caerp.models.task import Invoice
from caerp.models.task.payment import BaseTaskPayment
from caerp.utils.rest.apiv1 import RestError, RestResponse
from caerp.utils.strings import format_amount
from caerp.utils.widgets import Link
from caerp.views import (
    BaseFormView,
    BaseRestView,
    BaseView,
    JsAppViewMixin,
    PopupMixin,
    TreeMixin,
)
from caerp.views.invoices.invoice import InvoicePaymentView as InvoicePaymentTabView
from caerp.views.payment.routes import (
    INVOICE_PAYMENT_ADD,
    INVOICE_PAYMENT_API_COLLECTION,
    INVOICE_PAYMENT_API_ITEM_VIEW,
)
from caerp.views.task.utils import get_task_url

from .base import BasePaymentDeleteView, get_delete_confirm_message

logger = logging.getLogger(__name__)


class InvoicePaymentView(BaseView, TreeMixin):
    """
    Simple payment view
    """

    route_name = "payment"

    @property
    def tree_url(self):
        return self.request.route_path("payment", id=self.context.id)

    @property
    def title(self):
        return "Paiement pour la facture {0}".format(
            self.context.task.official_number,
        )

    def stream_actions(self):
        parent_url = get_task_url(self.request, self.context.task, suffix="/general")
        if self.request.has_permission(PERMISSIONS["context.edit_payment"]):
            _query = {"action": "edit"}
            if self.request.is_popup:
                _query["popup"] = "1"

            edit_url = self.request.route_path(
                "payment", id=self.context.id, _query=_query
            )

            yield Link(
                edit_url,
                label="Modifier",
                title="Modifier les informations du paiement",
                icon="pen",
                css="btn btn-primary",
            )
        if self.request.has_permission(PERMISSIONS["context.delete_payment"]):
            _query = dict(action="delete", come_from=parent_url)
            if self.request.is_popup:
                _query["popup"] = "1"

            confirm = get_delete_confirm_message(self.context, "encaissement", "cet")
            yield Link(
                self.request.route_path(
                    "payment",
                    id=self.context.id,
                    _query=_query,
                ),
                label="Supprimer",
                title="Supprimer le paiement",
                icon="trash-alt",
                confirm=confirm,
                css="negative",
            )
        if self.request.has_permission(PERMISSIONS["context.gen_inverse_payment"]):
            _query = dict(action="gen_inverse")
            if self.request.is_popup:
                _query["popup"] = "1"

            yield Link(
                self.request.route_path("payment", id=self.context.id, _query=_query),
                label="Annuler",
                title="Génère un encaissement négatif annulant comptablement celui-ci",
                icon="exchange",
                css="btn-primary negative",
            )

    def get_export_button(self):
        if not self.request.has_permission(PERMISSIONS["global.manage_accounting"]):
            return
        if self.context.exported:
            label = "Forcer l'export des écritures pour cet encaissement"
        else:
            label = "Générer les écritures pour cet encaissement"

        return Link(
            self.request.route_path(
                "/export/treasury/payments/{id}",
                id=self.context.id,
                _query=dict(come_from=self.tree_url, force=True),
            ),
            label=label,
            title=label,
            icon="file-export",
            css="btn btn-primary",
        )

    def __call__(self):
        self.populate_navigation()
        return dict(
            title=self.title,
            actions=self.stream_actions(),
            export_button=self.get_export_button(),
            money_flow_type="Cet encaissement",
            document_number=f"Facture {self.context.task.official_number}",
        )


class InvoicePaymentAddView(BaseView, JsAppViewMixin, TreeMixin, PopupMixin):
    edit = False
    route_name = INVOICE_PAYMENT_ADD
    more_template_vars = ("help_message",)

    @property
    def title(self):
        return (
            "Enregistrer un encaissement pour la facture "
            "{0.official_number}".format(self.get_invoice())
        )

    def get_invoice(self):
        return self.context

    def context_url(self, _query: Dict[str, str] = {}):
        return get_task_url(
            self.request,
            task=self.get_invoice(),
            _query=_query,
            api=True,
            suffix="/payments",
        )

    def __call__(self) -> dict:
        from caerp.resources import task_payment_js

        task_payment_js.need()
        self.populate_navigation()
        result = {
            "title": self.title,
            "js_app_options": self.get_js_app_options(),
        }
        return result

    def more_js_app_options(self):
        return {
            "invoice_id": self.get_invoice().id,
            "redirect_url": get_task_url(
                self.request, self.get_invoice(), suffix="/payment"
            ),
        }


class InvoicePaymentEditView(InvoicePaymentAddView):

    route_name = "payment"

    @property
    def title(self):
        return "Modification d'un encaissement"

    def get_invoice(self):
        return self.context.invoice

    def context_url(self, _query: Dict[str, str] = {}):
        return self.request.route_path(
            INVOICE_PAYMENT_API_ITEM_VIEW,
            id=self.context.id,
            _query=_query,
        )

    def more_js_app_options(self):
        result = super().more_js_app_options()
        result["payment_id"] = self.context.id
        return result


class InvoicePaymentRestView(BaseRestView):
    """
    Rest view for Invoice payments manipulation
    """

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.edit = isinstance(self.context, BaseTaskPayment)

    def _get_invoice(self):
        if self.edit:
            return self.context.invoice
        else:
            return self.context

    def get_schema(self, submitted: Dict):
        invoice = self._get_invoice()
        return get_payment_schema(self.request, invoice, self.edit)

    def form_config(self):
        topay = self._get_invoice().topay()
        if self.edit:
            topay += self.context.amount
        return {
            "schemas": {
                "default": convert_to_jsonschema(self.get_schema({})),
            },
            "options": {
                "payment_modes": deform_options_to_js_options(
                    get_payment_mode_options(self.request)
                ),
                "bank_accounts": deform_options_to_js_options(
                    get_bank_account_options(self.request)
                ),
                "customer_bank_accounts": deform_options_to_js_options(
                    get_customer_bank_options(self.request)
                ),
                "max_amount": topay,
            },
        }

    def get(self):
        return self.context

    def ensure_remittance_exists(self, attributes):
        """
        Add the bank remittance if it doesn't exist
        """
        if "bank_remittance_id" in attributes:
            bank_remittance_id = format_bank_remittance_name(
                self.request, attributes["bank_remittance_id"]
            )
            if self.edit:
                old_remittance_id = self.context.bank_remittance_id
                mode = attributes.get("mode", self.context.mode)
                bank_id = attributes.get("bank_id", self.context.bank_id)
            else:
                old_remittance_id = None
                mode = attributes["mode"]
                bank_id = attributes["bank_id"]

            bank_remittance = check_remittance(
                self.request,
                bank_remittance_id,
                mode,
                bank_id,
                old_remittance_id=old_remittance_id,
            )
            if bank_remittance is None:
                bank_remittance = create_bank_remittance(
                    self.request,
                    bank_remittance_id,
                    mode,
                    bank_id,
                )

    def test_values_to_be_confirmed(self, schema, attributes):
        """
        Test values that need to be confirmed before recording payments
        """
        if "bank_remittance_id" in attributes:
            bank_remittance_id = format_bank_remittance_name(
                self.request, attributes["bank_remittance_id"]
            )
            attributes["bank_remittance_id"] = bank_remittance_id
            if self.edit:
                old_remittance_id = self.context.bank_remittance_id
                mode = attributes.get("mode", self.context.mode)
                bank_id = attributes.get("bank_id", self.context.bank_id)
            else:
                old_remittance_id = None
                mode = attributes["mode"]
                bank_id = attributes["bank_id"]
            try:
                bank_remittance = check_remittance(
                    self.request,
                    bank_remittance_id,
                    mode,
                    bank_id,
                    old_remittance_id=old_remittance_id,
                )
            except BadRequest as error:
                message = error.message
                raise RestError({"bank_remittance_id": message})
            else:
                confirm = attributes.get("new_remittance_confirm", False)
                if bank_remittance is None and not confirm:
                    raise RestResponse(
                        {"field": "bank_remittance_id"}, status="confirmation", code=202
                    )

        return True

    def check_bank_remittance_id_view(self):
        """
        Rest endpoint for checking the bank remittance id
        """
        submitted = self.get_posted_data()
        schema = self.get_schema(submitted)
        try:
            attributes = schema.deserialize(submitted)
        except colander.Invalid as err:
            self.logger.exception("  - Erreur")
            self.logger.exception(submitted)
            raise RestError(err.asdict(), 400)

        self.test_values_to_be_confirmed(schema, attributes)
        return {}

    def notify(self):
        self.request.registry.notify(
            StatusChangedEvent(
                self.request,
                self.context,
                self.context.paid_status,
            )
        )

    def _before_add_edit(self, schema, attributes):
        self.test_values_to_be_confirmed(schema, attributes)
        self.ensure_remittance_exists(attributes)
        ensure_task_pdf_persisted(self._get_invoice(), self.request)

    def _after_add_edit(self, schema, attributes):
        force_resulted = attributes.pop("resulted", False)
        invoice: Invoice = self._get_invoice()
        check_node_resulted(
            self.request,
            invoice,
            force_resulted=force_resulted,
        )
        invoice.historize_paid_status(self.request.identity)
        # Mémorisation du dernier numéro de remise utilisé
        remittance_id = attributes.get("bank_remittance_id")
        UserPrefsService.set(self.request, "last_bank_remittance_id", remittance_id)

    def _add_element(self, schema, attributes):
        logger.debug(" + Adding a new payment")
        self._before_add_edit(schema, attributes)
        payment_service = self.request.find_service(IPaymentRecordService)
        # Computing the resulting payment depending on what has already
        # been paid and the different TVA rates
        submitted_amount = attributes["amount"]
        payments = self.context.compute_payments(submitted_amount)
        for payment in payments:
            # Construire un nouvel appstruct correspondant
            tva_payment = {}
            # BaseTaskPayment fields
            tva_payment["date"] = attributes["date"]
            tva_payment["amount"] = payment["amount"]
            tva_payment["tva_id"] = payment["tva_id"]

            # Payment fields
            if "mode" in attributes:
                tva_payment["mode"] = attributes["mode"]
            if "bank_id" in attributes:
                tva_payment["bank_id"] = attributes.get("bank_id")
            if "bank_remittance_id" in attributes:
                tva_payment["bank_remittance_id"] = attributes["bank_remittance_id"]
            if "check_number" in attributes:
                tva_payment["check_number"] = attributes["check_number"]
            if "customer_bank_id" in attributes:
                tva_payment["customer_bank_id"] = attributes["customer_bank_id"]
            if "issuer" in attributes:
                tva_payment["issuer"] = attributes["issuer"]

            # Record the payment
            payment_service.add(self.context, tva_payment)

        self._after_add_edit(schema, attributes)

        # Notification et redirection
        self.notify()
        return self.context.payments

    def _edit_element(self, schema, attributes):
        logger.debug(" + Modifying an existing payment")
        self._before_add_edit(schema, attributes)

        payment_service = self.request.find_service(IPaymentRecordService)
        # update the payment
        payment = payment_service.update(self.context, attributes)
        self._after_add_edit(schema, attributes)
        self.session.flash("Votre paiement a bien été modifié")
        return payment


class InvoicePaymentDeleteView(BasePaymentDeleteView):
    def on_after_delete(self):
        self.context.parent.historize_paid_status(self.request.identity)

    def delete_payment(self):
        """
        Delete the payment instance from the database
        """
        # On fait appel au pyramid_service définit pour l'interface
        # IPaymentRecordService (voir pyramid_services)
        # Il est possible de changer de service en en spécifiant un autre dans
        # le fichier .ini de l'application
        invoice = self.context.invoice
        payment_service = self.request.find_service(IPaymentRecordService)
        payment_service.delete(self.context)
        return check_node_resulted(self.request, invoice)

    def parent_url(self, parent_id):
        """
        Parent url to use if a come_from parameter is missing

        :param int parent_id: The id of the parent object
        :returns: The url to redirect to
        :rtype: str
        """
        return self.request.route_path("/invoices/{id}/payment", id=parent_id)


class GenInversePaymentView(BaseFormView, PopupMixin):
    """
    Generate a payment canceling the original one (context)
    """

    title = "Annulation d'un encaissement"
    add_template_vars = ("help_message",)
    popup_force_reload = True

    @property
    def help_message(self):
        return (
            "Annulation de l'encaissement pour la facture "
            "{} d'un montant "
            "de {} €.<br />"
            "Veuillez saisir la date de l'encaissement correspondant.".format(
                self.context.task.official_number,
                format_amount(self.context.amount, precision=5),
            )
        )

    def get_schema(self):
        return get_cancel_payment_schema(self.request, self.context.invoice)

    def get_default_appstruct(self, attributes: dict):
        result = {
            "date": attributes.get("date", datetime.date.today()),
            "amount": -1 * self.context.amount,
            "tva_id": self.context.tva_id,
        }
        if not self.context.invoice.internal:
            for key in (
                "mode",
                "bank_id",
                "bank_remittance_id",
                "check_number",
                "customer_bank_id",
                "issuer",
            ):
                if hasattr(self.context, key):
                    result[key] = getattr(self.context, key)

        return result

    def redirect(self, appstruct=None) -> Response:
        if self.request.is_popup:
            self.add_popup_response()
            return self.request.response
        return HTTPFound(
            get_task_url(self.request, self.context.task, suffix="/payment")
        )

    def submit_success(self, attributes) -> Response:
        """
        Generate the new payment
        """
        logger.info("Generating an inverse payment")
        task = self.context.task
        ensure_task_pdf_persisted(task, self.request)
        payment_service = self.request.find_service(IPaymentRecordService)
        payment_data = self.get_default_appstruct(attributes)
        # Record the payment
        payment = payment_service.add(task, payment_data)
        logger.debug(f"Payment {payment} recorded")
        check_node_resulted(self.request, task)
        task.historize_paid_status(self.request.identity)
        self.request.dbsession.merge(task)
        return self.redirect(attributes)


def includeme(config):
    config.add_tree_view(
        InvoicePaymentView,
        parent=InvoicePaymentTabView,
        permission=PERMISSIONS["company.view"],
        renderer="/payment.mako",
        context=BaseTaskPayment,
    )
    config.add_tree_view(
        InvoicePaymentAddView,
        parent=InvoicePaymentTabView,
        permission=PERMISSIONS["context.add_payment_invoice"],
        renderer="base/vue_app.mako",
        layout="vue_opa",
        context=Invoice,
    )
    config.add_tree_view(
        InvoicePaymentEditView,
        parent=InvoicePaymentView,
        permission=PERMISSIONS["context.edit_payment"],
        renderer="base/vue_app.mako",
        request_param="action=edit",
        layout="vue_opa",
        context=BaseTaskPayment,
    )
    config.add_rest_service(
        InvoicePaymentRestView,
        collection_context=Invoice,
        collection_route_name=INVOICE_PAYMENT_API_COLLECTION,
        route_name=INVOICE_PAYMENT_API_ITEM_VIEW,
        context=BaseTaskPayment,
        add_rights=PERMISSIONS["context.add_payment_invoice"],
        edit_rights=PERMISSIONS["context.edit_payment"],
        delete_rights=PERMISSIONS["context.delete_payment"],
        view_rights=PERMISSIONS["company.view"],
    )
    config.add_view(
        InvoicePaymentRestView,
        attr="form_config",
        route_name=INVOICE_PAYMENT_API_COLLECTION,
        renderer="json",
        request_param="form_config",
        context=Invoice,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        InvoicePaymentRestView,
        attr="form_config",
        route_name=INVOICE_PAYMENT_API_ITEM_VIEW,
        renderer="json",
        request_param="form_config",
        context=BaseTaskPayment,
        permission=PERMISSIONS["context.edit_payment"],
    )

    config.add_view(
        InvoicePaymentRestView,
        attr="check_bank_remittance_id_view",
        route_name=INVOICE_PAYMENT_API_COLLECTION,
        renderer="json",
        request_param="check_bank_remittance_id",
        context=Invoice,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        InvoicePaymentRestView,
        attr="check_bank_remittance_id_view",
        route_name=INVOICE_PAYMENT_API_ITEM_VIEW,
        renderer="json",
        request_param="check_bank_remittance_id",
        context=BaseTaskPayment,
        permission=PERMISSIONS["context.edit_payment"],
    )
    config.add_view(
        InvoicePaymentDeleteView,
        route_name="payment",
        permission=PERMISSIONS["context.delete_payment"],
        request_param="action=delete",
        context=BaseTaskPayment,
    )
    config.add_view(
        GenInversePaymentView,
        route_name="payment",
        request_param="action=gen_inverse",
        permission=PERMISSIONS["context.gen_inverse_payment"],
        renderer="/base/formpage.mako",
        context=BaseTaskPayment,
    )
