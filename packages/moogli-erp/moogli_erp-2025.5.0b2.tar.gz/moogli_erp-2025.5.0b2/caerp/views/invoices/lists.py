"""
    Company invoice list view
"""
import logging
import datetime
import colander

from caerp.consts.permissions import PERMISSIONS
from beaker.cache import cache_region
from deform import Form
from sqlalchemy import (
    func,
    or_,
    distinct,
)
from sqlalchemy.orm import (
    aliased,
    contains_eager,
    load_only,
)

from caerp_base.models.base import DBSESSION

from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import (
    export_to_file,
    export_invoices_details_to_file,
)

from .routes import INVOICE_COLLECTION_ROUTE
from caerp.export.utils import write_file_to_request
from caerp.export.task_pdf import task_bulk_pdf
from caerp.forms.tasks.invoice import (
    get_list_schema,
    get_pdf_export_schema,
)
from caerp.models.task import (
    Task,
    Invoice,
    CancelInvoice,
    BaseTaskPayment,
    Payment,
)
from caerp.models.third_party.customer import Customer
from caerp.models.company import Company
from caerp.utils.widgets import (
    Link,
    ViewLink,
)
from caerp.views.export.utils import find_task_status_date
from caerp.views import (
    AsyncJobMixin,
    BaseListView,
    submit_btn,
)
from caerp.views.company.routes import COMPANY_INVOICE_ADD_ROUTE, COMPANY_INVOICES_ROUTE

logger = log = logging.getLogger(__name__)


# Here we do some multiple function stuff to allow caching to work
# Beaker caching is done through signature (dbsession is changing each time, so
# it won't cache if it's an argument of the cached function
def get_taskdates(dbsession):
    """
    Return all taskdates
    """

    @cache_region("long_term", "taskdates")
    def taskdates():
        """
        Cached version
        """
        return dbsession.query(distinct(Invoice.financial_year))

    return taskdates()


def get_years(dbsession):
    """
    We consider that all documents should be dated after 2000
    """
    inv = get_taskdates(dbsession)

    @cache_region("long_term", "taskyears")
    def years():
        """
        cached version
        """
        return [invoice[0] for invoice in inv.all()]

    return years()


def get_year_range(year):
    """
    Return the first january of the current and the next year
    """
    fday = datetime.date(year, 1, 1)
    lday = datetime.date(year + 1, 1, 1)
    return fday, lday


def filter_all_status(self, query, appstruct):
    """
    Filter the invoice by status
    """
    status = appstruct.get("status", "all")
    if status != "all":
        logger.info("  + Status filtering : %s" % status)
        query = query.filter(Task.status == status)

    return query


class InvoiceListTools:
    title = "Factures de la CAE"
    sort_columns = dict(
        date=Task.date,
        internal_number=Task.internal_number,
        customer=Customer.name,
        company=Company.name,
        official_number=Task.status_date,
        ht=Task.ht,
        ttc=Task.ttc,
        tva=Task.tva,
        payment="latest_payment_date",
    )

    default_sort = "official_number"
    default_direction = "desc"

    # Is it a CAE level view
    is_admin = True
    # Do we want to exclude more fields (used in company level views)
    fields_to_exclude = ()

    def get_schema(self):
        return get_list_schema(
            self.request, is_global=self.is_admin, excludes=self.fields_to_exclude
        )

    def query(self):
        payment_subquery = aliased(
            BaseTaskPayment,
            DBSESSION.query(
                BaseTaskPayment,
                func.Max(BaseTaskPayment.date).label("latest_payment_date"),
            )
            .group_by(BaseTaskPayment.task_id)
            .subquery(),
        )
        cancelinvoices_subquery = aliased(
            CancelInvoice,
            DBSESSION.query(CancelInvoice)
            .options(load_only("official_number", "ttc", "date"))
            .filter(CancelInvoice.status == "valid")
            .group_by(CancelInvoice.invoice_id)
            .subquery(),
        )

        query = DBSESSION().query(Task)
        query = query.with_polymorphic([Invoice, CancelInvoice])
        query = query.outerjoin(Task.customer)
        query = query.outerjoin(Task.company)
        query = query.outerjoin(payment_subquery)
        query = query.outerjoin(
            cancelinvoices_subquery, Task.id == cancelinvoices_subquery.invoice_id
        )
        query = query.options(
            contains_eager(Task.customer).load_only(
                Customer.company_name,
                Customer.code,
                Customer.id,
                Customer.firstname,
                Customer.lastname,
                Customer.civilite,
                Customer.type,
            )
        )
        query = query.options(
            contains_eager(Task.company).load_only(
                Company.name,
                Company.id,
            )
        )
        query = query.options(
            load_only(
                "_acl",
                "name",
                "date",
                "id",
                "ht",
                "tva",
                "ttc",
                "company_id",
                "customer_id",
                "official_number",
                "internal_number",
                "status",
                Invoice.paid_status,
            )
        )
        return query

    def _get_company_id(self, appstruct):
        """
        Return the company_id found in the appstruct
        Should be overriden if we want a company specific list view
        """
        res = appstruct.get("company_id")
        logger.debug("Company id : %s" % res)
        return res

    def filter_company(self, query, appstruct):
        company_id = self._get_company_id(appstruct)
        if company_id not in (None, colander.null):
            query = query.filter(Task.company_id == company_id)
        return query

    def filter_official_number(self, query, appstruct):
        number = appstruct["search"]
        if number and number != -1:
            logger.debug("    Filtering by official_number : %s" % number)
            query = query.filter(Task.official_number.like("%" + number + "%"))
        return query

    def filter_ttc(self, query, appstruct):
        ttc = appstruct.get("ttc", {})
        if ttc.get("start") not in (None, colander.null):
            log.info("Filtering by ttc amount : %s" % ttc)
            start = ttc.get("start")
            end = ttc.get("end")
            if end in (None, colander.null):
                query = query.filter(Task.ttc >= start)
            else:
                query = query.filter(Task.ttc.between(start, end))
        return query

    def filter_customer(self, query, appstruct):
        customer_id = appstruct.get("customer_id")
        if customer_id not in (None, colander.null):
            logger.debug("Customer id : %s" % customer_id)
            query = query.filter(Task.customer_id == customer_id)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id", None)
        if antenne_id not in (None, "", colander.null):
            logger.debug("  + Filtering on antenne_id")
            query = query.filter(Company.antenne_id == antenne_id)
        return query

    def filter_date(self, query, appstruct):
        logger.debug(" + Filtering date")

        year = appstruct.get("year", -1)
        if year not in (-1, colander.null):
            try:
                start = datetime.date(year, 1, 1)
                end = datetime.date(year, 12, 31)
                query = query.filter(Task.date.between(start, end))
                logger.debug("    Year : %s" % year)
            except:
                logger.debug("    Unable to filter by year : %s is invalid" % year)

        period = appstruct.get("period", {})
        if period.get("start") not in (None, colander.null):
            start = period.get("start")
            end = period.get("end")
            if end in (None, colander.null):
                end = datetime.date.today()
            query = query.filter(Task.date.between(start, end))

            logger.debug("    Between %s and %s" % (start, end))

        financial_year = appstruct.get("financial_year", -1)
        if financial_year not in (-1, colander.null):
            query = query.filter(
                or_(
                    Invoice.financial_year == financial_year,
                    CancelInvoice.financial_year == financial_year,
                )
            )
            logger.debug("    Financial year : %s" % financial_year)
        return query

    def filter_status(self, query, appstruct):
        """
        Filter the status a first time (to be overriden)
        """
        logger.debug("Filtering status")
        query = query.filter(Task.status == "valid")
        return query

    def filter_paid_status(self, query, appstruct):
        status = appstruct["paid_status"]
        if status == "paid":
            query = self._filter_paid(query)
        elif status == "notpaid":
            query = self._filter_not_paid(query)
        return query

    def _filter_paid(self, query):
        return query.filter(Invoice.paid_status == "resulted")

    def _filter_not_paid(self, query):
        return query.filter(Invoice.paid_status.in_(("waiting", "paid")))

    def filter_doctype(self, query, appstruct):
        """
        Filter invocies by type (invoice/cancelinvoice)
        """
        type_ = appstruct.get("doctype")
        if type_ in (
            "invoice",
            "cancelinvoice",
            "internalinvoice",
            "internalcancelinvoice",
        ):
            query = query.filter(Task.type_ == type_)
        elif type_ == "internal":
            query = query.filter(
                Task.type_.in_(("internalinvoice", "internalcancelinvoice"))
            )
        elif type_ == "external":
            query = query.filter(Task.type_.in_(("invoice", "cancelinvoice")))
        else:
            query = query.filter(Task.type_.in_(Task.invoice_types))
        return query

    def filter_payment_mode(self, query, appstruct):
        """
        Filter invoices by payment mode (invoice/cancelinvoice)
        """
        mode = appstruct.get("payment_mode")
        if mode not in ("all", None):
            subquery = (
                DBSESSION()
                .query(Payment)
                .filter(Payment.mode == mode, Payment.task_id == Task.id)
            )
            query = query.filter(subquery.exists())
        return query

    def filter_auto_validated(self, query, appstruct):
        """
        Filter the estimations by doc types
        """
        auto_validated = appstruct.get("auto_validated")
        if auto_validated:
            query = query.filter(Task.auto_validated == 1)
        return query

    def filter_business_type_id(self, query, appstruct):
        business_type_id = appstruct.get("business_type_id")
        if business_type_id not in ("all", None):
            query = query.filter(Invoice.business_type_id == business_type_id)
        return query


class GlobalInvoicesListView(InvoiceListTools, BaseListView):
    """
    Used as base for company invoices listing
    """

    add_template_vars = (
        "title",
        "stream_main_actions",
        "stream_more_actions",
        "is_admin",
    )
    is_admin = True

    def filter_validator_id(self, query, appstruct):
        validator_id = appstruct.get("validator_id")
        if validator_id:
            query = Task.query_by_validator_id(validator_id, query)
        return query

    def stream_main_actions(self):
        if self.request.has_permission(PERMISSIONS["global.manage_accounting"]):
            yield Link(
                "/invoices/export/pdf",
                label="Export<span class='no_mobile'>&nbsp;massif</span>",
                icon="file-export",
                css="btn icon",
                title="Aller vers la page d'export des factures au format PDF",
            )

    def get_export_path(self, extension, details=False):
        return self.request.route_path(
            "invoices{}_export".format("_details" if details else ""),
            extension=extension,
            _query=self.request.GET,
        )

    def stream_more_actions(self):
        yield Link(
            self.get_export_path(extension="xls"),
            icon="file-excel",
            label="Liste des factures (Excel)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export excel des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods"),
            icon="file-spreadsheet",
            label="Liste des factures (ODS)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="csv"),
            icon="file-csv",
            label="Liste des factures (CSV)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="xls", details=True),
            icon="file-excel",
            label="Détail des factures (Excel)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export excel du détail des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods", details=True),
            icon="file-spreadsheet",
            label="Détail des factures (ODS)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS du détail des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="csv", details=True),
            icon="file-csv",
            label="Détail des factures (CSV)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV du détail des factures de la liste",
        )


class CompanyInvoicesListView(GlobalInvoicesListView):
    """
    Invoice list for one given company
    """

    is_admin = False

    @property
    def with_draft(self):
        return True

    def _get_company_id(self, appstruct=None):
        return self.request.context.id

    @property
    def title(self):
        return "Factures de l'enseigne {0}".format(self.request.context.name)

    filter_status = filter_all_status

    def get_export_path(self, extension, details=False):
        return self.request.route_path(
            "company_invoices{}_export".format("_details" if details else ""),
            id=self._get_company_id(),
            extension=extension,
            _query=self.request.GET,
        )

    def stream_main_actions(self):
        if self.request.has_permission(PERMISSIONS["context.add_invoice"]):
            yield Link(
                self.request.route_path(
                    COMPANY_INVOICE_ADD_ROUTE,
                    id=self._get_company_id(),
                ),
                label="Ajouter<span class='no_mobile'>&nbsp;une facture</span>",
                icon="plus",
                css="btn btn-primary",
                title="Ajouter une nouvelle facture",
            )


class GlobalInvoicesCsvView(
    AsyncJobMixin,
    InvoiceListTools,
    BaseListView,
):
    model = Invoice
    file_format = "csv"
    filename = "factures_"

    def query(self):
        payment_subquery = aliased(
            BaseTaskPayment,
            DBSESSION.query(
                BaseTaskPayment,
                func.Max(BaseTaskPayment.date).label("latest_payment_date"),
            )
            .group_by(BaseTaskPayment.task_id)
            .subquery(),
        )
        query = self.request.dbsession.query(Task)
        query = query.with_polymorphic([Invoice, CancelInvoice])
        query = query.outerjoin(Invoice.payments)
        query = query.outerjoin(Task.customer)
        query = query.outerjoin(Task.company)
        query = query.outerjoin(payment_subquery)
        query = query.options(load_only(Task.id))
        return query

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the streamed file object
        """
        all_ids = [elem.id for elem in query]
        logger.debug("    + All_ids where collected : {0}".format(all_ids))
        if not all_ids:
            return self.show_error("Aucune facture ne correspond à cette requête")

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp
        else:
            logger.debug("    + In the GlobalInvoicesCsvView._build_return_value")
            job_result = self.initialize_job_result(FileGenerationJob)

            logger.debug("    + Delaying the export_to_file task")
            celery_job = export_to_file.delay(
                job_result.id, "invoices", all_ids, self.filename, self.file_format
            )
            return self.redirect_to_job_watch(celery_job, job_result)


class GlobalInvoicesXlsView(GlobalInvoicesCsvView):
    file_format = "xls"


class GlobalInvoicesOdsView(GlobalInvoicesCsvView):
    file_format = "ods"


class CompanyInvoicesCsvView(GlobalInvoicesCsvView):
    is_admin = False

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class CompanyInvoicesXlsView(GlobalInvoicesXlsView):
    is_admin = False

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class CompanyInvoicesOdsView(GlobalInvoicesOdsView):
    is_admin = False

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class GlobalInvoicesDetailsCsvView(
    AsyncJobMixin,
    InvoiceListTools,
    BaseListView,
):
    file_format = "csv"

    def query(self):
        query = self.request.dbsession.query(Task)
        query = query.with_polymorphic([Invoice, CancelInvoice])
        query = query.outerjoin(Task.customer)
        query = query.outerjoin(Task.company)
        query = query.options(load_only(Task.id))
        return query

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the streamed file object
        """
        task_ids = [elem.id for elem in query]
        logger.debug("    + Invoices ids where collected : {0}".format(task_ids))
        if not task_ids:
            return self.show_error("Aucune facture ne correspond à cette requête")

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp
        else:
            logger.debug(
                "    + In the GlobalInvoicesDetailsCsvView._build_return_value"
            )
            job_result = self.initialize_job_result(FileGenerationJob)

            logger.debug("    + Delaying the export_invoices_details_to_file task")
            celery_job = export_invoices_details_to_file.delay(
                job_result.id,
                task_ids,
                self.file_format,
            )
            return self.redirect_to_job_watch(celery_job, job_result)


class GlobalInvoicesDetailsXlsView(GlobalInvoicesDetailsCsvView):
    file_format = "xls"


class GlobalInvoicesDetailsOdsView(GlobalInvoicesDetailsCsvView):
    file_format = "ods"


class CompanyInvoicesDetailsCsvView(GlobalInvoicesDetailsCsvView):
    is_admin = False

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class CompanyInvoicesDetailsXlsView(GlobalInvoicesDetailsXlsView):
    is_admin = False

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class CompanyInvoicesDetailsOdsView(GlobalInvoicesDetailsOdsView):
    is_admin = False

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class InvoicePdfView(InvoiceListTools, BaseListView):
    sort_columns = dict(official_number=Task.status_date)
    default_direction = "asc"
    title = "Export massif de factures au format PDF"

    def get_schema(self):
        return get_pdf_export_schema(self.request)

    def _get_submitted(self):
        return self.request.POST

    def query(self):
        query = Task.get_valid_invoices()
        query = query.outerjoin(Task.customer)
        query = query.outerjoin(Task.company)
        return query

    def filter_official_number(self, query, appstruct):
        logger.debug(" + Filtering official number")
        number_range = appstruct.get("official_number", {})
        if number_range.get("start") not in (None, colander.null):
            start = number_range.get("start")
            start_status_date = find_task_status_date(start)
            query = query.filter(Task.status_date >= start_status_date)

            end = number_range.get("end")
            if end not in (None, colander.null):
                end_status_date = find_task_status_date(end)
                query = query.filter(Task.status_date <= end_status_date)
            else:
                end_status_date = "Aujourd'hui"

            logger.debug("    Between %s and %s" % (start_status_date, end_status_date))
        return query

    def _get_filename(self, appstruct):
        return "factures_ventes.pdf"

    def _get_form(self, schema: "colander.Schema", appstruct: dict) -> Form:
        """
        Build the form object
        """
        query_form = Form(
            schema,
            buttons=(submit_btn,),
            with_loader=False,
        )
        query_form.set_appstruct(appstruct)
        return query_form

    def _build_return_value(self, schema, appstruct, query):
        logger.debug(appstruct)
        if self.error:
            return dict(title=self.title, form=self.error.render())
        if "submit" in self.request.POST:
            logger.debug("Rendering bulk PDFs")
            # We've got some documents to export
            if DBSESSION.query(query.exists()).scalar():
                logger.debug(" + Rendering {} documents".format(query.count()))
                # Getting the html output
                pdf_buffer = task_bulk_pdf(query.all(), self.request)
                filename = self._get_filename(appstruct)

                try:
                    # Placing the pdf datas in the request
                    write_file_to_request(self.request, filename, pdf_buffer)
                    return self.request.response
                except BaseException:
                    logger.exception("Erreur à la génération massives des PDFs")
                    self.request.session.flash(
                        "Erreur à l’export des factures, \
    essayez de limiter le nombre de factures à exporter. Prévenez \
    votre administrateur si le problème persiste.",
                        queue="error",
                    )
            else:
                # There were no documents to export, we send a message to the
                # end user
                self.request.session.flash(
                    "Aucune facture à exporter n’a été trouvée", queue="error"
                )
        gotolist_btn = ViewLink(
            "Liste des factures", "global.list_invoices", path=INVOICE_COLLECTION_ROUTE
        )
        self.request.actionmenu.add(gotolist_btn)
        query_form = self._get_form(schema, appstruct)

        return dict(
            title=self.title,
            form=query_form.render(),
        )


def add_routes(config):
    """
    Add module's related route
    """
    # invoice export routes
    config.add_route("invoices_export", "/invoices.{extension}")
    config.add_route("invoices_details_export", "/invoices_details.{extension}")
    config.add_route(
        "company_invoices_export",
        r"/company/{id:\d+}/invoices.{extension}",
        traverse="/companies/{id}",
    )
    config.add_route(
        "company_invoices_details_export",
        r"/company/{id:\d+}/invoices_details.{extension}",
        traverse="/companies/{id}",
    )
    config.add_route("/invoices/export/pdf", "/invoices/export/pdf")


def includeme(config):
    add_routes(config)
    # Vues globales
    config.add_view(
        GlobalInvoicesListView,
        route_name=INVOICE_COLLECTION_ROUTE,
        renderer="invoices.mako",
        permission=PERMISSIONS["global.list_invoices"],
    )
    config.add_view(
        GlobalInvoicesCsvView,
        route_name="invoices_export",
        match_param="extension=csv",
        permission=PERMISSIONS["global.list_invoices"],
    )
    config.add_view(
        GlobalInvoicesOdsView,
        route_name="invoices_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.list_invoices"],
    )
    config.add_view(
        GlobalInvoicesXlsView,
        route_name="invoices_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.list_invoices"],
    )
    config.add_view(
        GlobalInvoicesDetailsCsvView,
        route_name="invoices_details_export",
        match_param="extension=csv",
        permission=PERMISSIONS["global.list_invoices"],
    )
    config.add_view(
        GlobalInvoicesDetailsOdsView,
        route_name="invoices_details_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.list_invoices"],
    )

    config.add_view(
        GlobalInvoicesDetailsXlsView,
        route_name="invoices_details_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.list_invoices"],
    )

    config.add_view(
        InvoicePdfView,
        route_name="/invoices/export/pdf",
        renderer="/base/formpage.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    # Vue Enseignes
    config.add_view(
        CompanyInvoicesListView,
        route_name=COMPANY_INVOICES_ROUTE,
        renderer="invoices.mako",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyInvoicesCsvView,
        route_name="company_invoices_export",
        match_param="extension=csv",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyInvoicesOdsView,
        route_name="company_invoices_export",
        match_param="extension=ods",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyInvoicesXlsView,
        route_name="company_invoices_export",
        match_param="extension=xls",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )

    config.add_view(
        CompanyInvoicesDetailsCsvView,
        route_name="company_invoices_details_export",
        match_param="extension=csv",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )

    config.add_view(
        CompanyInvoicesDetailsOdsView,
        route_name="company_invoices_details_export",
        match_param="extension=ods",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyInvoicesDetailsXlsView,
        route_name="company_invoices_details_export",
        match_param="extension=xls",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )

    config.add_admin_menu(
        parent="sale",
        order=1,
        label="Factures",
        href=INVOICE_COLLECTION_ROUTE,
        permission=PERMISSIONS["global.list_invoices"],
    )
    config.add_company_menu(
        parent="sale",
        order=2,
        label="Factures",
        route_name=COMPANY_INVOICES_ROUTE,
        route_id_key="company_id",
    )
