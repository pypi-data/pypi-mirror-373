"""
    Expense handling view
"""
import logging
from typing import Dict

from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from sqlalchemy import select

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.expense.payment import create_sepa_waiting_payment
from caerp.export.excel import make_excel_view
from caerp.export.expense_excel import XlsExpense
from caerp.forms.expense import get_add_edit_sheet_schema, get_sepa_waiting_schema
from caerp.forms.files import get_file_upload_schema
from caerp.models.company import Company
from caerp.models.expense.sheet import (
    ExpenseKmLine,
    ExpenseLine,
    ExpenseSheet,
    get_expense_sheet_name,
)
from caerp.models.expense.types import ExpenseTelType
from caerp.models.files import File
from caerp.models.user.user import User
from caerp.resources import expense_resources
from caerp.services.sepa import is_valid_bic, is_valid_iban
from caerp.utils import strings
from caerp.utils.image import get_pdf_image_resizer
from caerp.utils.widgets import ViewLink
from caerp.views import BaseFormView, BaseView, DeleteView, JsAppViewMixin, TreeMixin
from caerp.views.files.routes import NODE_FILE_API
from caerp.views.files.views import BaseZipFileView, FileUploadView
from caerp.views.render_api import format_account, month_name
from caerp.views.user.routes import USER_ACCOUNTING_URL

logger = logging.getLogger(__name__)


def get_expense_sheet(year, month, cid, uid):
    """
    Return the expense sheet for the given 4-uple
    """
    return (
        ExpenseSheet.query()
        .filter(ExpenseSheet.year == year)
        .filter(ExpenseSheet.month == month)
        .filter(ExpenseSheet.company_id == cid)
        .filter(ExpenseSheet.user_id == uid)
        .first()
    )


def get_new_expense_sheet(year, month, title, cid, uid):
    """
    Return a new expense sheet for the given 4-uple
    """
    expense = ExpenseSheet()
    expense.name = get_expense_sheet_name(month, year)
    expense.year = year
    expense.month = month
    expense.title = title
    expense.company_id = cid
    expense.user_id = uid
    query = ExpenseTelType.query()
    query = query.filter(ExpenseTelType.active == True)  # noqa
    teltypes = query.filter(ExpenseTelType.initialize == True)  # noqa
    for type_ in teltypes:
        line = ExpenseLine(type_id=type_.id, ht=0, tva=0, description=type_.label)
        expense.lines.append(line)
    return expense


def populate_actionmenu(request, tolist=False):
    """
    Add buttons in the request actionmenu attribute
    """
    link = None
    if not tolist and isinstance(request.context, ExpenseSheet):
        link = ViewLink(
            "Revenir à la note de dépenses",
            path="/expenses/{id}",
            id=request.context.id,
        )
    else:
        label = "Revenir à la liste des notes de dépenses"
        if request.has_permission("global.list_expenses"):
            link = ViewLink(label, path="expenses")
        else:
            if isinstance(request.context, Company):
                company_id = request.context.id
            else:
                company_id = request.context.company_id
            link = ViewLink(
                label,
                path="company_expenses",
                id=company_id,
            )
    if link is not None:
        request.actionmenu.add(link)


def get_formatted_user_vehicle_information_sentence(
    vehicle_fiscal_power, vehicle_registration
):
    """
    Return a formatted sentence with vehicle information
    :param vehicle_fiscal_power:
    :param vehicle_registration:
    :return: String
    """
    formatted_sentence = ""
    sentence = []
    if vehicle_fiscal_power:
        sentence.append("Puissance fiscale {}CV ".format(vehicle_fiscal_power))
    if vehicle_registration:
        sentence.append("Plaque {}".format(vehicle_registration))
    if len(sentence) > 0:
        formatted_sentence = "({})".format(";".join(sentence))
    return formatted_sentence


class ExpenseSheetAddView(BaseFormView):
    """
    A simple expense sheet add view
    """

    schema = get_add_edit_sheet_schema()

    @property
    def title(self):
        if isinstance(self.context, User):
            user = self.context
        else:
            user = User.get(self.request.matchdict["uid"])
        return "Ajouter une note de dépenses ({})".format(
            user.label,
        )

    def before(self, form):
        populate_actionmenu(self.request)

    def redirect(self, sheet):
        return HTTPFound(self.request.route_path("/expenses/{id}", id=sheet.id))

    def create_instance(self, appstruct):
        """
        Create a new expense sheet instance
        """
        year = appstruct["year"]
        month = appstruct["month"]
        title = None
        if "title" in appstruct:
            title = appstruct["title"]
        if isinstance(self.context, Company):
            company_id = self.context.id
            user_id = self.request.matchdict["uid"]
        elif isinstance(self.context, User):
            if len(self.context.companies) > 0:
                company_id = self.context.companies[0].id
                user_id = self.context.id
            else:
                raise HTTPForbidden()
        else:
            raise HTTPForbidden()
        result = get_new_expense_sheet(year, month, title, company_id, user_id)
        return result

    def submit_success(self, appstruct):
        sheet = self.create_instance(appstruct)
        self.dbsession.add(sheet)
        self.dbsession.flush()
        return self.redirect(sheet)

    def submit_failure(self, e):
        BaseFormView.submit_failure(self, e)


class ExpenseSheetEditInfosView(BaseFormView):
    """
    Expense sheet edit infos (year, month, title) view
    """

    schema = get_add_edit_sheet_schema()

    @property
    def title(self):
        return "Modification de la note de dépenses de {0} pour la période de {1} {2}".format(
            format_account(self.request.context.user),
            month_name(self.context.month),
            self.context.year,
        )

    def before(self, form):
        populate_actionmenu(self.request)
        form.set_appstruct(
            {
                "month": self.context.month,
                "year": self.context.year,
                "title": self.context.title if self.context.title else "",
            }
        )

    def redirect(self, sheet):
        return HTTPFound(self.request.route_path("/expenses/{id}", id=sheet.id))

    def submit_success(self, appstruct):
        sheet = self.context
        sheet.year = appstruct["year"]
        sheet.month = appstruct["month"]
        sheet.title = None
        if "title" in appstruct:
            sheet.title = appstruct["title"]
        self.dbsession.merge(sheet)
        self.dbsession.flush()
        return self.redirect(sheet)

    def submit_failure(self, e):
        BaseFormView.submit_failure(self, e)


class ExpenseSheetEditView(BaseView, JsAppViewMixin, TreeMixin):
    route_name = "/expenses/{id}"

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.current().id)

    @property
    def title(self):
        current = self.current()

        return "Note de dépenses de {0} pour la période de {1} {2}".format(
            format_account(current.user),
            month_name(current.month),
            current.year,
        )

    def current(self):
        """
        Renvoie le contexte pour la génération des informations de breadcrumb
        (title, tree_url)
        """
        if isinstance(self.context, ExpenseSheet):
            current = self.context
        elif hasattr(self.context, "parent"):
            current = self.context.parent
        else:
            raise Exception(
                f"No ExpenseSheet could be retrieved from context {self.context}"
            )
        return current

    def context_url(self, _query: Dict[str, str] = {}):
        return self.request.route_path(
            "/api/v1/expenses/{id}",
            id=self.request.context.id,
            _query=_query,
        )

    def more_js_app_options(self):
        logger.debug("more_js_app_options")

        result = super().more_js_app_options()
        result["file_upload_url"] = self.request.route_path(
            NODE_FILE_API, id=self.context.id
        )
        result["edit"] = False
        if self.request.has_permission(PERMISSIONS["context.edit_expensesheet"]):
            result["edit"] = True
        logger.debug(result)
        return result

    def __call__(self):
        populate_actionmenu(self.request, tolist=True)
        expense_resources.need()

        sheets = (
            ExpenseSheet.query()
            .filter(ExpenseSheet.year == self.context.year)
            .filter(ExpenseSheet.company_id == self.context.company_id)
            .filter(ExpenseSheet.user_id == self.context.user_id)
            .filter(ExpenseSheet.status == "valid")
            .filter(ExpenseSheet.kmlines.any())
        )
        sheets_id = [sheet.id for sheet in sheets.all()]
        kmlines = (
            ExpenseKmLine.query().filter(ExpenseKmLine.sheet_id.in_(sheets_id)).all()
        )
        kmlines_current_year = sum([line.km for line in kmlines])

        user_vehicle_information = get_formatted_user_vehicle_information_sentence(
            self.context.user.vehicle_fiscal_power,
            self.context.user.vehicle_registration,
        )
        ret = dict(
            kmlines_current_year=kmlines_current_year,
            context=self.context,
            title=self.title,
            status_history=self.context.statuses,
            user_vehicle_information=user_vehicle_information,
            treasury=self.context.company.get_last_treasury_main_indicator(),
        )
        ret["js_app_options"] = self.get_js_app_options()
        logger.debug(ret)
        return ret


class ExpenseSheetDeleteView(DeleteView):
    """
    Expense deletion view

    Current context is an expensesheet
    """

    delete_msg = "La note de dépenses a bien été supprimée"

    def redirect(self):
        url = self.request.route_path("company_expenses", id=self.context.company.id)
        return HTTPFound(url)


class ExpenseSheetDuplicateView(BaseFormView):
    form_options = (("formid", "duplicate_form"),)
    schema = get_add_edit_sheet_schema()

    @property
    def title(self):
        return "Dupliquer la note de dépenses de {0} {1}".format(
            strings.month_name(self.context.month),
            self.context.year,
        )

    def before(self, form):
        populate_actionmenu(self.request)
        if self.context.title:
            form.set_appstruct({"title": "Copie de {}".format(self.context.title)})

    def redirect(self, sheet):
        return HTTPFound(self.request.route_path("/expenses/{id}", id=sheet.id))

    def submit_success(self, appstruct):
        logger.debug("# Duplicating an expensesheet #")
        sheet = self.context.duplicate(appstruct["year"], appstruct["month"])
        sheet.title = None
        if "title" in appstruct:
            sheet.title = appstruct["title"]
        self.dbsession.add(sheet)
        self.dbsession.flush()
        logger.debug(
            "ExpenseSheet {0} was duplicated to {1}".format(self.context.id, sheet.id)
        )
        return self.redirect(sheet)

    def submit_failure(self, e):
        BaseFormView.submit_failure(self, e)


def excel_filename(request):
    """
    return an excel filename based on the request context
    """
    exp = request.context
    filename = "ndf_{0}_{1}_{2}_{3}".format(
        exp.year,
        exp.month,
        exp.user.lastname,
        exp.user.firstname,
    )
    if exp.title:
        filename += "_{}".format(exp.title[:50])
    filename += ".xlsx"
    return filename


class ExpenseFileUploadView(FileUploadView):
    def get_schema(self):
        resizer = get_pdf_image_resizer(self.request)
        return get_file_upload_schema([resizer])


class ExpenseSheetZipFileView(BaseZipFileView):
    """
    View to generate a zip file containing all files attached to a given expense sheet
    """

    def filename(self):
        return f"justificatifs_{self.context.official_number}.zip"

    def collect_files(self):
        return (
            self.dbsession.execute(
                select(File).filter(File.parent_id == self.context.id)
            )
            .scalars()
            .all()
        )


class ExpenseSheetSepaWaitingView(BaseFormView):
    """
    Form view used to add a ExpensePaymentSepaWaiting entry using a colander schema
    """

    add_template_vars = ("help_message", "warn_message")

    @property
    def title(self):
        return "Ajouter à la liste des paiement SEPA en attente"

    @property
    def title_detail(self):
        return (
            f"Ajouter la note de dépenses {self.context.official_number} à la "
            "liste des paiements SEPA en attente"
        )

    @property
    def help_message(self):
        result = (
            "Indiquez ici le montant à mettre à payer.<br /> "
            "Ce montant pourra alors "
            "être inclu dans un ordre de virement à destination de l'entrepreneur"
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
        user = self.context.user
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
            amount = self.context.amount_waiting_for_payment()
        else:
            amount = appstruct.get("amount")
        return amount

    def submit_success(self, appstruct):
        amount = self._get_amount_to_include(appstruct)
        create_sepa_waiting_payment(self.request, self.context, amount)
        url = self.request.route_path("/expenses/{id}", id=self.context.id)
        return HTTPFound(url)


def add_routes(config):
    """
    Add module's related routes
    """
    config.add_route("expenses", "/expenses")

    config.add_route(
        "user_expenses", "/company/{id}/{uid}/expenses", traverse="/companies/{id}"
    )
    config.add_route(
        "user_expenses_shortcut", "/user_expenses/{id}", traverse="/users/{id}"
    )

    config.add_route(
        "/expenses/{id}",
        r"/expenses/{id:\d+}",
        traverse="/expenses/{id}",
    )

    for extension in ("xlsx", "zip"):
        config.add_route(
            "/expenses/{id}.%s" % extension,
            r"/expenses/{id:\d+}.%s" % extension,
            traverse="/expenses/{id}",
        )

    for action in (
        "delete",
        "duplicate",
        "addfile",
        "edit",
        "add_to_sepa",
    ):
        config.add_route(
            "/expenses/{id}/%s" % action,
            r"/expenses/{id:\d+}/%s" % action,
            traverse="/expenses/{id}",
        )


def includeme(config):
    """
    Declare all the routes and views related to this module
    """
    add_routes(config)

    config.add_view(
        ExpenseSheetAddView,
        route_name="user_expenses",
        permission=PERMISSIONS["context.add_expensesheet"],
        renderer="base/formpage.mako",
        context=Company,
    )
    config.add_view(
        ExpenseSheetAddView,
        route_name="user_expenses_shortcut",
        permission=PERMISSIONS["global.access_ea"],
        renderer="base/formpage.mako",
        context=User,
    )

    config.add_tree_view(
        ExpenseSheetEditView,
        route_name="/expenses/{id}",
        renderer="expenses/expense.mako",
        permission=PERMISSIONS["company.view"],
        layout="opa",
        context=ExpenseSheet,
    )
    config.add_view(
        ExpenseSheetZipFileView,
        route_name="/expenses/{id}.zip",
        permission=PERMISSIONS["company.view"],
        context=ExpenseSheet,
    )

    config.add_view(
        ExpenseSheetDeleteView,
        route_name="/expenses/{id}/delete",
        permission=PERMISSIONS["context.delete_expensesheet"],
        request_method="POST",
        require_csrf=True,
        context=ExpenseSheet,
    )

    config.add_view(
        ExpenseSheetDuplicateView,
        route_name="/expenses/{id}/duplicate",
        renderer="base/formpage.mako",
        # Cette permission est checkée au niveau de la company parente
        permission=PERMISSIONS["context.add_expensesheet"],
        context=ExpenseSheet,
    )

    # Xls export
    config.add_view(
        make_excel_view(excel_filename, XlsExpense),
        route_name="/expenses/{id}.xlsx",
        permission=PERMISSIONS["company.view"],
        context=ExpenseSheet,
    )
    # File attachment
    config.add_view(
        ExpenseFileUploadView,
        route_name="/expenses/{id}/addfile",
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.add_file"],
        context=ExpenseSheet,
    )

    config.add_view(
        ExpenseSheetEditInfosView,
        route_name="/expenses/{id}/edit",
        permission=PERMISSIONS["context.edit_expensesheet"],
        renderer="base/formpage.mako",
        context=ExpenseSheet,
    )
    config.add_view(
        ExpenseSheetSepaWaitingView,
        route_name="/expenses/{id}/add_to_sepa",
        permission=PERMISSIONS["context.add_to_sepa_expensesheet"],
        context=ExpenseSheet,
        renderer="base/formpage.mako",
    )
