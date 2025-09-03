import datetime
import logging
from collections import OrderedDict

import colander
from caerp_base.models.base import DBSESSION
from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import export_expenses_to_file
from deform import Form
from sqlalchemy import desc, distinct, select

from caerp.consts.permissions import PERMISSIONS
from caerp.export.utils import write_file_to_request
from caerp.forms.expense import get_files_export_schema, get_list_schema
from caerp.models.company import Company
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.expense.types import ExpenseKmType, ExpenseTelType, ExpenseType
from caerp.models.user import User, UserDatas
from caerp.models.user.login import Login
from caerp.resources import admin_expense_js
from caerp.utils.widgets import Link, PopUp, ViewLink
from caerp.utils.zip import mk_receipt_files_zip
from caerp.views import AsyncJobMixin, BaseListView, submit_btn
from caerp.views.expenses.utils import get_payment_form

logger = logging.getLogger(__name__)


class ExpenseListTools:
    title = "Liste des notes de dépenses de la CAE"
    sort_columns = dict(
        official_number=ExpenseSheet.official_number,
        month=ExpenseSheet.month,
        name=User.lastname,
    )
    default_sort = "month"
    default_direction = "desc"

    def get_schema(self):
        return get_list_schema(self.request)

    def query(self):
        query = DBSESSION().query(distinct(ExpenseSheet.id), ExpenseSheet)
        query = query.outerjoin(ExpenseSheet.user)
        query = query.outerjoin(User.userdatas)
        query = query.order_by(ExpenseSheet.year.desc())
        return query

    def filter_search(self, query, appstruct):
        search = appstruct.get("search")
        if search and search != colander.null:
            query = query.filter(ExpenseSheet.official_number == search)
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year")
        if year and year not in (-1, colander.null):
            query = query.filter(ExpenseSheet.year == year)
        return query

    def filter_month(self, query, appstruct):
        month = appstruct.get("month")
        if month and month not in (-1, colander.null, "-1"):
            query = query.filter(ExpenseSheet.month == month)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            query = query.filter(UserDatas.situation_antenne_id == antenne_id)
        return query

    def filter_owner(self, query, appstruct):
        user_id = appstruct.get("owner_id", None)
        if user_id and user_id not in ("", -1, colander.null):
            query = query.filter(ExpenseSheet.user_id == user_id)
        return query

    def filter_status(self, query, appstruct):
        # Must add invalid and notpaid status
        status = appstruct.get("status")
        if status in ("wait", "valid", "invalid"):
            query = query.filter(ExpenseSheet.status == status)
        elif status in ("paid", "resulted"):
            query = query.filter(ExpenseSheet.status == "valid")
            query = query.filter(ExpenseSheet.paid_status == status)
        elif status == "notpaid":
            query = query.filter(ExpenseSheet.status == "valid")
            query = query.filter(ExpenseSheet.paid_status == "waiting")
        else:
            query = query.filter(ExpenseSheet.status.in_(("valid", "wait")))
        return query

    def filter_doc_status(self, query, appstruct):
        status = appstruct.get("justified_status")
        if status == "notjustified":
            query = query.filter(ExpenseSheet.justified == False)  # noqa
        elif status == "justified":
            query = query.filter(ExpenseSheet.justified == True)  # noqa
        return query


class ExpenseList(ExpenseListTools, BaseListView):
    """
    expenses list

        payment_form

            The payment form is added as a popup and handled through javascript
            to set the expense id
    """

    add_template_vars = (
        "title",
        "payment_formname",
        "stream_main_actions",
        "stream_more_actions",
    )

    @property
    def payment_formname(self):
        """
        Return a payment form name, add the form to the page popups as well
        """
        admin_expense_js.need()
        form_name = "payment_form"
        form = get_payment_form(self.request)
        form.set_appstruct({"come_from": self.request.current_route_path()})
        popup = PopUp(form_name, "Saisir un paiement", form.render())
        self.request.popups[popup.name] = popup
        return form_name

    def more_template_vars(self, response_dict):
        """
        Add template vars to the response dict

        :param obj result: A Sqla Query
        :returns: vars to pass to the template
        :rtype: dict
        """
        ret_dict = BaseListView.more_template_vars(self, response_dict)
        records = response_dict["records"]
        ret_dict["total_ht"] = sum(r[1].total_ht for r in records)
        ret_dict["total_tva"] = sum(r[1].total_tva for r in records)
        ret_dict["total_ttc"] = sum(r[1].total for r in records)
        ret_dict["total_km"] = sum(r[1].total_km for r in records)
        return ret_dict

    def stream_main_actions(self):
        if self.request.has_permission(PERMISSIONS["global.list_expenses"]):
            yield Link(
                "/expenses/export/files",
                label="Export<span class='no_mobile'>&nbsp;massif&nbsp;</span>des justificatifs",
                icon="file-export",
                css="btn icon",
                title="Export massif des justificatifs de dépense",
            )

    def get_export_path(self, extension, details=False):
        return self.request.route_path(
            "expenses{}_export".format("_details" if details else ""),
            extension=extension,
            _query=self.request.GET,
        )

    def stream_more_actions(self):
        yield Link(
            self.get_export_path(extension="xls"),
            icon="file-excel",
            label="Notes de dépenses (Excel)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export excel des notes de dépenses de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods"),
            icon="file-spreadsheet",
            label="Notes de dépenses (ODS)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS des notes de dépenses de la liste",
        )
        yield Link(
            self.get_export_path(extension="csv"),
            icon="file-csv",
            label="Notes de dépenses (CSV)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV des notes de dépenses de la liste",
        )


def create_global_expenses_export_view(extension):
    class GlobalExpensesView(
        AsyncJobMixin,
        ExpenseListTools,
        BaseListView,
    ):
        model = ExpenseSheet
        filename = "note_depense"

        def _build_return_value(self, schema, appstruct, query):
            """
            Return the streamed file object
            """
            all_ids = [elem[0] for elem in query]
            logger.debug("    + All_ids where collected : {0}".format(all_ids))
            if not all_ids:
                return self.show_error(
                    "Aucune note de dépense ne correspond à cette requête"
                )

            celery_error_resp = self.is_celery_alive()
            if celery_error_resp:
                return celery_error_resp
            else:
                logger.debug("    + In the GlobalExpenseCsvView._build_return_value")
                job_result = self.initialize_job_result(FileGenerationJob)

                logger.debug("    + Delaying the export_to_file task")
                celery_job = export_expenses_to_file.delay(
                    job_result.id, all_ids, self.filename, extension
                )
                return self.redirect_to_job_watch(celery_job, job_result)

    return GlobalExpensesView


def expense_configured():
    """
    Return True if the expenses were already configured
    """
    length = 0
    for factory in (ExpenseType, ExpenseKmType, ExpenseTelType):
        length += factory.query().count()
    return length > 0


def get_expensesheet_by_year(request, company: Company) -> OrderedDict:
    """
    Return expenses stored by year and users for display purpose
    """
    result = OrderedDict()

    today = datetime.date.today()
    year_dict = result.setdefault(today.year, OrderedDict())
    for user in request.dbsession.execute(
        select(User)
        .outerjoin(User.login)
        .where(User.companies.any(id=company.id))
        .order_by(desc(User.id == request.identity.id), Login.active, User.lastname)
    ).scalars():
        if user.login and user.login.active:
            year_dict[user] = []

    for expense_sheet in request.dbsession.execute(
        select(ExpenseSheet)
        .outerjoin(ExpenseSheet.user)
        .outerjoin(User.login)
        .where(ExpenseSheet.company_id == company.id)
        .order_by(
            ExpenseSheet.year.desc(),
            desc(User.id == request.identity.id),
            Login.active,
            User.lastname,
            ExpenseSheet.month.desc(),
        )
    ).scalars():
        year_dict = result.setdefault(expense_sheet.year, OrderedDict())
        year_dict.setdefault(expense_sheet.user, []).append(expense_sheet)

    today = datetime.date.today()
    year_dict = result.setdefault(today.year, {})
    for user in company.employees:
        if user.login and user.login.active:
            year_dict[user] = []
    return result


def company_expenses_view(request):
    """
    View that lists the expenseSheets related to the current company
    """
    title = "Notes de dépenses"
    if not expense_configured():
        return dict(
            title=title,
            conf_msg="La déclaration des notes de dépenses n'est pas encore \
accessible.",
        )

    expense_sheets = get_expensesheet_by_year(request, company=request.context)

    return dict(
        title=title,
        expense_sheets=expense_sheets,
        current_year=datetime.date.today().year,
        several_users=len(request.context.employees) > 1,
    )


class ExpensesFilesExportView(ExpenseListTools, BaseListView):
    title = "Export massif des justificatifs de dépense"
    default_sort = "official_number"
    default_direction = "asc"

    def get_schema(self):
        return get_files_export_schema()

    def filter_valid(self, query, appstruct):
        return query.filter(ExpenseSheet.status == "valid")

    def _is_filtered_by_user(self, appstruct):
        return "owner_id" in appstruct

    def _is_filtered_by_month(self, appstruct):
        return appstruct["month"] != -1

    def _get_form(self, schema: "colander.Schema", appstruct: dict) -> Form:
        query_form = Form(schema, buttons=(submit_btn,))
        query_form.set_appstruct(appstruct)
        return query_form

    def _get_submitted(self):
        return self.request.POST

    def _get_filename(self, appstruct):
        filename = f"justificatifs_depenses_{appstruct['year']}"
        if self._is_filtered_by_month(appstruct):
            filename += f"_{appstruct['month']}"
        if self._is_filtered_by_user(appstruct):
            filename += f"_{User.get(appstruct['owner_id']).label}"
        filename += ".zip"
        return filename

    def _collect_files(self, query):
        files = []
        for id, sheet in query.all():
            for file in sheet.files:
                files.append(file)
        logger.debug(
            "> Collecting {} files from {} expense sheets".format(
                len(files), query.count()
            )
        )
        return files

    def _build_return_value(self, schema, appstruct, query):
        if self.error:
            return dict(title=self.title, form=self.error.render())
        if "submit" in self.request.POST:
            logger.debug(
                f"Exporting expenses files to '{self._get_filename(appstruct)}'"
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
                                not self._is_filtered_by_user(appstruct)
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
                        "Aucune justificatif trouvé pour les notes de dépense \
correspondant à ces critères",
                        queue="error",
                    )
            else:
                self.request.session.flash(
                    "Aucune note de dépense correspondant à ces critères", queue="error"
                )

        gotolist_btn = ViewLink(
            "Liste des notes de dépense", "global.list_expenses", path="expenses"
        )
        self.request.actionmenu.add(gotolist_btn)
        query_form = self._get_form(schema, appstruct)

        return dict(
            title=self.title,
            form=query_form.render(),
        )


def add_routes(config):
    config.add_route(
        "company_expenses",
        "/company/{id}/expenses",
        traverse="/companies/{id}",
    )
    config.add_route("expenses_export", "/expenses.{extension}")
    config.add_route("/expenses/export/files", "/expenses/export/files")


def add_views(config):
    config.add_view(
        ExpenseList,
        route_name="expenses",
        permission=PERMISSIONS["global.list_expenses"],
        renderer="expenses/admin_expenses.mako",
    )

    config.add_view(
        company_expenses_view,
        route_name="company_expenses",
        renderer="expenses/expenses.mako",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )

    config.add_view(
        create_global_expenses_export_view("csv"),
        route_name="expenses_export",
        match_param="extension=csv",
        permission=PERMISSIONS["global.list_expenses"],
    )

    config.add_view(
        create_global_expenses_export_view("ods"),
        route_name="expenses_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.list_expenses"],
    )

    config.add_view(
        create_global_expenses_export_view("xls"),
        route_name="expenses_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.list_expenses"],
    )

    config.add_view(
        ExpensesFilesExportView,
        route_name="/expenses/export/files",
        renderer="/base/formpage.mako",
        permission=PERMISSIONS["global.list_expenses"],
    )


def includeme(config):
    add_routes(config)
    add_views(config)

    config.add_admin_menu(
        parent="sale",
        order=2,
        label="Notes de dépenses",
        href="/expenses",
        permission=PERMISSIONS["global.list_expenses"],
    )
    config.add_company_menu(
        parent="supply",
        order=1,
        label="Notes de dépenses",
        route_name="company_expenses",
        route_id_key="company_id",
        permission=PERMISSIONS["company.view"],
        routes_prefixes=["/expenses/{id}"],
    )
