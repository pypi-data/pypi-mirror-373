import logging

from caerp.consts.permissions import PERMISSIONS
from collections import OrderedDict
from sqlalchemy import or_

from caerp.interfaces import (
    ITreasuryProducer,
    ITreasuryExpenseWriter,
)
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.expense.types import ExpenseType
from caerp.models.export.accounting_export_log import ExpenseAccountingExportLogEntry
from caerp.models.user.user import User
from caerp.models.user.userdatas import UserDatas
from caerp.utils import strings
from caerp.utils.accounting import (
    check_user_accounting_configuration,
    check_company_accounting_configuration,
)
from caerp.utils.files import get_timestamped_filename
from caerp.utils.widgets import ViewLink
from caerp.views.admin.expense.accounting import EXPENSE_ACCOUNTING_URL
from caerp.views.company.tools import get_company_url
from caerp.views.export import BaseExportView
from caerp.views.export.utils import (
    get_expense_all_form,
    get_expense_number_form,
    get_expense_form,
    ACCOUNTING_EXPORT_TYPE_EXPENSES,
)
from caerp.views.user.routes import USER_ACCOUNTING_URL


logger = logging.getLogger(__name__)


CONFIG_ERROR_MSG = """Veuillez vous assurer que tous les éléments de
configuration nécessaire à l'export des notes de dépenses ont
bien été fournis : 
<a onclick="window.openPopup('{0}');" href='#' title="La configuration des notes de dépenses s’ouvrira dans une nouvelle fenêtre" aria-label="La configuration des notes de dépenses s’ouvrira dans une nouvelle fenêtre">
    Configuration des notes de dépenses
</a>"""


COMPANY_ERROR_MSG = """Le code analytique de l'enseigne {0} n'a pas été
configuré : 
<a onclick="window.openPopup('{1}');" href='#' title="Voir l’enseigne dans une nouvelle fenêtre" aria-label="Voir l’enseigne dans une nouvelle fenêtre">
    Voir l’enseigne
</a>"""

ACCOUNT_ERROR_MSG = """Le compte tiers de l'employé {0} n'a pas été
configuré : 
<a onclick="window.openPopup('{1}');" href='#' title="Voir l’employé dans une nouvelle fenêtre" aria-label="Voir l’employé dans une nouvelle fenêtre">
    Voir les informations comptables de l’employé
</a>"""


class SageExpenseExportPage(BaseExportView):
    """
    Sage Expense export views
    """

    title = "Export des écritures des notes de dépenses"
    config_keys = (
        "compte_cg_ndf",
        "code_journal_ndf",
    )
    writer_interface = ITreasuryExpenseWriter

    def _populate_action_menu(self):
        self.request.actionmenu.add(
            ViewLink(
                label="Liste des notes de dépenses",
                path="expenses",
            )
        )

    def before(self):
        self._populate_action_menu()

    def _get_forms(self, prefix="0", label="dépenses", genre="e", counter=None):
        """
        Generate forms for the given parameters

        :param str prefix: The prefix to give to the form ids
        :param str label: The label of our expense type
        :param str genre: 'e' or ''
        :param obj counter: An iterable for form field numbering passed to all
        forms in the same page
        :returns: A dict with forms in it
            {formid: {'form': form, title:formtitle}}
        :rtype: OrderedDict
        """
        result = OrderedDict()

        main_form = get_expense_form(
            self.request,
            title="Exporter des %s" % label,
            prefix=prefix,
            counter=counter,
        )
        id_form = get_expense_number_form(
            self.request,
            main_form.counter,
            title="Exporter des %s depuis un n° de pièce" % label,
            prefix=prefix,
        )
        all_form = get_expense_all_form(
            self.request,
            main_form.counter,
            title="Exporter les %s non exporté%ss" % (label, genre),
            prefix=prefix,
        )

        for form in all_form, id_form, main_form:
            result[form.formid] = {"form": form, "title": form.schema.title}

        return result

    def get_forms(self):
        """
        Implement parent get_forms method
        """
        result = self._get_forms()
        counter = list(result.values())[0]["form"].counter
        result.update(
            self._get_forms(prefix="1", label="frais", genre="", counter=counter)
        )
        result.update(
            self._get_forms(prefix="2", label="achats", genre="", counter=counter)
        )
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
        # -2 means situation_antenne_id = NULL
        if antenne_id == -2:
            antenne_id = None

        query = query.outerjoin(User, ExpenseSheet.user)
        query = query.outerjoin(User.userdatas)
        query = query.filter(UserDatas.situation_antenne_id == antenne_id)

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
        # -2 means situation_follower_id = NULL
        if follower_id == -2:
            follower_id = None

        query = query.outerjoin(User, ExpenseSheet.user)
        query = query.outerjoin(User.userdatas)
        query = query.filter(UserDatas.situation_follower_id == follower_id)

        return query

    def _filter_by_number(self, query, appstruct):
        """
        Add an official_number filter on the query
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        official_number = appstruct["official_number"]
        return query.filter(ExpenseSheet.official_number == official_number)

    def _filter_by_period(self, query, appstruct):
        """
        Add a filter on month and year
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        year = appstruct["year"]
        query = query.filter(ExpenseSheet.year == year)
        month = appstruct["month"]
        query = query.filter(ExpenseSheet.month == month)
        return query

    def _filter_by_user(self, query, appstruct):
        """
        Add a filter on the user_id
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if appstruct.get("user_id", 0) != 0:
            user_id = appstruct["user_id"]
            query = query.filter(ExpenseSheet.user_id == user_id)
        return query

    def _filter_by_exported(self, query, appstruct):
        """
        Filter exported regarding the category of expense we want to export
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if not appstruct.get("exported"):
            export_category = appstruct["category"]
            if export_category == "0":
                query = query.filter(
                    or_(
                        ExpenseSheet.purchase_exported == False,  # noqa:E712
                        ExpenseSheet.expense_exported == False,  # noqa:E712
                    )
                )

            elif export_category == "1":
                query = query.filter_by(expense_exported=False)

            elif export_category == "2":
                query = query.filter_by(purchase_exported=False)
        return query

    def _filter_by_validator(self, query, appstruct):
        """
        Filter regarding who validated the expense sheet.
        Will only keep all expenses validated by the designated user.
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if "validator_id" in appstruct:
            query = query.filter(
                ExpenseSheet.status_user_id == appstruct["validator_id"]
            )
        return query

    def query(self, appstruct, form_name):
        """
        Base Query for expenses
        :param appstruct: params passed in the query for expense export
        :param str form_name: The submitted form's name
        """
        query = ExpenseSheet.query()
        query = query.filter(ExpenseSheet.status == "valid")

        if form_name.endswith("_number_form"):
            query = self._filter_by_number(query, appstruct)

        elif form_name.endswith("_main_form"):
            query = self._filter_by_period(query, appstruct)
            query = self._filter_by_user(query, appstruct)

        query = self._filter_by_exported(query, appstruct)
        query = self._filter_by_validator(query, appstruct)
        query = self._filter_by_antenne(query, appstruct)
        query = self._filter_by_follower(query, appstruct)

        return query

    def _check_expense_types(self):
        """
        Check expense types have all a code set
        """
        for type_ in (
            ExpenseType.query().filter_by(active=True).filter_by(internal=False)
        ):
            if not type_.code:
                return False
        return True

    def _check_config(self, config, expenses):
        """
        Check all configuration values are set for export

        :param config: The application configuration dict
        """
        for key in self.config_keys:
            if not config.get(key):
                return False

        return True

    def _check_company(self, company):
        if not check_company_accounting_configuration(company):
            company_url = get_company_url(self.request, company, action="edit")
            return COMPANY_ERROR_MSG.format(company.name, company_url)
        return None

    def _check_user(self, account):
        if not check_user_accounting_configuration(self.request, account):
            user_url = self.request.route_path(USER_ACCOUNTING_URL, id=account.id)
            return ACCOUNT_ERROR_MSG.format(account.label, user_url)
        return None

    def check(self, expenses):
        """
        Check if we can export the expenses

        :param expenses: the expenses to export
        :returns: a 2-uple (is_ok, messages)
        """
        count = expenses.count()
        if count == 0:
            logger.warning("Il n'y a aucune note de dépenses à exporter")
            title = "Il n'y a aucune note de dépenses à exporter"
            res = {"title": title, "errors": []}
            return False, res

        title = "Vous vous apprêtez à exporter {0} notes de dépenses".format(count)

        errors = []

        if not self._check_config(self.request.config, expenses):
            url1 = self.request.route_path(EXPENSE_ACCOUNTING_URL)
            errors.append(CONFIG_ERROR_MSG.format(url1))

        for expense in expenses:
            company = expense.company
            error = self._check_company(company)
            if error is not None:
                errors.append(
                    "La note de dépenses de {0} n'est pas exportable "
                    "<br />{1}".format(strings.format_account(expense.user), error)
                )
            error = self._check_user(expense.user)
            if error is not None:
                errors.append(
                    "La note de dépenses de {0} n'est pas exportable "
                    "<br />{1}".format(strings.format_account(expense.user), error)
                )

        res = {"title": title, "errors": errors}
        return len(errors) == 0, res

    def record_exported(self, expenses, form_name, appstruct):
        """
        Tag the exported expenses

        :param expenses: The expenses we are exporting
        """
        category = appstruct["category"]

        for expense in expenses:
            logger.info(
                f"The expense with id {expense.id} and official number "
                f"{expense.official_number} has been exported"
            )

            if category == "0":
                expense.expense_exported = True
                expense.purchase_exported = True
            elif category == "1":
                expense.expense_exported = True
            elif category == "2":
                expense.purchase_exported = True

            self.request.dbsession.merge(expense)

    def _collect_export_data(self, expenses, appstruct=None):
        """
        Collect the datas to export

        If we export all datas, ensure only the non-already exported datas are
        included

        :returns: A list of book entry lines in dict format
        :rtype: list
        """
        force = appstruct.get("exported", False)
        category = appstruct["category"]

        exporter_class = self.request.find_service_factory(
            ITreasuryProducer, context=ExpenseSheet
        )
        exporter = exporter_class(self.context, self.request)
        datas = []
        if category in ("1", "2") or force:
            datas = exporter.get_book_entries(expenses, category)
        else:
            # If we're not forcing and we export all, we filter regarding which
            # datas were already exported
            for expense in expenses:
                if not expense.expense_exported:
                    datas.extend(exporter.get_item_book_entries(expense, "1"))

                if not expense.purchase_exported:
                    datas.extend(exporter.get_item_book_entries(expense, "2"))
        return datas

    def record_export(self, expenses, form_name, appstruct, export_file):
        export = ExpenseAccountingExportLogEntry()
        export.user_id = self.request.identity.id
        export.export_file_id = export_file.id
        export.export_type = ACCOUNTING_EXPORT_TYPE_EXPENSES

        for expense in expenses:
            export.exported_expenses.append(expense)

        self.request.dbsession.add(export)
        self.request.dbsession.flush()

    def get_filename(self, writer):
        return get_timestamped_filename("export_ndf", writer.extension)


def add_routes(config):
    config.add_route("/export/treasury/expenses", "/export/treasury/expenses")
    config.add_route("/export/treasury/expenses/{id}", "/export/treasury/expenses/{id}")


def add_views(config):
    config.add_view(
        SageExpenseExportPage,
        route_name="/export/treasury/expenses",
        renderer="/export/main.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )


def includeme(config):
    add_routes(config)
    add_views(config)
    config.add_admin_menu(
        parent="accounting",
        order=2,
        label="Export des notes de dépenses",
        href="/export/treasury/expenses",
        permission=PERMISSIONS["global.manage_accounting"],
    )
