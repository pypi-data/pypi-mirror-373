import logging
from typing import Dict

import colander
import deform_extensions
from caerp_base.models.base import DBSESSION
from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import export_to_file
from deform import Form
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import asc, desc, extract
from sqlalchemy.orm import contains_eager, load_only

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.supplier_invoice.payment import (
    create_sepa_waiting_payment_for_supplier,
    create_sepa_waiting_payment_for_user,
)
from caerp.export.utils import write_file_to_request
from caerp.forms.company import get_default_employee_from_request
from caerp.forms.supply.supplier_invoice import (
    SetTypesSchema,
    SupplierInvoiceDispatchSchema,
    get_files_export_schema,
    get_sepa_waiting_schema,
    get_supplier_invoice_add_by_supplier_schema,
    get_supplier_invoice_list_schema,
)
from caerp.models.company import Company
from caerp.models.supply import SupplierInvoice, SupplierInvoiceLine
from caerp.models.third_party.supplier import Supplier
from caerp.models.user.user import User
from caerp.resources import dispatch_supplier_invoice_js, supplier_invoice_resources
from caerp.services.sepa import is_valid_bic, is_valid_iban
from caerp.utils import strings
from caerp.utils.widgets import Link, POSTButton, ViewLink
from caerp.utils.zip import mk_receipt_files_zip
from caerp.views import (
    AsyncJobMixin,
    BaseAddView,
    BaseFormView,
    BaseListView,
    BaseView,
    DeleteView,
    DuplicateView,
    JsAppViewMixin,
    TreeMixin,
    submit_btn,
)
from caerp.views.files.controller import FileController
from caerp.views.files.views import FileUploadView
from caerp.views.supply.base_views import SupplierDocListTools
from caerp.views.supply.utils import get_supplier_doc_url
from caerp.views.task.utils import get_task_url
from caerp.views.user.routes import USER_ACCOUNTING_URL

from .routes import (
    ADD_TO_SEPA_URL,
    COLLECTION_EXPORT_ROUTE,
    COLLECTION_ROUTE,
    COMPANY_COLLECTION_EXPORT_ROUTE,
    COMPANY_COLLECTION_ROUTE,
    DISPATCH_ROUTE,
    FILE_EXPORT_ROUTE,
    ITEM_ROUTE,
)

logger = logging.getLogger(__name__)


def populate_actionmenu(request):
    return request.actionmenu.add(
        ViewLink(
            "Revenir à la liste des factures fournisseur",
            path=COMPANY_COLLECTION_ROUTE,
            id=request.context.get_company_id(),
        )
    )


class BaseSupplierInvoiceAddMixin(BaseFormView):
    add_template_vars = ("title",)
    title = "Saisir une facture fournisseur"

    buttons = (submit_btn,)


class SupplierInvoiceAddView(BaseSupplierInvoiceAddMixin, BaseAddView):
    """
    Optional view ; with supplier selector

    Displayed only when no supplier order has been selected at previous step.
    """

    msg = "La facture fournisseur a été créée"

    schema = get_supplier_invoice_add_by_supplier_schema()

    def create_instance(self):
        return SupplierInvoice(
            company_id=self.context.id,
            payer=get_default_employee_from_request(self.request),
        )

    def redirect(self, appstruct, obj):
        url = get_supplier_doc_url(
            self.request,
            doc=obj,
        )
        return HTTPFound(url)


class SupplierInvoiceEditView(BaseView, JsAppViewMixin, TreeMixin):
    """
    Can act as edit view or readonly view (eg: waiting for validation).
    """

    def context_url(self, _query: Dict[str, str] = {}):
        return get_supplier_doc_url(self.request, api=True, _query=_query)

    @property
    def title(self):
        current_inv = self.current()
        label = current_inv.remote_invoice_number
        if current_inv.internal:
            label += " (Facture interne)"
        if not label:
            label = "Facture fournisseur"
        return label

    @property
    def tree_url(self):
        current_inv = self.current()
        return get_supplier_doc_url(self.request, doc=current_inv)

    def current(self):
        """
        Return the supplier invoice to use in the breadcrumb
        (TreeMixin) implementations
        """
        if isinstance(self.context, SupplierInvoice):
            result = self.context
        elif hasattr(self.context, "parent"):
            result = self.context.parent
        else:
            raise Exception(f"Can't find current supplier invoice in {self.context}")
        return result

    def more_js_app_options(self):
        return dict(
            edit=bool(
                self.request.has_permission(
                    PERMISSIONS["context.edit_supplier_invoice"]
                )
            ),
        )

    def internal_source_document_link(self):
        if self.context.internal:
            source_doc = self.context.source
            if self.request.has_permission(PERMISSIONS["company.view"], source_doc):
                url = get_task_url(self.request, source_doc, suffix="/general")

                return Link(
                    url=url,
                    label=f"Facture associée {source_doc.official_number}",
                    title="Voir la facture associée",
                    icon=None,
                )
        else:
            return None

    def __call__(self):
        populate_actionmenu(self.request)
        supplier_invoice_resources.need()
        return dict(
            title=self.title,
            context=self.context,
            js_app_options=self.get_js_app_options(),
            internal_source_document_link=self.internal_source_document_link(),
        )


class SupplierInvoiceDuplicateView(DuplicateView):
    route_name = "/supplier_invoices/{id}"
    message = "vous avez été redirigé vers la nouvelle facture fournisseur"


class SupplierInvoiceListTools(SupplierDocListTools):
    model_class = SupplierInvoice
    model_class_date_field = "date"
    line_model_class = SupplierInvoiceLine
    line_model_parent_field = "supplier_invoice_id"

    sort_columns = {
        "official_number": "official_number",
        "remote_invoice_number": "remote_invoice_number",
        "total_ht": "total_ht",
        "total_tva": "total_tva",
        "total": "total",
    }
    sort_columns.update(SupplierDocListTools.sort_columns)

    # sort by invoice date rather than creation date
    default_sort = "date"
    default_direction = "desc"

    def sort_by_total_tva(self, query, appstruct):
        sort_direction = self._get_sort_direction(appstruct)
        self.logger.debug("  + Direction : %s" % sort_direction)
        query = query.outerjoin(SupplierInvoice.lines).options(
            contains_eager(SupplierInvoice.lines).load_only(
                SupplierInvoiceLine.tva,
            )
        )

        if sort_direction == "asc":
            func = asc
        else:
            func = desc

        query = query.order_by(func(SupplierInvoiceLine.tva))
        return query

    def sort_by_total_ht(self, query, appstruct):
        sort_direction = self._get_sort_direction(appstruct)
        self.logger.debug("  + Direction : %s" % sort_direction)
        query = query.outerjoin(SupplierInvoice.lines).options(
            contains_eager(SupplierInvoice.lines).load_only(
                SupplierInvoiceLine.ht,
            )
        )

        if sort_direction == "asc":
            func = asc
        else:
            func = desc

        query = query.order_by(func(SupplierInvoiceLine.ht))
        return query

    def sort_by_total(self, query, appstruct):
        sort_direction = self._get_sort_direction(appstruct)
        self.logger.debug("  + Direction : %s" % sort_direction)
        query = query.outerjoin(SupplierInvoice.lines).options(
            contains_eager(SupplierInvoice.lines).load_only(
                SupplierInvoiceLine.ht, SupplierInvoiceLine.tva
            )
        )

        if sort_direction == "asc":
            func = asc
        else:
            func = desc

        query = query.order_by(func(SupplierInvoiceLine.ht + SupplierInvoiceLine.tva))
        return query

    def filter_official_number(self, query, appstruct):
        official_number = appstruct.get("official_number")
        if official_number:
            query = query.filter(SupplierInvoice.official_number == official_number)
        return query

    def filter_remote_invoice_number(self, query, appstruct):
        remote_invoice_number = appstruct.get("remote_invoice_number")
        if remote_invoice_number:
            query = query.filter(
                SupplierInvoice.remote_invoice_number.like(f"%{remote_invoice_number}%")
            )
        return query

    def filter_combined_paid_status(self, query, appstruct):
        status = appstruct.get("combined_paid_status")
        if status == "paid":
            query = query.filter(SupplierInvoice.paid_status == "resulted")
        elif status == "supplier_topay":
            query = query.filter(
                SupplierInvoice.supplier_paid_status != "resulted",
                SupplierInvoice.cae_percentage > 0,
            )
        elif status == "worker_topay":
            query = query.filter(
                SupplierInvoice.worker_paid_status != "resulted",
                SupplierInvoice.cae_percentage < 100,
            )
        return query


def stream_supplier_invoice_actions(request, supplier_invoice):
    yield Link(
        get_supplier_doc_url(request, doc=supplier_invoice),
        "Voir ou modifier",
        icon="arrow-right",
    )
    delete_allowed = request.has_permission(
        PERMISSIONS["context.delete_supplier_invoice"],
        supplier_invoice,
    )
    if delete_allowed:
        yield POSTButton(
            get_supplier_doc_url(
                request, doc=supplier_invoice, _query={"action": "delete"}
            ),
            "Supprimer",
            title="Supprimer définitivement cette facture ?",
            icon="trash-alt",
            css="negative",
            confirm="Êtes-vous sûr de vouloir supprimer cette facture ?",
        )


class BaseSupplierInvoiceListView(
    SupplierInvoiceListTools,
    BaseListView,
):
    title = "Liste des factures fournisseurs"
    add_template_vars = [
        "title",
        "stream_actions",
        "stream_main_actions",
        "stream_more_actions",
    ]
    is_admin_view = False

    def get_schema(self):
        return get_supplier_invoice_list_schema(
            self.request, is_global=self.is_admin_view
        )

    def stream_actions(self, supplier_invoice):
        return stream_supplier_invoice_actions(self.request, supplier_invoice)

    def get_export_path(self, extension):
        return self.request.route_path(
            COLLECTION_EXPORT_ROUTE,
            extension=extension,
            _query=self.request.GET,
        )

    def stream_main_actions(self):
        return []

    def stream_more_actions(self):
        yield Link(
            self.get_export_path(extension="csv"),
            icon="file-csv",
            label="Liste des factures fournisseurs (CSV)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="xlsx"),
            icon="file-excel",
            label="Liste des factures fournisseurs (Excel)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export Excel des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods"),
            icon="file-spreadsheet",
            label="Liste des factures fournisseurs (ODS)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS des factures de la liste",
        )


class AdminSupplierInvoiceListView(BaseSupplierInvoiceListView):
    """
    Global list of SupplierOrder from all companies
    """

    is_admin_view = True
    add_template_vars = BaseSupplierInvoiceListView.add_template_vars + [
        "is_admin_view",
    ]

    def query(self):
        return SupplierInvoice.query().join(SupplierInvoice.company)

    def stream_main_actions(self):
        yield Link(
            DISPATCH_ROUTE,
            icon="dispatch",
            label="Ventiler une facture fournisseur",
            css="btn btn-primary",
        )
        if self.request.has_permission(PERMISSIONS["global.list_supplier_invoices"]):
            yield Link(
                FILE_EXPORT_ROUTE,
                label="Export<span class='no_mobile'>&nbsp;massif&nbsp;</span>des factures d'achat",
                icon="file-export",
                css="btn icon",
                title="Export massif des factures d'achat",
            )


class CompanySupplierInvoiceListView(BaseSupplierInvoiceListView):
    """
    Company-scoped list of SupplierInvoice
    """

    is_admin_view = False

    def query(self):
        company = self.request.context
        query = SupplierInvoice.query()
        return query.filter(SupplierInvoice.company_id == company.id)

    def stream_main_actions(self):
        yield Link(
            self.request.route_path(
                COMPANY_COLLECTION_ROUTE,
                _query=dict(action="new"),
                id=self.request.context.id,
            ),
            icon="plus",
            label="Ajouter une facture fournisseur",
            css="btn btn-primary",
        )

    def get_export_path(self, extension):
        return self.request.route_path(
            COMPANY_COLLECTION_EXPORT_ROUTE,
            id=self.request.context.id,
            extension=extension,
            _query=self.request.GET,
        )


class GlobalSupplierInvoicesCsvView(
    AsyncJobMixin,
    SupplierInvoiceListTools,
    BaseListView,
):
    model = SupplierInvoice
    file_format = "csv"
    filename = "factures_frns_"
    is_admin_view = True

    def get_schema(self):
        return get_supplier_invoice_list_schema(
            self.request, is_global=self.is_admin_view
        )

    def query(self):
        query = self.request.dbsession.query(SupplierInvoice)
        query = query.options(load_only(SupplierInvoice.id))
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
                job_result.id,
                "supplier_invoices",
                all_ids,
                self.filename,
                self.file_format,
            )
            return self.redirect_to_job_watch(celery_job, job_result)


class GlobalSupplierInvoicesExcelView(GlobalSupplierInvoicesCsvView):
    file_format = "xlsx"


class GlobalSupplierInvoiceOdsView(GlobalSupplierInvoicesCsvView):
    file_format = "ods"


class CompanySupplierInvoiceCsvView(GlobalSupplierInvoicesCsvView):
    file_format = "csv"
    is_admin_view = False

    def query(self):
        company = self.request.context
        query = self.request.dbsession.query(SupplierInvoice).options(
            load_only(SupplierInvoice.id)
        )
        return query.filter(SupplierInvoice.company_id == company.id)


class CompanySupplierInvoiceExcelView(CompanySupplierInvoiceCsvView):
    file_format = "xlsx"


class CompanySupplierInvoiceOdsView(CompanySupplierInvoiceCsvView):
    file_format = "ods"


class SupplierInvoiceDeleteView(DeleteView):
    delete_msg = "La facture fournisseur a bien été supprimée"

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                COMPANY_COLLECTION_ROUTE, id=self.context.company.id
            )
        )


SUPPLIER_INVOICE_DISPATCH_GRID = (
    (
        ("date", 2),
        ("supplier_id", 10),
    ),
    (("remote_invoice_number", 6), ("invoice_file", 6)),
    (
        ("total_ht", 6),
        ("total_tva", 6),
    ),
    (("lines", 12),),
)


class SupplierInvoiceDispatchView(BaseFormView):
    """
    Used when an EA receives a global supplier invoice that needs to be split,
    enDi-wise, into several supplier invoices.
    """

    add_template_vars = ("title",)
    title = "Ventiler une facture fournisseur"
    schema = SupplierInvoiceDispatchSchema(
        widget=deform_extensions.GridFormWidget(
            named_grid=SUPPLIER_INVOICE_DISPATCH_GRID
        ),
        title="Réception d'une commande fournisseur",
    )

    def before(self, form):
        dispatch_supplier_invoice_js.need()

    @staticmethod
    def _group_lines_by_company(lines):
        ret = {}
        for line in lines:
            try:
                ret[line["company_id"]].append(line)
            except KeyError:
                ret[line["company_id"]] = [line]
        return ret

    def submit_success(self, appstruct):
        reference_supplier = Supplier.query().get(appstruct["supplier_id"])
        created_invoices = []

        indexed_lines = self._group_lines_by_company(appstruct["lines"])
        for company_id, lines in list(indexed_lines.items()):
            supplier = (
                Supplier.query()
                .filter(
                    Supplier.registration == reference_supplier.registration,
                    Supplier.company_id == company_id,
                )
                .first()
            )
            if supplier is None:
                # Copy minimal information to avoid data leak
                supplier = Supplier(
                    company_id=company_id,
                    company_name=reference_supplier.company_name,
                    registration=reference_supplier.registration,
                )
                self.dbsession.add(supplier)

            invoice = SupplierInvoice(
                date=appstruct["date"],
                company=Company.get(company_id),
                supplier=supplier,
                remote_invoice_number=appstruct.get("remote_invoice_number", ""),
            )
            controller = FileController(self.request)
            controller.save({"upload": appstruct["invoice_file"]}, parent=invoice)
            self.dbsession.add(invoice)

            for line in lines:
                SupplierInvoiceLine(
                    supplier_invoice=invoice,
                    description=line["description"],
                    ht=line["ht"],
                    tva=line["tva"],
                    type_id=line["type_id"],
                )
                # invoice.lines.append(new_line)
            created_invoices.append(invoice)

        invoices_descriptions = [
            f"{invoice.company.name}/{invoice.remote_invoice_number}"
            for invoice in created_invoices
        ]

        self.session.flash(
            "Les factures suivantes ont été créées : {}".format(
                " ".join(invoices_descriptions)
            )
        )
        return HTTPFound("/supplier_invoices")


class SupplierInvoiceSetTypesView(BaseFormView):
    """
    Base view for setting product codes (on supplier_invoices)

    context

        invoice or cancelinvoice
    """

    schema = SetTypesSchema

    @property
    def title(self):
        return (
            "Configuration des types de dépenses de la facture fournisseur "
            "{}".format(self.context.official_number)
        )

    def before(self, form):
        form.set_appstruct({"lines": [line.appstruct() for line in self.context.lines]})
        self.request.actionmenu.add(
            ViewLink(
                "Revenir au document",
                path="/supplier_invoices/{id}",
                id=self.context.id,
            )
        )

    def submit_success(self, appstruct):
        for line in appstruct["lines"]:
            line_id = line.get("id")
            type_id = line.get("type_id")
            if line_id is not None and type_id is not None:
                line = SupplierInvoiceLine.get(line_id)
                if line.supplier_invoice == self.context:
                    line.type_id = type_id
                    self.request.dbsession.merge(line)
                else:
                    logger.error(
                        "Possible break in attempt: trying to set product id "
                        "on the wrong supplier_invoice line (not belonging to "
                        "this supplier_invoice)"
                    )
        return HTTPFound(get_supplier_doc_url(self.request))


class SupplierInvoicesFilesExportView(SupplierInvoiceListTools, BaseListView):
    title = "Export massif des justificatifs d'achat"
    schema = get_files_export_schema()
    sort_columns = dict(official_number=SupplierInvoice.official_number)
    default_direction = "asc"

    def _is_filtered_by_company(self, appstruct):
        return "owner_id" in appstruct

    def _is_filtered_by_month(self, appstruct):
        return appstruct["month"] != -1

    def query(self):
        return SupplierInvoice.query().filter(SupplierInvoice.status == "valid")

    def filter_owner(self, query, appstruct):
        if self._is_filtered_by_company(appstruct):
            query = query.filter(SupplierInvoice.company_id == appstruct["owner_id"])
        return query

    def filter_month(self, query, appstruct):
        if self._is_filtered_by_month(appstruct):
            query = query.filter(
                extract("month", SupplierInvoice.date) == appstruct["month"]
            )
        return query

    def _get_form(self, schema: "colander.Schema", appstruct: dict) -> Form:
        query_form = Form(schema, buttons=(submit_btn,))
        query_form.set_appstruct(appstruct)
        return query_form

    def _get_submitted(self):
        return self.request.POST

    def _get_filename(self, appstruct):
        filename = f"justificatifs_achats_{appstruct['year']}"
        if self._is_filtered_by_month(appstruct):
            filename += f"_{appstruct['month']}"
        if self._is_filtered_by_company(appstruct):
            filename += f"_{Company.get(appstruct['owner_id']).name}"
        filename += ".zip"
        return filename

    def _collect_files(self, query):
        files = []
        for supplier_invoice in query.all():
            for file in supplier_invoice.files:
                files.append(file)
        logger.debug(
            "> Collecting {} files from {} supplier invoices".format(
                len(files), query.count()
            )
        )
        return files

    def _build_return_value(self, schema, appstruct, query):
        if self.error:
            return dict(title=self.title, form=self.error.render())
        if "submit" in self.request.POST:
            logger.debug(
                f"Exporting supplier invoices files to '{self._get_filename(appstruct)}'"
            )
            logger.debug(appstruct)
            if DBSESSION.query(query.exists()).scalar():
                files_to_export = self._collect_files(query)
                if len(files_to_export) > 0:
                    try:
                        zipcontent_buffer = mk_receipt_files_zip(
                            files_to_export,
                            with_month_folder=(
                                not self._is_filtered_by_month(appstruct)
                            ),
                            with_owner_folder=(
                                not self._is_filtered_by_company(appstruct)
                            ),
                        )
                        write_file_to_request(
                            self.request,
                            self._get_filename(appstruct),
                            zipcontent_buffer,
                            "application/zip",
                        )
                        return self.request.response
                    except BaseException as e:
                        self.request.session.flash(
                            f'Erreur lors de l’export des justificatifs : "{e}"',
                            queue="error",
                        )
                else:
                    self.request.session.flash(
                        "Aucune justificatif trouvé pour les factures fournisseur \
correspondant à ces critères",
                        queue="error",
                    )
            else:
                self.request.session.flash(
                    "Aucune facture fournisseur correspondant à ces critères",
                    queue="error",
                )

        gotolist_btn = ViewLink(
            "Liste des factures fournisseur",
            "global.list_supplier_invoices",
            path=COLLECTION_ROUTE,
        )
        self.request.actionmenu.add(gotolist_btn)
        query_form = self._get_form(schema, appstruct)

        return dict(
            title=self.title,
            form=query_form.render(),
        )


class SupplierInvoiceSepaWaitingView(BaseFormView):
    """
    Create a SupplierInvoiceSupplierSepaWaitingPayment
    """

    add_template_vars = ("help_message", "warn_message")

    def __init__(self, context, request=None):
        super().__init__(context, request)
        if self.request.matchdict["type"] == "user":
            self.type_ = "user"
        else:
            self.type_ = "cae"

    @property
    def title(self):
        return "Ajouter à la liste des paiements SEPA en attente"

    @property
    def title_detail(self):
        return (
            f"Ajouter la facture fournisseur {self.context.official_number} à la "
            "liste des paiements SEPA en attente"
        )

    @property
    def help_message(self):
        result = (
            "Indiquez ici le montant à mettre à payer.<br /> "
            "Ce montant pourra alors "
            "être inclu dans un ordre de virement à destination du fournisseur"
        )
        tresorerie = self.context.company.get_last_treasury_main_indicator()
        if tresorerie:
            value = strings.format_amount(tresorerie["value"])
            result += (
                "<ul>"
                f"<li>Enseigne : {self.context.company.name}</li>"
                f"<li>{tresorerie['label']} : {value}&nbsp;€</li>"
                "</ul>"
            )
        return result

    @property
    def warn_message(self):
        if self.type_ == "cae":
            supplier: Supplier = self.context.supplier
            if not is_valid_bic(supplier.bank_account_bic) or not is_valid_iban(
                supplier.bank_account_iban
            ):
                supplier_edit_url = self.request.route_path(
                    "supplier", id=supplier.id, _query={"action": "edit"}
                )
                return (
                    "Les informations bancaires du fournisseur ne sont pas "
                    "renseignées. Sans ces informations, il sera impossible d'intégrer "
                    "ce paiement dans un ordre de virement. <br />"
                    "<a href='javascript:void(0);' "
                    f"onclick='window.openPopup(\"{supplier_edit_url}\")' "
                    "title='Ouvrir le formulaire de modification des informations "
                    "bancaires "
                    "dans une nouvelle fenêtre' aria-label='Ouvrir le formulaire de "
                    "modification des informations bancaires dans une"
                    " nouvelle fenêtre'>Modifier les informations bancaires de "
                    f"{supplier.label}</a>"
                )
        else:
            user: User = self.context.payer
            if not is_valid_bic(user.bank_account_bic) or not is_valid_iban(
                user.bank_account_iban
            ):
                user_edit_url = self.request.route_path(USER_ACCOUNTING_URL, id=user.id)
                return (
                    "Les informations bancaires du compte de l'utilisateur ne sont pas "
                    "renseignées. Sans ces informations, il sera impossible d'intégrer "
                    "ce paiement dans un ordre de virement. <br />"
                    "<a href='javascript:void(0);' "
                    f"onclick='window.openPopup(\"{user_edit_url}\")' "
                    "title='Ouvrir le formulaire de modification des informations "
                    "bancaires "
                    "dans une nouvelle fenêtre' aria-label='Ouvrir le formulaire de "
                    "modification des informations bancaires dans une"
                    " nouvelle fenêtre'>Modifier les informations bancaires de "
                    f"{user.label}</a>"
                )

    def get_schema(self):
        return get_sepa_waiting_schema(self.context)

    def _get_amount_to_include(self, appstruct):
        full = appstruct.get("full", False)
        if full:
            if self.type_ == "cae":
                amount = self.context.cae_amount_waiting_for_payment()
            else:
                amount = self.context.worker_amount_waiting_for_payment()
        else:
            amount = appstruct.get("amount")
        return amount

    def submit_success(self, appstruct):
        amount = self._get_amount_to_include(appstruct)
        if self.type_ == "cae":
            create_sepa_waiting_payment_for_supplier(self.request, self.context, amount)
        else:
            create_sepa_waiting_payment_for_user(self.request, self.context, amount)
        url = self.request.route_path(ITEM_ROUTE, id=self.context.id)
        return HTTPFound(url)


def includeme(config):
    # Admin views
    config.add_view(
        AdminSupplierInvoiceListView,
        request_method="GET",
        route_name=COLLECTION_ROUTE,
        renderer="/supply/supplier_invoices.mako",
        permission=PERMISSIONS["global.list_supplier_invoices"],
    )
    config.add_view(
        GlobalSupplierInvoicesCsvView,
        route_name=COLLECTION_EXPORT_ROUTE,
        match_param="extension=csv",
        permission=PERMISSIONS["global.list_supplier_invoices"],
    )
    config.add_view(
        GlobalSupplierInvoicesExcelView,
        route_name=COLLECTION_EXPORT_ROUTE,
        match_param="extension=xlsx",
        permission=PERMISSIONS["global.list_supplier_invoices"],
    )
    config.add_view(
        GlobalSupplierInvoiceOdsView,
        route_name=COLLECTION_EXPORT_ROUTE,
        match_param="extension=ods",
        permission=PERMISSIONS["global.list_supplier_invoices"],
    )
    config.add_view(
        SupplierInvoicesFilesExportView,
        route_name=FILE_EXPORT_ROUTE,
        renderer="/base/formpage.mako",
        permission=PERMISSIONS["global.list_supplier_invoices"],
    )

    config.add_view(
        SupplierInvoiceAddView,
        route_name=COMPANY_COLLECTION_ROUTE,
        request_param="action=new",
        renderer="base/formpage.mako",
        context=Company,
        permission=PERMISSIONS["context.add_supplier_invoice"],
    )
    config.add_view(
        CompanySupplierInvoiceListView,
        route_name=COMPANY_COLLECTION_ROUTE,
        request_method="GET",
        renderer="/supply/supplier_invoices.mako",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        CompanySupplierInvoiceCsvView,
        route_name=COMPANY_COLLECTION_EXPORT_ROUTE,
        match_param="extension=csv",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        CompanySupplierInvoiceExcelView,
        route_name=COMPANY_COLLECTION_EXPORT_ROUTE,
        match_param="extension=xlsx",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        CompanySupplierInvoiceOdsView,
        route_name=COMPANY_COLLECTION_EXPORT_ROUTE,
        match_param="extension=ods",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )

    config.add_view(
        SupplierInvoiceEditView,
        route_name=ITEM_ROUTE,
        renderer="/supply/supplier_invoice.mako",
        layout="opa",
        context=SupplierInvoice,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        SupplierInvoiceSetTypesView,
        route_name=f"{ITEM_ROUTE}/set_types",
        renderer="base/formpage.mako",
        context=SupplierInvoice,
        permission=PERMISSIONS["context.set_treasury_supplier_invoice"],
    )

    config.add_view(
        SupplierInvoiceDeleteView,
        route_name=ITEM_ROUTE,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
        context=SupplierInvoice,
        permission=PERMISSIONS["context.delete_supplier_invoice"],
    )
    config.add_view(
        SupplierInvoiceDuplicateView,
        route_name=ITEM_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        require_csrf=True,
        context=SupplierInvoice,
        permission=PERMISSIONS["context.duplicate_supplier_invoice"],
    )
    config.add_view(
        SupplierInvoiceSepaWaitingView,
        route_name=ADD_TO_SEPA_URL,
        renderer="base/formpage.mako",
        context=SupplierInvoice,
        permission=PERMISSIONS["context.add_to_sepa_supplier_invoice"],
    )

    # File attachment
    config.add_view(
        FileUploadView,
        route_name=f"{ITEM_ROUTE}/addfile",
        renderer="base/formpage.mako",
        context=SupplierInvoice,
        permission=PERMISSIONS["context.add_file"],
    )

    config.add_view(
        SupplierInvoiceDispatchView,
        route_name=DISPATCH_ROUTE,
        renderer="supply/dispatch_supplier_invoice.mako",
        permission=PERMISSIONS["global.list_supplier_invoices"],
    )

    # Menus
    config.add_admin_menu(
        parent="sale",
        order=3,
        label="Factures fournisseurs",
        href=COLLECTION_ROUTE,
        routes_prefixes=[ITEM_ROUTE],
        permission=PERMISSIONS["global.list_supplier_invoices"],
    )
    config.add_company_menu(
        parent="supply",
        order=2,
        label="Factures fournisseurs",
        route_name=COMPANY_COLLECTION_ROUTE,
        route_id_key="company_id",
        routes_prefixes=[ITEM_ROUTE],
    )
