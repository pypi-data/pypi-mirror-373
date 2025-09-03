import logging
from collections import OrderedDict

from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound

from caerp.consts.permissions import PERMISSIONS
from caerp.interfaces import (
    ITreasuryGroupper,
    ITreasuryPaymentWriter,
    ITreasuryProducer,
)
from caerp.models.export.accounting_export_log import PaymentAccountingExportLogEntry
from caerp.models.task import (
    BankRemittance,
    BaseTaskPayment,
    InternalPayment,
    Payment,
    Task,
)
from caerp.utils.accounting import check_customer_accounting_configuration
from caerp.utils.compat import Iterable
from caerp.utils.files import get_timestamped_filename
from caerp.utils.widgets import Link, ViewLink
from caerp.views.accounting.routes import BANK_REMITTANCE_ROUTE
from caerp.views.admin.sale.accounting.receipts import RECEIPT_CONFIG_URL, RECEIPT_URL
from caerp.views.export import BaseExportView
from caerp.views.export.utils import (
    ACCOUNTING_EXPORT_TYPE_PAYMENTS,
    get_invoice_number_form,
    get_payment_all_form,
    get_payment_period_form,
    query_invoices_for_export,
)
from caerp.views.invoices.routes import INVOICE_COLLECTION_ROUTE
from caerp.views.third_party.customer.routes import CUSTOMER_ITEM_ROUTE

logger = logging.getLogger(__name__)


PAYMENT_VOID_ERROR_MSG = "Il n'y a aucun encaissement à exporter"

PAYMENT_CUSTOMER_ERROR_MSG = """Un encaissement de la facture {0} n'est pas
exportable : Des informations sur le client {1} (compte général ou compte tiers) sont
manquantes
 <a href='#' onclick="window.openPopup('{2}')" title="Voir le client dans une nouvelle fenêtre" aria-label="Voir le client dans une nouvelle fenêtre">Voir le client</a>"""

PAYMENT_BANK_ERROR_MSG = """Un encaissement de la facture {0}
n'est pas exportable : L'encaissement n'est associé à aucune banque
<a href='#' onclick="window.openPopup('{1}')" title="Voir l'encaissement dans une nouvelle fenêtre" aria-label="Voir l'encaissement dans une nouvelle fenêtre">Voir l’encaissement</a>"""

PAYMENT_REMITTANCE_INFO_MSG = """Les encaissements associés à une remise en
banque non clôturée ne seront pas exportées en comptabilité.<br/><br/>
<a href='{}'target='_blank' title="Voir les remises ouvertes dans une nouvelle fenêtre" aria-label="Voir les remises ouvertes dans une nouvelle fenêtre">Voir les remises ouvertes</a>"""

INTERNAL_BANK_ERROR_MSG = """
Le compte banque des encaissements internes n'a pas été configuré.
<a href='#' onclick="window.openPopup('{}')" title="Voir la configuration des encaissements internes dans une nouvelle fenêtre" aria-label="Voir l'encaissement dans une nouvelle fenêtre">Configurer</a>
"""


class SinglePaymentExportPage(BaseExportView):
    """View used to export a single payment"""

    admin_route_name = RECEIPT_URL
    writer_interface = ITreasuryPaymentWriter

    @property
    def title(self):
        return "Export des écritures pour l'encaissement de la facture {}".format(
            self.context.task.official_number
        )

    def _populate_action_menu(self):
        """
        Add a back button to the action menu
        """
        if "come_from" in self.request.params:
            url = self.request.params["come_from"]
            title = "Retour à la page précédente"
        else:
            url = self.request.route_path("payment", id=self.context.id)
            title = "Retour à l'encaissement"
        self.request.actionmenu.add(
            Link(
                url=url,
                label="Retour",
                title=title,
                icon=None,
                css="",
            )
        )

    def before(self):
        self._populate_action_menu()

    def validate_form(self, forms):
        return "", {}

    def query(self, appstruct, formname):
        # NB : on a une query alors que le contexte fourni déjà l'objet
        # Mais on en a besoin pour satisfaire la BaseExportView
        force = self.request.params.get("force", False)
        query = BaseTaskPayment.query().with_polymorphic([Payment, InternalPayment])
        query = query.filter(BaseTaskPayment.id == self.context.id)
        if not force:
            query = query.filter(BaseTaskPayment.exported == 0)
        return query

    def _check_bank(self, payment):
        if payment.bank is None:
            return False
        return True

    def check(self, payments):
        """
        Check that the given payments are 'exportable'
        :param obj payments: a SQLA query of BaseTaskPayments
        """
        count = payments.count()
        if count == 0:
            res = {
                "title": PAYMENT_VOID_ERROR_MSG,
                "errors": [],
            }
            return False, res

        title = "Vous vous apprêtez à exporter {0} encaissements".format(count)
        res = {"title": title, "errors": []}
        for payment in payments:
            invoice = payment.invoice

            # CHECK CUSTOMER
            if not check_customer_accounting_configuration(
                self.request, invoice.customer, invoice
            ):
                customer_url = self.request.route_path(
                    CUSTOMER_ITEM_ROUTE,
                    id=invoice.customer.id,
                    _query={"action": "edit"},
                )
                message = PAYMENT_CUSTOMER_ERROR_MSG.format(
                    invoice.official_number, invoice.customer.label, customer_url
                )
                res["errors"].append(message)
                continue

            # CHECK BANK
            if not payment.internal:
                if not self._check_bank(payment):
                    payment_url = self.request.route_path(
                        "payment", id=payment.id, _query={"action": "edit"}
                    )
                    message = PAYMENT_BANK_ERROR_MSG.format(
                        invoice.official_number, payment_url
                    )
                    res["errors"].append(message)
                    continue
            else:
                if not bool(self.request.config.get("internalbank_general_account")):
                    url = self.request.route_path(RECEIPT_CONFIG_URL)
                    message = INTERNAL_BANK_ERROR_MSG.format(url)
                    res["errors"].append(message)
                    continue

        return len(res["errors"]) == 0, res

    def record_exported(self, payments, form_name, appstruct):
        for payment in payments:
            logger.info(
                "The payment id : {0} (invoice {1} id:{2}) has been exported".format(
                    payment.id,
                    payment.invoice.official_number,
                    payment.invoice.id,
                )
            )
            payment.exported = True
            self.request.dbsession.merge(payment)

    def _collect_export_data(self, payments, appstruct=None) -> Iterable[dict]:
        """
        Produce the data to export
        """
        result = []
        for payment in payments:
            exporter = self.request.find_service(ITreasuryProducer, context=payment)
            result.extend(exporter.get_item_book_entries(payment))
        return self._group_export_data(result)

    def _group_export_data(self, data):
        """
        Group Payment export data following the associated grouping rule

        """
        Groupper = self.request.find_service_factory(
            ITreasuryGroupper, context=BaseTaskPayment
        )
        groupper = Groupper(self.context, self.request)
        return groupper.group_items(data)

    def record_export(self, payments, form_name, appstruct, export_file):
        export = PaymentAccountingExportLogEntry()
        export.user_id = self.request.identity.id
        export.export_file_id = export_file.id
        export.export_type = ACCOUNTING_EXPORT_TYPE_PAYMENTS

        for payment in payments:
            export.exported_payments.append(payment)

        self.request.dbsession.add(export)
        self.request.dbsession.flush()

    def get_filename(self, writer):
        return get_timestamped_filename("export_encaissement", writer.extension)


class PaymentExportPage(SinglePaymentExportPage):
    """
    Provide a sage export view compound of multiple forms for payment exports
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help_message = None

    @property
    def title(self):
        return "Export des écritures des encaissements"

    def _populate_action_menu(self):
        self.request.actionmenu.add(
            ViewLink(
                label="Liste des factures",
                path=INVOICE_COLLECTION_ROUTE,
            )
        )

    def before(self):
        if self.request.has_module("accounting"):
            self.help_message = PAYMENT_REMITTANCE_INFO_MSG.format(
                self.request.route_path(
                    BANK_REMITTANCE_ROUTE, _query=dict(__formid__="deform")
                )
            )

    def get_forms(self):
        """
        Return the different payment search forms
        """
        result = OrderedDict()
        all_form = get_payment_all_form(self.request)
        period_form = get_payment_period_form(self.request, all_form.counter)

        number_form = get_invoice_number_form(
            self.request,
            all_form.counter,
            title="Exporter les encaissements depuis des numéros de factures",
        )

        for form in all_form, number_form, period_form:
            result[form.formid] = {"form": form, "title": form.schema.title}

        return result

    def _filter_by_antenne(self, query, query_params_dict):
        """
        Filter regarding the antenne of the User associated to the company
        that created the document. If no user associated to the company or
        multiple user it's not taken int account
        """
        if "antenne_id" not in query_params_dict:
            return query

        antenne_id = query_params_dict["antenne_id"]
        query = Task.query_by_antenne_id(antenne_id, query, payment=True)

        return query

    def _filter_by_follower(self, query, query_params_dict):
        """
        Filter regarding the follower of the User associated to the company
        that created the document. If no user associated to the company or
        multiple user it's not taken int account
        """
        if "follower_id" not in query_params_dict:
            return query

        follower_id = query_params_dict["follower_id"]
        query = Task.query_by_follower_id(follower_id, query, payment=True)

        return query

    def _filter_doctypes(self, query, doctypes):
        if doctypes == "internal":
            query = query.filter_by(type_="internalpayment")
        elif doctypes == "external":
            query = query.filter_by(type_="payment")
        return query

    def _filter_date(self, query, start_date, end_date):
        return query.filter(BaseTaskPayment.date.between(start_date, end_date))

    def _filter_number(self, query, start, end, year, doctypes):
        filters = dict(
            start_number=start,
            end_number=end,
            year=year,
            doctypes=doctypes,
        )
        try:
            task_query = query_invoices_for_export(**filters)
            task_ids = [t.id for t in task_query]
        except MultipleResultsFound:
            self.request.session.flash(
                "Votre filtre n'est pas assez précis, plusieurs factures "
                "portent le même numéro, veuillez spécifier une année"
            )
            task_ids = []

        return query.filter(BaseTaskPayment.task_id.in_(task_ids))

    def _filter_open_remittances(self, query):
        br_query = self.request.dbsession.query(BankRemittance.id)
        br_query = br_query.filter(BankRemittance.closed == 0)
        open_br_ids = [item[0] for item in br_query]
        return query.filter(
            or_(
                Payment.bank_remittance_id.notin_(open_br_ids),
                Payment.bank_remittance_id == None,  # noqa: E711
                BaseTaskPayment.type_ == "internal",
            )
        )

    def _filter_by_issuer(self, query, query_params_dict):
        if "issuer_id" in query_params_dict:
            issuer_id = query_params_dict["issuer_id"]
            query = query.filter(BaseTaskPayment.user_id == issuer_id)

        return query

    def _filter_by_mode(self, query, query_params_dict):
        if "mode" in query_params_dict:
            logger.debug("Filtering by mode: %s", query_params_dict["mode"])
            query = query.filter(Payment.mode == query_params_dict["mode"])
        return query

    def _filter_by_bank_account(self, query, query_params_dict):
        if "bank_account" in query_params_dict:
            if query_params_dict["bank_account"] > 0:
                logger.debug(
                    "Filtering by bank_account: %s", query_params_dict["bank_account"]
                )
                query = query.filter(
                    Payment.bank_id == query_params_dict["bank_account"]
                )
        return query

    def query(self, query_params_dict, form_name):
        # NB : si on veut exporter les paiements internes, il faut le gérer ici
        query = BaseTaskPayment.query().with_polymorphic([Payment, InternalPayment])
        query = self._filter_open_remittances(query)

        if form_name == "period_form":
            start_date = query_params_dict["start_date"]
            end_date = query_params_dict["end_date"]
            query = self._filter_date(query, start_date, end_date)
            query = self._filter_doctypes(query, query_params_dict["doctypes"])

        elif form_name == "invoice_number_form":
            start = query_params_dict["start"]
            end = query_params_dict["end"]
            financial_year = query_params_dict["financial_year"]
            query = self._filter_number(
                query, start, end, financial_year, query_params_dict["doctypes"]
            )
        else:
            query = self._filter_doctypes(query, query_params_dict["doctypes"])

        if "exported" not in query_params_dict or not query_params_dict.get("exported"):
            query = query.filter(
                BaseTaskPayment.exported == False  # noqa: E712
            )  # noqa: E712

        query = self._filter_by_issuer(query, query_params_dict)
        query = self._filter_by_antenne(query, query_params_dict)
        query = self._filter_by_follower(query, query_params_dict)
        query = self._filter_by_mode(query, query_params_dict)
        query = self._filter_by_bank_account(query, query_params_dict)
        return query

    def validate_form(self, forms):
        return BaseExportView.validate_form(self, forms)


def add_routes(config):
    config.add_route("/export/treasury/payments", "/export/treasury/payments")
    config.add_route(
        "/export/treasury/payments/{id}",
        "/export/treasury/payments/{id}",
        traverse="/base_task_payments/{id}",
    )


def add_views(config):
    config.add_view(
        SinglePaymentExportPage,
        route_name="/export/treasury/payments/{id}",
        renderer="/export/single.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )

    config.add_view(
        PaymentExportPage,
        route_name="/export/treasury/payments",
        renderer="/export/main.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )


def includeme(config):
    add_routes(config)
    add_views(config)

    config.add_admin_menu(
        parent="accounting",
        order=1,
        label="Export des encaissements",
        href="/export/treasury/payments",
        permission=PERMISSIONS["global.manage_accounting"],
    )
