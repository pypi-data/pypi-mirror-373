import logging
import datetime

from caerp.consts.permissions import PERMISSIONS
from collections import OrderedDict
from sqlalchemy import or_

from caerp.interfaces import (
    ITreasuryProducer,
    ITreasurySupplierPaymentWriter,
)
from caerp.models.company import Company
from caerp.models.export.accounting_export_log import (
    SupplierPaymentAccountingExportLogEntry,
)
from caerp.models.supply.internalpayment import InternalSupplierInvoiceSupplierPayment
from caerp.models.supply import (
    BaseSupplierInvoicePayment,
    SupplierInvoiceUserPayment,
    SupplierInvoice,
    SupplierInvoiceSupplierPayment,
)
from caerp.utils import strings
from caerp.utils.accounting import (
    check_company_accounting_configuration,
    check_user_accounting_configuration,
    check_waiver_accounting_configuration,
)
from caerp.utils.files import get_timestamped_filename
from caerp.utils.widgets import ViewLink
from caerp.views.admin.supplier.accounting import SUPPLIER_ACCOUNTING_URL
from caerp.views.company.tools import get_company_url
from caerp.views.export.utils import (
    get_supplier_payment_period_form,
    get_supplier_payment_all_form,
    get_supplier_payment_number_form,
    ACCOUNTING_EXPORT_TYPE_SUPPLIER_PAYMENTS,
)
from caerp.views.export import (
    BaseExportView,
)
from caerp.views.user.routes import USER_ACCOUNTING_URL


logger = logging.getLogger(__name__)


ERR_CONFIG = """Des éléments de configuration sont manquants pour exporter
les paiements des factures fournisseurs.
<br/>
<a href='{0}' target='_blank' title="Configurer le module Fournisseur dans une nouvelle fenêtre" aria-label="Configurer le module Fournisseur dans une nouvelle fenêtre">
Configuration comptable du module Fournisseur
</a>"""

ERR_COMPANY_CONFIG = """Un paiement de la facture fournisseur {0}
n'est pas exportable, le code analytique de l'enseigne {1} n'a pas été
configuré : 
<a onclick="window.openPopup('{2}');" href='#' title="Voir l’enseigne dans une nouvelle fenêtre" aria-label="Voir l’enseigne dans une nouvelle fenêtre">Voir l’enseigne</a>"""
ERR_USER_CONFIG = """Un paiement de la facture fournisseur {0}
n'est pas exportable, le compte tiers de l'entrepreneur {1} n'a pas été
configuré : 
<a onclick="window.openPopup('{2}');" href='#' title="Voir l’entrepreneur dans une nouvelle fenêtre" aria-label="Voir l’entrepreneur dans une nouvelle fenêtre">Voir l’entrepreneur</a>"""
ERR_BANK_CONFIG = """Un paiement de la facture fournisseur {0}
n'est pas exportable, le paiement n'est associé à aucune banque : 
<a onclick="window.openPopup('{1}');" href='#' title="Voir le paiement dans une nouvelle fenêtre" aria-label="Voir le paiement dans une nouvelle fenêtre">Voir le paiement</a>"""
ERR_WAIVER_CONFIG = """Le compte pour les abandons de créances n'a pas
été configuré : 
<a onclick="window.openPopup('{}');" href='#' title="Configurer le compte dans une nouvelle fenêtre" aria-label="Configurer le compte dans une nouvelle fenêtre">vous pouvez le configurer ici</a>
"""


class SingleSupplierPaymentExportPage(BaseExportView):
    writer_interface = ITreasurySupplierPaymentWriter

    def _populate_action_menu(self):
        self.request.actionmenu.add(
            ViewLink(
                label="Liste des factures fournisseurs",
                path="/supplier_invoices",
            )
        )

    def before(self):
        self._populate_action_menu()

    def validate_form(self, forms):
        return "", {}

    def query(self, query_params_dict, form_name):
        """
        Retrieve the exports we want to export
        """
        force = self.request.params.get("force", False)
        query = BaseSupplierInvoicePayment.query().with_polymorphic(
            [
                SupplierInvoiceSupplierPayment,
                SupplierInvoiceUserPayment,
                InternalSupplierInvoiceSupplierPayment,
            ]
        )
        query = query.filter(BaseSupplierInvoicePayment.id == self.context.id)
        if not force:
            query = query.filter(BaseSupplierInvoicePayment.exported == 0)
        return query

    def _check_config(self, payment_query):
        # On regarde si on doit checker la configuration des paiements internes
        has_internal = False
        if (
            payment_query.filter(
                BaseSupplierInvoicePayment.type_ == "internalsupplier_payment"
            ).count()
            > 0
        ):
            has_internal = True

        if not self.request.config.get("code_journal_frns"):
            logger.error("Error : Undefined key {}".format("code_journal_frns"))
            return False

        if has_internal:
            if not self.request.config.get("internalbank_general_account"):
                logger.error(
                    "Error : Undefined key {}".format("internalbank_general_account")
                )
                return False
            if not self.request.config.get("internalcode_journal_paiements_frns"):
                logger.error(
                    "Error : Undefined key {}".format(
                        "internalcode_journal_paiements_frns"
                    )
                )
                return False
        return True

    def _check_bank(self, supplier_payment):
        if not supplier_payment.bank:
            return False
        return True

    def check(self, supplier_payments):
        """
        Check that the given supplier_payments can be exported

        :param obj supplier_payments: A SQLA query of
        SupplierInvoiceSupplierPayment objects
        """
        count = supplier_payments.count()
        if count == 0:
            title = "Il n'y a aucun paiement fournisseur à exporter"
            res = {
                "title": title,
                "errors": [],
            }
            return False, res

        title = (
            "Vous vous apprêtez à exporter {0}             paiements"
            " fournisseurs".format(count)
        )
        res = {"title": title, "errors": []}

        if not self._check_config(supplier_payments):
            config_url = self.request.route_path(SUPPLIER_ACCOUNTING_URL)
            message = ERR_CONFIG.format(config_url)
            res["errors"].append(message)

        for payment in supplier_payments:
            supplier_invoice = payment.supplier_invoice
            company = supplier_invoice.company
            if not check_company_accounting_configuration(company):
                company_url = get_company_url(self.request, company, action="edit")
                message = ERR_COMPANY_CONFIG.format(
                    supplier_invoice.id,
                    company.name,
                    company_url,
                )
                res["errors"].append(message)
                continue

            if isinstance(payment, SupplierInvoiceUserPayment):
                user = supplier_invoice.payer
                if not check_user_accounting_configuration(self.request, user):
                    user_url = self.request.route_path(
                        USER_ACCOUNTING_URL,
                        id=user.id,
                        _query={"action": "edit"},
                    )
                    message = ERR_USER_CONFIG.format(
                        supplier_invoice.id,
                        strings.format_account(user),
                        user_url,
                    )
                    res["errors"].append(message)
                    continue
                if payment.waiver and not check_waiver_accounting_configuration(
                    self.request
                ):
                    admin_url = self.request.route_path(self.admin_route_name)
                    message = ERR_WAIVER_CONFIG.format(admin_url)
                    res["errors"].append(message)
                    continue

            if not payment.internal and not self._check_bank(payment):
                payment_url = self.request.route_path(
                    "supplier_payment",
                    id=payment.id,
                    _query={"action": "edit"},
                )
                message = ERR_BANK_CONFIG.format(supplier_invoice.id, payment_url)
                res["errors"].append(message)
                continue

        return len(res["errors"]) == 0, res

    def record_exported(self, supplier_payments, form_name, appstruct):
        """
        Record that those supplier_payments have already been exported
        """
        for payment in supplier_payments:
            logger.info(
                f"The supplier payment id : {payment.id} (supplier invoice id "
                f"{payment.supplier_invoice.id} / official number "
                f"{payment.supplier_invoice.official_number} ) "
                "has been exported"
            )
            payment.exported = True
            self.request.dbsession.merge(payment)

    def _collect_export_data(self, supplier_payments, appstruct=None):
        result = []
        for supplier_payment in supplier_payments:
            exporter = self.request.find_service(
                ITreasuryProducer, context=supplier_payment
            )
            result.extend(exporter.get_item_book_entries(supplier_payment))
        return result

    def record_export(self, supplier_payments, form_name, appstruct, export_file):
        export = SupplierPaymentAccountingExportLogEntry()
        export.user_id = self.request.identity.id
        export.export_file_id = export_file.id
        export.export_type = ACCOUNTING_EXPORT_TYPE_SUPPLIER_PAYMENTS

        for supplier_payment in supplier_payments:
            export.exported_supplier_payments.append(supplier_payment)

        self.request.dbsession.add(export)
        self.request.dbsession.flush()

    def get_filename(self, writer):
        return get_timestamped_filename("export_paiements_frn", writer.extension)


class SupplierPaymentExportPage(SingleSupplierPaymentExportPage):
    """
    Provide a supplier payment export page
    """

    title = "Export des écritures des paiements des factures fournisseurs"

    def get_forms(self):
        """
        Implement parent get_forms method
        """
        result = OrderedDict()
        all_form = get_supplier_payment_all_form(self.request)

        period_form = get_supplier_payment_period_form(self.request, all_form.counter)

        supplier_invoice_id_form = get_supplier_payment_number_form(
            self.request,
            all_form.counter,
        )

        for form in all_form, supplier_invoice_id_form, period_form:
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
        if antenne_id == -2:
            antenne_id = None

        query = query.outerjoin(SupplierInvoice)
        query = query.join(Company, SupplierInvoice.company_id == Company.id)
        query = query.filter(Company.antenne_id == antenne_id)

        return query

    def _filter_by_follower(self, query, query_params_dict):
        """
        Filter regarding the antenne of the User associated to the company
        that created the document. If no user associated to the company or
        multiple user it's not taken int account
        """
        if "follower_id" not in query_params_dict:
            return query

        follower_id = query_params_dict["follower_id"]
        if follower_id == -2:
            follower_id = None

        query = query.outerjoin(SupplierInvoice)
        query = query.join(Company, SupplierInvoice.company_id == Company.id)
        query = query.filter(Company.follower_id == follower_id)

        return query

    def _filter_by_doctypes(self, query, query_params_dict):
        doctypes = query_params_dict.get("doctypes")
        if doctypes == "internal":
            query = query.filter(
                BaseSupplierInvoicePayment.type_ == "internalsupplier_payment"
            )
        elif doctypes == "external":
            query = query.filter(
                BaseSupplierInvoicePayment.type_.in_(
                    ["supplier_payment", "supplier_invoice_user_payment"]
                )
            )
        return query

    def _filter_date(self, query, start_date, end_date):
        if end_date == datetime.date.today():
            query = query.filter(BaseSupplierInvoicePayment.date >= start_date)
        else:
            query = query.filter(
                BaseSupplierInvoicePayment.date.between(start_date, end_date)
            )
        return query

    def _filter_by_supplier_invoice_number(self, query, appstruct):
        """
        Add an id filter on the query
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if "official_number" in appstruct:
            query = query.filter(BaseSupplierInvoicePayment.supplier_invoice)
            query = query.filter(
                SupplierInvoice.official_number == appstruct["official_number"]
            )

        return query

    def _filter_by_exported(self, query, query_params_dict):
        if "exported" not in query_params_dict or not query_params_dict.get("exported"):
            query = query.filter(
                BaseSupplierInvoicePayment.exported == False  # noqa: E712
            )
        return query

    def _filter_by_issuer(self, query, appstruct):
        """
        Filter according to the issuer of the supplier payment
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if "issuer_id" in appstruct:
            query = query.filter(
                BaseSupplierInvoicePayment.user_id == appstruct["issuer_id"]
            )
        return query

    def _filter_by_mode(self, query, appstruct):
        """
        Filter according to the mode of the supplier payment
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if "mode" in appstruct:
            logger.debug(f"Filtering by mode {appstruct['mode']}")
            query = query.filter(
                or_(
                    SupplierInvoiceUserPayment.mode == appstruct["mode"],
                    SupplierInvoiceSupplierPayment.mode == appstruct["mode"],
                )
            )
        return query

    def _filter_by_bank_account(self, query, appstruct):
        if "bank_account" in appstruct:
            if appstruct["bank_account"] > 0:
                logger.debug("Filtering by bank_account: %s", appstruct["bank_account"])
                query = query.filter(
                    or_(
                        SupplierInvoiceUserPayment.bank_id == appstruct["bank_account"],
                        SupplierInvoiceSupplierPayment.bank_id
                        == appstruct["bank_account"],
                    )
                )
        return query

    def query(self, query_params_dict, form_name):
        """
        Retrieve the exports we want to export
        """
        query = BaseSupplierInvoicePayment.query().with_polymorphic(
            [
                SupplierInvoiceSupplierPayment,
                SupplierInvoiceUserPayment,
                InternalSupplierInvoiceSupplierPayment,
            ]
        )
        query = self._filter_by_doctypes(query, query_params_dict)
        if form_name == "period_form":
            start_date = query_params_dict["start_date"]
            end_date = query_params_dict["end_date"]
            query = self._filter_date(query, start_date, end_date)

        elif form_name == "official_number_form":
            query = self._filter_by_supplier_invoice_number(query, query_params_dict)

        query = self._filter_by_exported(query, query_params_dict)
        query = self._filter_by_issuer(query, query_params_dict)
        query = self._filter_by_antenne(query, query_params_dict)
        query = self._filter_by_follower(query, query_params_dict)
        query = self._filter_by_mode(query, query_params_dict)
        query = self._filter_by_bank_account(query, query_params_dict)
        return query

    def validate_form(self, forms):
        return BaseExportView.validate_form(self, forms)


def add_routes(config):
    config.add_route(
        "/export/treasury/supplier_payments",
        "/export/treasury/supplier_payments",
    )
    config.add_route(
        "/export/treasury/supplier_payments/{id}",
        "/export/treasury/supplier_payments/{id}",
        traverse="/supplier_payments/{id}",
    )


def add_views(config):
    config.add_view(
        SingleSupplierPaymentExportPage,
        route_name="/export/treasury/supplier_payments/{id}",
        renderer="/export/main.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        SupplierPaymentExportPage,
        route_name="/export/treasury/supplier_payments",
        renderer="/export/main.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )


def includeme(config):
    add_routes(config)
    add_views(config)
    config.add_admin_menu(
        parent="accounting",
        order=5,
        label="Export des paiements de facture fournisseur",
        href="/export/treasury/supplier_payments",
        permission=PERMISSIONS["global.manage_accounting"],
    )
