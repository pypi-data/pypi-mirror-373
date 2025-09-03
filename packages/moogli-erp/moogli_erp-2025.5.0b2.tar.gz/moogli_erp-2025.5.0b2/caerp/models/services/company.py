"""
Company query service
"""
import datetime
from sqlalchemy import (
    func,
    desc,
    and_,
    select,
)
from sqlalchemy.orm import (
    load_only,
)

from caerp_base.models.base import DBSESSION
from caerp_base.models.utils import non_null_sum
from caerp.models.config import Config


class CompanyService:
    @classmethod
    def get_tasks(cls, instance, offset=None, limit=None):
        from caerp.models.task import Task

        query = DBSESSION().query(Task)
        query = query.filter(Task.company_id == instance.id)
        query = query.order_by(desc(Task.status_date))
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query

    @classmethod
    def get_estimations(cls, instance, valid=False):
        from caerp.models.task import Estimation

        query = DBSESSION().query(Estimation)
        query = query.filter(Estimation.company_id == instance.id)
        if valid:
            query = query.filter(Estimation.status == "valid")

        return query

    @classmethod
    def get_invoices(cls, instance, valid=False, not_paid=False):
        from caerp.models.task import Invoice

        query = DBSESSION().query(Invoice)
        query = query.filter(Invoice.company_id == instance.id)
        if valid:
            query = query.filter(Invoice.status == "valid")
        elif not_paid:
            query = query.filter(Invoice.status == "valid")
            query = query.filter(Invoice.paid_status.in_(("paid", "waiting")))
        return query

    @classmethod
    def get_cancelinvoices(cls, instance, valid=False):
        from caerp.models.task import CancelInvoice

        query = DBSESSION().query(CancelInvoice)
        query = query.filter(CancelInvoice.company_id == instance.id)
        if valid:
            query = query.filter(CancelInvoice.status == "valid")
        return query

    @classmethod
    def get_customers(cls, instance, year):
        from caerp.models.task import Invoice
        from caerp.models.third_party.customer import Customer

        query = DBSESSION().query(Customer)
        query = query.filter(Customer.company_id == instance.id)
        query = query.filter(
            Customer.invoices.any(
                and_(Invoice.status == "valid", Invoice.financial_year == year)
            )
        )
        return query

    @classmethod
    def get_late_invoices(cls, instance):
        from caerp.models.task import Invoice

        query = cls.get_invoices(instance, not_paid=True)
        key_day = datetime.date.today() - datetime.timedelta(days=45)
        query = query.filter(Invoice.date < key_day)
        query = query.order_by(desc(Invoice.date))
        return query

    @classmethod
    def get_customer_codes_and_names(cls, company):
        """
        Return a query for code and names of customers related to company
        :param company: the company we're working on
        :returns: an orm query loading Customer instances with only the columns
        we want
        :rtype: A Sqlalchemy query object
        """
        from caerp.models.third_party.customer import Customer

        query = DBSESSION().query(Customer)
        query = query.options(load_only("code", "label"))
        query = query.filter(Customer.code != None)  # noqa: E711
        query = query.filter(Customer.company_id == company.id)
        return query.order_by(Customer.code)

    @classmethod
    def get_supplier_codes_and_names(cls, company):
        """
        Return a query for code and names of suppliers related to company
        :param company: the company we're working on
        :returns: an orm query loading Supplier instances with only the columns
        we want
        :rtype: A Sqlalchemy query object
        """
        from caerp.models.third_party.supplier import Supplier

        query = DBSESSION().query(Supplier)
        query = query.options(load_only("code", "label"))
        query = query.filter(Supplier.code != None)  # noqa: E711
        query = query.filter(Supplier.company_id == company.id)
        return query.order_by(Supplier.code)

    @classmethod
    def get_project_codes_and_names(cls, company):
        """
        Return a query for code and names of projects related to company

        :param company: the company we're working on
        :returns: an orm query loading Project instances with only the columns
        we want
        :rtype: A Sqlalchemy query object
        """
        from caerp.models.project import Project

        query = DBSESSION().query(Project)
        query = query.options(load_only("code", "name"))
        query = query.filter(Project.code != None)  # noqa: E711
        query = query.filter(Project.company_id == company.id)
        return query.order_by(Project.code)

    @classmethod
    def get_next_index(cls, company, factory):
        query = DBSESSION.query(func.max(factory.company_index))
        query = query.filter(factory.company_id == company.id)
        max_num = query.first()[0]
        if max_num is None:
            max_num = 0

        return max_num + 1

    @classmethod
    def get_next_estimation_index(cls, company):
        """
        Return the next available sequence index in the given company
        """
        from caerp.models.task import Estimation

        return cls.get_next_index(company, Estimation)

    @classmethod
    def get_next_invoice_index(cls, company):
        """
        Return the next available sequence index in the given company
        """
        from caerp.models.task import Invoice

        return cls.get_next_index(company, Invoice)

    @classmethod
    def get_next_cancelinvoice_index(cls, company):
        """
        Return the next available sequence index in the given company
        """
        from caerp.models.task import CancelInvoice

        return cls.get_next_index(company, CancelInvoice)

    @classmethod
    def get_turnover(cls, company, start_date, end_date):
        """
        Compute the turnover for a given company on the given period
        """
        from caerp.models.task import Task

        query = DBSESSION.query(non_null_sum(Task.ht))
        query = query.filter(Task.type_.in_(Task.invoice_types))
        query = query.filter(Task.company_id == company.id)
        query = query.filter(Task.date.between(start_date, end_date))
        query = query.filter(Task.status == "valid")

        return query.scalar()

    @classmethod
    def get_total_expenses_on_period(cls, company, start_date, end_date):
        """
        Compute the expense total HT for a given company on the given period
        """
        from caerp.models.expense.sheet import ExpenseSheet

        query = DBSESSION.query(ExpenseSheet)
        query = query.filter(ExpenseSheet.company_id == company.id)
        query = query.filter(ExpenseSheet.date.between(start_date, end_date))
        query = query.filter(ExpenseSheet.status == "valid")
        query = query.all()

        return sum([expense_sheet.total_ht for expense_sheet in query])

    @classmethod
    def get_nb_km_on_period(cls, company, start_date, end_date):
        """
        Compute the kilometers declared for a given company on the given period
        """
        from caerp.models.expense.sheet import ExpenseSheet, ExpenseKmLine

        query = DBSESSION.query(ExpenseSheet)
        query = query.filter(ExpenseSheet.company_id == company.id)
        query = query.filter(ExpenseSheet.date.between(start_date, end_date))
        query = query.filter(ExpenseSheet.status == "valid")
        query = query.filter(ExpenseSheet.kmlines.any())
        query = query.all()

        sheets_id = [expense_sheet.id for expense_sheet in query]
        kmlines = (
            ExpenseKmLine.query().filter(ExpenseKmLine.sheet_id.in_(sheets_id)).all()
        )
        return sum([line.km for line in kmlines])

    @classmethod
    def get_total_expenses_and_km_on_period(cls, company, start_date, end_date):
        """
        Compute the expense total HT and the kilometers declared
        for a given company on the given period
        """
        from caerp.models.expense.sheet import ExpenseSheet, ExpenseKmLine

        query = DBSESSION.query(ExpenseSheet)
        query = query.filter(ExpenseSheet.company_id == company.id)
        query = query.filter(ExpenseSheet.date.between(start_date, end_date))
        query = query.filter(ExpenseSheet.status == "valid")
        query = query.all()

        total_ht = sum([expense_sheet.total_ht for expense_sheet in query])

        sheets_id = [expense_sheet.id for expense_sheet in query]
        kmlines = (
            ExpenseKmLine.query().filter(ExpenseKmLine.sheet_id.in_(sheets_id)).all()
        )
        nb_km = sum([line.km for line in kmlines])

        return total_ht, nb_km

    @classmethod
    def get_total_purchases_on_period(cls, company, start_date, end_date):
        """
        Compute the purchase total HT for a given company on the given period
        """
        from caerp.models.supply.supplier_invoice import (
            SupplierInvoice,
            SupplierInvoiceLine,
        )

        query = DBSESSION.query(non_null_sum(SupplierInvoiceLine.ht))
        query = query.join(SupplierInvoice)
        query = query.filter(SupplierInvoice.company_id == company.id)
        query = query.filter(SupplierInvoice.date.between(start_date, end_date))
        query = query.filter(SupplierInvoice.status == "valid")

        return query.scalar()

    @classmethod
    def get_last_treasury_main_indicator(cls, company):
        """
        Retrieve the main indicator's datas from the last treasury grid
        of a given company
        Return {"date", "label", "value"} of the measure
        """
        from caerp.models.accounting.treasury_measures import (
            TreasuryMeasure,
            TreasuryMeasureGrid,
        )

        main_treasury_measure_id = Config.get_value("treasury_measure_ui", None)
        query = DBSESSION.query(
            TreasuryMeasureGrid.date, TreasuryMeasure.label, TreasuryMeasure.value
        )
        query = query.join(TreasuryMeasureGrid)
        query = query.filter(TreasuryMeasureGrid.company_id == company.id)
        query = query.filter(
            TreasuryMeasure.measure_type_id == main_treasury_measure_id
        )
        query = query.order_by(TreasuryMeasureGrid.date.desc())

        result = query.first()
        if result is not None:
            result = {"date": result[0], "label": result[1], "value": result[2]}
        return result

    @classmethod
    def label_datas_query(cls, company_class, request, only_active=False):
        from caerp.models.user.user import COMPANY_EMPLOYEE, User
        from caerp.models.user.login import Login

        dbsession = request.dbsession
        query = (
            dbsession.query(
                company_class.id,
                company_class.name,
                company_class.code_compta,
                company_class.active,
                func.count(User.id).label("nb_employees"),
                func.group_concat(
                    func.concat(User.lastname, " ", User.firstname)
                ).label("employees_list"),
            )
            .select_from(company_class)
            .outerjoin(COMPANY_EMPLOYEE)
            .outerjoin(User)
            .outerjoin(Login, and_(User.id == Login.user_id, Login.active == 1))
            .group_by(company_class.id)
            .order_by(company_class.name)
        )
        if only_active:
            query = query.filter(company_class.active == 1)
        return query

    @classmethod
    def _get_company_display_option(cls):
        """
        Collect the configuration for the company display option cache
        it as class attribute
        """
        return Config.get_value("companies_label_add_user_name", False)

    @classmethod
    def format_label_from_datas(
        cls, company_class, company_datas, with_select_search_datas=False
    ):
        """
        Return the company's label to display
        Add employees infos to company's name if config ask to
        Add search datas (employees, code_compta) if asked

        company_datas:
            can be either
            - a Company object
            - an SqlAlchemy.Row : (
                id,
                name,
                code_compta,
                active,
                nb_employees,
                employees_list
            )
            - a dict : {
                'id': int,
                'name': str,
                'code_compta': str,
                'active': bool,
                'nb_employees': int,
                'employees_list': str
            }
        """
        employee_in_label = cls._get_company_display_option() == "1"
        if not employee_in_label and not with_select_search_datas:
            if isinstance(company_datas, dict):
                return company_datas["name"]
            else:
                return company_datas.name

        if isinstance(company_datas, company_class):
            actives_employees = company_datas.get_active_employees()
            employees_list = ""
            for employee in actives_employees:
                employees_list += "{} {}, ".format(
                    employee.lastname,
                    employee.firstname,
                )
            employees_list = employees_list[:-2]
            company_datas = {
                "id": company_datas.id,
                "name": company_datas.name,
                "active": company_datas.active,
                "code_compta": company_datas.code_compta,
                "nb_employees": len(actives_employees),
                "employees_list": employees_list,
            }
        elif not isinstance(company_datas, dict):
            company_datas = company_datas._asdict()

        full_label = company_datas["name"]
        if employee_in_label:
            if (
                company_datas["nb_employees"] == 1
                and company_datas["employees_list"].split(" ", 1)[0].lower()
                not in full_label.lower()
            ):
                full_label += " - {}".format(company_datas["employees_list"])
            elif company_datas["nb_employees"] > 1:
                full_label += " ({} entrepreneurs)".format(
                    company_datas["nb_employees"]
                )
            elif company_datas["nb_employees"] < 1 and company_datas["active"]:
                full_label += " (Aucun entrepreneur)"
        if with_select_search_datas:
            full_label += "## {} ({})".format(
                company_datas["employees_list"], company_datas["code_compta"]
            )
        return full_label

    @classmethod
    def get_companies_select_datas(cls, company_class, request, only_active=False):
        select_datas = []
        query = cls.label_datas_query(company_class, request, only_active=only_active)

        for company_datas in query.all():
            select_datas.append(
                (
                    company_datas.id,
                    cls.format_label_from_datas(
                        company_class,
                        company_datas,
                        with_select_search_datas=True,
                    ),
                )
            )
        return select_datas

    @classmethod
    def get_id_by_analytical_account(cls, company_class, analytical_account):
        """
        Return id of the oldest company with given analytical account

        :param class company_class: The Company class
        :param str analytical_account: The analytical account to get
        :returns: Integer or None
        """
        result = (
            DBSESSION()
            .query(company_class.id)
            .filter_by(code_compta=analytical_account)
            .order_by(company_class.id)
            .first()
        )
        if result is not None:
            result = result[0]
        return result

    @classmethod
    def get_companies_by_analytical_account(
        cls, company_class, analytical_account, active_only=False
    ):
        """
        Return all companies with given analytical account

        :param class company_class: The Company class
        :param str analytical_account: The analytical account to get
        :param bool active_only: Wether we want only active companies or not
        :returns: list of companies
        """
        companies_query = (
            DBSESSION()
            .query(company_class)
            .filter(company_class.code_compta == analytical_account)
            .order_by(company_class.id)
        )
        if active_only:
            companies_query = companies_query.filter(company_class.active == True)
        return companies_query.all()

    @classmethod
    def query_for_select_with_trainer(cls, company_class, request):
        """
        Build a query suitable for deform select widgets population

        :param class company_class: The Company class
        :returns: A sqlalchemy query object
        """
        from caerp.models.user.user import User
        from caerp.models.user.login import Login
        from caerp.models.user.group import Group
        from caerp.models.user.access_right import AccessRight

        query = select(company_class.id, company_class.name)
        query = (
            query.join(User, company_class.employees)
            .join(Login)
            .join(Group, Login._groups)
            .join(AccessRight, Group.access_rights)
            .filter(AccessRight.name == "es_trainer")
        )

        query = query.order_by(company_class.name.asc()).distinct()
        return request.dbsession.execute(query)

    @classmethod
    def has_member_with_access_right(cls, company, access_right_name: str) -> bool:
        """
        Check if the company has a member with the given access right

        :param obj company: A Company instance
        :param str access_right_name: The name of the access right to check
        :returns: A boolean
        """
        from caerp.models.user.user import User
        from caerp.models.user.login import Login
        from caerp.models.user.group import Group
        from caerp.models.company import COMPANY_EMPLOYEE
        from caerp.models.user.access_right import AccessRight

        query = (
            select(func.count(User.id))
            .join(COMPANY_EMPLOYEE)
            .join(Login)
            .join(Group, Login._groups)
            .join(AccessRight, Group.access_rights)
            .filter(AccessRight.name == access_right_name)
            .filter(COMPANY_EMPLOYEE.c.company_id == company.id)
        )

        return DBSESSION().execute(query).scalar() > 0

    @classmethod
    def get_employee_ids(cls, company):
        """
        Collect company user_ids
        """
        from caerp.models.company import COMPANY_EMPLOYEE

        query = (
            DBSESSION()
            .query(COMPANY_EMPLOYEE.c.account_id)
            .filter(COMPANY_EMPLOYEE.c.company_id == company.id)
        )

        return [a[0] for a in query]

    @classmethod
    def get_active_employees(cls, company):
        """
        Collect active employees
        """
        return [
            employee
            for employee in company.employees
            if employee.login and employee.login.active
        ]

    @classmethod
    def employs(cls, company, uid):
        """
        Check if the given company employs User with id uid

        :param obj company: The current Company
        :param int uid: The user id
        :rtype: bool
        """
        from caerp.models.company import COMPANY_EMPLOYEE

        query = DBSESSION().query(COMPANY_EMPLOYEE)
        query = query.filter(
            COMPANY_EMPLOYEE.c.company_id == company.id,
            COMPANY_EMPLOYEE.c.account_id == uid,
        )
        return query.count() > 0

    @classmethod
    def get_contribution(cls, company_id, prefix=""):
        return cls.get_rate(company_id, "contribution", prefix)

    @classmethod
    def get_rate(cls, company_id: int, rate_name: str, prefix: str = "") -> float:
        """
        Renvoie le taux de contribution à appliquer pour cette enseigne
        (assurance/contribution ou autre)

        Les CustomInvoiceBookEntry module créé par caerp ont un "name"
        qui correspond à l'attribut de Company qui permet d'overrider le
        taux associé

        :param id: Company id
        :param str prefix: configuration key prefix (ex: internal)
        """
        from caerp.models.company import Company
        from caerp.models.accounting.bookeeping import (
            CustomInvoiceBookEntryModule,
        )

        attrname = "{}{}".format(prefix, rate_name)

        if hasattr(Company, attrname):
            rate = (
                DBSESSION()
                .query(getattr(Company, attrname))
                .filter(Company.id == company_id)
                .scalar()
            )
        else:
            rate = None

        if rate is None:
            rate = CustomInvoiceBookEntryModule.get_percentage(rate_name, prefix)
        return rate

    @classmethod
    def get_rate_level(cls, company_id: int, rate_name: str, prefix: str = "") -> str:
        """
        Renvoie le niveau (cae/company/document) auquel la contribution est
        définie

        Note : Les CustomInvoiceBookEntry module créé par caerp ont un "name"
        qui correspond à l'attribut de Company qui permet d'overrider le
        taux associé

        :param id: Company id
        :param str prefix: configuration key prefix (ex: internal)
        """
        from caerp.models.company import Company
        from caerp.models.accounting.bookeeping import (
            CustomInvoiceBookEntryModule,
        )

        attrname = "{}{}".format(prefix, rate_name)

        if hasattr(Company, attrname):
            rate = (
                DBSESSION()
                .query(getattr(Company, attrname))
                .filter(Company.id == company_id)
                .scalar()
            )
        else:
            rate = None
        result = None
        if rate is None:
            rate = CustomInvoiceBookEntryModule.get_percentage(rate_name, prefix)
            if rate is not None:
                result = "cae"
        else:
            result = "company"
        return result

    @classmethod
    def _get_account(cls, instance: "Company", account_label, prefix=""):
        """
        Collect the instance's accounting account for the given label

        :param obj instance: the company
        :param str account_label: The account_label like

            third_party_customer
            general_customer
            general_supplier
            third_party_supplier

            general_expense
        """
        if account_label == "general_expense":
            # inconsistent naming, but risky renaming, so handle it as an exception.
            cae_label = "%scompte_cg_ndf" % prefix

        else:
            cae_label = "%scae_%s_account" % (prefix, account_label)

        company_label = "%s%s_account" % (prefix, account_label)
        result = getattr(instance, company_label)

        if not result:
            result = Config.get_value(cae_label, default="")
        return result

    @classmethod
    def get_general_customer_account(cls, instance, prefix=""):
        return cls._get_account(instance, "general_customer", prefix)

    @classmethod
    def get_third_party_customer_account(cls, instance, prefix=""):
        return cls._get_account(instance, "third_party_customer", prefix)

    @classmethod
    def get_general_supplier_account(cls, instance, prefix=""):
        return cls._get_account(instance, "general_supplier", prefix)

    @classmethod
    def get_third_party_supplier_account(cls, instance, prefix=""):
        return cls._get_account(instance, "third_party_supplier", prefix)

    @classmethod
    def get_general_expense_account(cls, instance, prefix=""):
        return cls._get_account(instance, "general_expense", prefix)
