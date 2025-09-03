import logging

from caerp.consts.permissions import PERMISSIONS
from collections import OrderedDict

from caerp.interfaces import (
    ITreasuryProducer,
    ITreasurySupplierInvoiceWriter,
)
from caerp.models.company import Company
from caerp.models.export.accounting_export_log import (
    SupplierInvoiceAccountingExportLogEntry,
)
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.utils.accounting import check_company_accounting_configuration
from caerp.utils.files import get_timestamped_filename
from caerp.utils.widgets import ViewLink
from caerp.views.admin.supplier.accounting import SUPPLIER_ACCOUNTING_URL
from caerp.views.admin.supplier.accounting.supplier_invoice import (
    CONFIG_URL as SUPPLIER_CONFIG_URL,
)
from caerp.views.admin.supplier.accounting.internalsupplier_invoice import (
    CONFIG_URL as INTERNALSUPPLIER_CONFIG_URL,
)
from caerp.views.company.tools import get_company_url
from caerp.views.export import BaseExportView
from caerp.views.export.utils import (
    get_supplier_invoice_all_form,
    get_supplier_invoice_number_form,
    get_supplier_invoice_form,
    get_supplier_invoice_period_form,
    ACCOUNTING_EXPORT_TYPE_SUPPLIER_INVOICES,
)
from caerp.views.supply.invoices.routes import ITEM_ROUTE


logger = logging.getLogger(__name__)

CONFIG_ERROR_MSG = """Des éléments de configuration sont manquants pour
exporter les factures fournisseurs.
<br/>
<a href='{0}' target='_blank' title="Configurer le module Fournisseur dans une nouvelle fenêtre" aria-label="Configurer le module Fournisseur dans une nouvelle fenêtre">
    Configuration comptable du module Fournisseur
</a>"""
COMPANY_ERROR_MSG = """Le code analytique de l'enseigne {0} n'a pas été
configuré : 
<a onclick="window.openPopup('{1}');" href='#' title="Voir l’enseigne dans une nouvelle fenêtre" aria-label="Voir l’enseigne dans une nouvelle fenêtre">Voir l’enseigne</a>"""

SUPPLIER_ERROR_MSG = """Le document 
 <a target="_blank" href="{invoice_url}" title="Ce document s’ouvrira dans une nouvelle fenêtre" aria-label="Ce document s’ouvrira dans une nouvelle fenêtre"> {official_number}</a> n'est pas exportable : 
impossible de déterminer le compte général client à utiliser.

Il peut être configuré à différents niveaux :
<a onclick="window.openPopup('{supplier_url}');" href='#' title="Voir le fournisseur dans une nouvelle fenêtre" aria-label="Voir le fournisseur dans une nouvelle fenêtre">
Fournisseur {supplier_label}</a> /
<a onclick="window.openPopup('{company_url}');" href='#' title="Voir l’enseigne dans une nouvelle fenêtre" aria-label="Voir l’enseigne dans une nouvelle fenêtre">
Enseigne {company_label}</a> /
<a onclick="window.openPopup('{admin_url}');" href='#' title="Voir la CAE dans une nouvelle fenêtre" aria-label="Voir la CAE dans une nouvelle fenêtre">
CAE</a>.
"""

ETYPE_ERROR_MSG = """La facture {} n'est pas exportable, des types de dépense
sont manquants : 
<a onclick="window.openPopup('{}');" href='#' title="Configurer les types manquants dans une nouvelle fenêtre" aria-label="Configurer les types manquants dans une nouvelle fenêtre">
    Configurer les types manquants
</a>"""


class SageSupplierInvoiceExportPage(BaseExportView):
    """
    Sage SupplierInvoice export views
    """

    title = "Export des écritures des factures fournisseurs"
    config_keys = (
        "code_journal_frns",
        "internalcode_journal_frns",
    )
    writer_interface = ITreasurySupplierInvoiceWriter

    def _populate_action_menu(self):
        self.request.actionmenu.add(
            ViewLink(
                label="Liste des factures fournisseur",
                path="/supplier_invoices",
            )
        )

    def before(self):
        self._populate_action_menu()

    def _get_forms(self):
        """
        Generate forms for the given parameters

        :returns: A dict with forms in it
            {formid: {'form': form, title:formtitle}}
        :rtype: OrderedDict
        """
        result = OrderedDict()

        all_form = get_supplier_invoice_all_form(self.request)
        main_form = get_supplier_invoice_form(self.request, all_form.counter)
        id_form = get_supplier_invoice_number_form(
            self.request,
            all_form.counter,
            title="Exporter les factures fournisseurs depuis un identifiant",
        )
        period_form = get_supplier_invoice_period_form(self.request, all_form.counter)

        for form in all_form, main_form, id_form, period_form:
            result[form.formid] = {"form": form, "title": form.schema.title}

        return result

    def get_forms(self):
        """
        Implement parent get_forms method
        """
        result = self._get_forms()
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

        query = query.join(Company, SupplierInvoice.company_id == Company.id)
        query = query.filter(Company.antenne_id == antenne_id)

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
        if follower_id == -2:
            follower_id = None

        query = query.join(Company, SupplierInvoice.company_id == Company.id)
        query = query.filter(Company.follower_id == follower_id)

        return query

    def _filter_by_supplier_invoice_number(self, query, appstruct):
        """
        Add an id filter on the query
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        number = appstruct["official_number"]
        return query.filter(SupplierInvoice.official_number == number)

    def _filter_by_company(self, query, appstruct):
        """
        Add a filter on the company_id
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if appstruct.get("company_id", 0) != 0:
            company_id = appstruct["company_id"]
            query = query.filter(SupplierInvoice.company_id == company_id)
        return query

    def _filter_by_exported(self, query, appstruct):
        """
        Add a filter on the exported status
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if not appstruct.get("exported"):
            query = query.filter_by(exported=False)
        return query

    def _filter_by_doctypes(self, query, appstruct):
        doctypes = appstruct.get("doctypes")
        if doctypes == "internal":
            query = query.filter_by(type_="internalsupplier_invoice")
        elif doctypes == "external":
            query = query.filter_by(type_="supplier_invoice")
        return query

    def _filter_by_validator(self, query, appstruct):
        if "validator_id" in appstruct:
            validator_id = appstruct["validator_id"]
            query = query.filter(SupplierInvoice.status_user_id == validator_id)
        return query

    def _filter_date(self, query, start_date, end_date):
        return query.filter(SupplierInvoice.date.between(start_date, end_date))

    def query(self, appstruct, form_name):
        """
        Base Query for supplier invoices
        :param appstruct: params passed in the query for the export
        :param str form_name: The submitted form's name
        """
        query = SupplierInvoice.query()
        query = query.filter(SupplierInvoice.status == "valid")
        query = self._filter_by_doctypes(query, appstruct)

        if form_name == "official_number_form":
            query = self._filter_by_supplier_invoice_number(query, appstruct)

        elif form_name == "main_form":
            query = self._filter_by_company(query, appstruct)

        elif form_name == "period_form":
            start_date = appstruct["start_date"]
            end_date = appstruct["end_date"]
            query = self._filter_date(query, start_date, end_date)

        query = self._filter_by_exported(query, appstruct)
        query = self._filter_by_validator(query, appstruct)
        query = self._filter_by_antenne(query, appstruct)
        query = self._filter_by_follower(query, appstruct)
        return query

    def _check_config(self, config):
        """
        Check all configuration values are set for export

        :param config: The application configuration dict
        """
        logger.debug(" + Checking configuration keys")
        for key in self.config_keys:
            if not config.get(key):
                logger.debug(f"   - error : {key} : Undefined config value")
                return False
        return True

    def _check_company(self, company):
        if not check_company_accounting_configuration(company):
            company_url = get_company_url(self.request, company, action="edit")
            return COMPANY_ERROR_MSG.format(company.name, company_url)
        return None

    def _check_supplier(self, supplier, invoice):
        """
        Check the invoice's supplier is configured for exports
        """
        prefix = ""
        if invoice.internal:
            prefix = "internal"
        if self.request.config.get_value(
            "thirdparty_account_mandatory_supplier", False, bool
        ):
            if not supplier.get_third_party_account(prefix):
                invoice_url = self.request.route_path(
                    ITEM_ROUTE, id=invoice.id, _query={"action": "edit"}
                )
                supplier_url = self.request.route_path(
                    "supplier", id=supplier.id, _query={"action": "edit"}
                )
                company_url = get_company_url(
                    self.request, invoice.company, action="edit"
                )

                if invoice.internal:
                    admin_url = self.request.route_path(INTERNALSUPPLIER_CONFIG_URL)
                else:
                    admin_url = self.request.route_path(SUPPLIER_CONFIG_URL)

                message = SUPPLIER_ERROR_MSG.format(
                    official_number=invoice.official_number,
                    supplier_label=invoice.supplier_label,
                    company_label=invoice.company.name,
                    invoice_url=invoice_url,
                    supplier_url=supplier_url,
                    company_url=company_url,
                    admin_url=admin_url,
                )
                return message

        return None

    def _check_lines(self, invoice):
        error = None
        for line in invoice.lines:
            if line.expense_type is None:
                url = self.request.route_path(
                    "/supplier_invoices/{id}/set_types", id=invoice.id
                )
                error = ETYPE_ERROR_MSG.format(invoice.official_number, url)
                break
        return error

    def check(self, supplier_invoices):
        """
        Check if we can export the supplier_invoices

        :param supplier_invoices: the supplier_invoices to export
        :returns: a 2-uple (is_ok, messages)
        """
        count = supplier_invoices.count()
        if count == 0:
            title = "Il n'y a aucune facture fournisseur à exporter"
            res = {"title": title, "errors": []}
            return False, res

        title = "Vous vous apprêtez à exporter {0} \
            factures fournisseurs".format(
            count
        )
        errors = []

        if not self._check_config(self.request.config):
            errors.append(CONFIG_ERROR_MSG.format(SUPPLIER_ACCOUNTING_URL))

        for invoice in supplier_invoices:
            company = invoice.company
            error = self._check_company(company)
            if error is not None:
                errors.append(
                    "La facture fournisseur de {0} n'est pas exportable "
                    "<br />{1}".format(invoice.company.name, error)
                )

            error = self._check_lines(invoice)
            if error is not None:
                errors.append(error)

            supplier = invoice.supplier
            error = self._check_supplier(supplier, invoice)
            if error is not None:
                errors.append(error)

        res = {"title": title, "errors": errors}

        return len(errors) == 0, res

    def record_exported(self, supplier_invoices, form_name, appstruct):
        """
        Tag the exported supplier_invoices

        :param supplier_invoices: The supplier_invoices we are exporting
        """
        for supplier_invoice in supplier_invoices:
            logger.info(
                f"The supplier invoice with id {supplier_invoice.id} / "
                f"official number {supplier_invoice.official_number} "
                "has been exported"
            )
            supplier_invoice.exported = True

            self.request.dbsession.merge(supplier_invoice)

    def _collect_export_data(self, supplier_invoices, appstruct=None):
        result = []
        for supplier_invoice in supplier_invoices:
            exporter = self.request.find_service(
                ITreasuryProducer, context=supplier_invoice
            )
            result.extend(exporter.get_item_book_entries(supplier_invoice))
        return result

    def record_export(self, supplier_invoices, form_name, appstruct, export_file):
        export = SupplierInvoiceAccountingExportLogEntry()
        export.user_id = self.request.identity.id
        export.export_file_id = export_file.id
        export.export_type = ACCOUNTING_EXPORT_TYPE_SUPPLIER_INVOICES

        for supplier_invoice in supplier_invoices:
            export.exported_supplier_invoices.append(supplier_invoice)

        self.request.dbsession.add(export)
        self.request.dbsession.flush()

    def get_filename(self, writer):
        return get_timestamped_filename("export_factures_frn", writer.extension)


def add_routes(config):
    config.add_route(
        "/export/treasury/supplier_invoices", "/export/treasury/supplier_invoices"
    )
    config.add_route(
        "/export/treasury/supplier_invoices/{id}",
        "/export/treasury/supplier_invoices/{id}",
    )


def add_views(config):
    config.add_view(
        SageSupplierInvoiceExportPage,
        route_name="/export/treasury/supplier_invoices",
        renderer="/export/main.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )


def includeme(config):
    add_routes(config)
    add_views(config)
    config.add_admin_menu(
        parent="accounting",
        order=4,
        label="Export des factures fournisseurs",
        href="/export/treasury/supplier_invoices",
        permission=PERMISSIONS["global.manage_accounting"],
    )
