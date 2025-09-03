import logging
import sys
import inspect
import transaction

from collections import OrderedDict
from sqlalchemy.orm import load_only
from zope.sqlalchemy import mark_changed

from caerp_base.models.base import DBSESSION
from caerp.models.listeners import SQLAListeners
from caerp.scripts.utils import command


class DatabaseCleaner:
    """
    Class used to clean the database and remove all informations not concerning
    the given company
    """

    def __init__(self, company, logger):
        self.logger = logger
        self.company_id = company.id
        self.session = DBSESSION()
        self.methods = self._load_clean_methods()
        print(" + Removing listeners")
        SQLAListeners.stop_listening()

    def _load_clean_methods(self):
        methods = {}
        for method_name, method in inspect.getmembers(self, inspect.ismethod):
            if method_name.startswith("_clean_"):
                methods[method_name] = method

        keys = list(methods.keys())
        keys.sort()
        result = OrderedDict()
        for key in keys:
            result[key] = methods[key]
        return result

    # Clean all contents
    def _clean_all_competences(self):
        from caerp.models.competence import (
            CompetenceDeadline,
            CompetenceScale,
            CompetenceOption,
            CompetenceSubOption,
        )

        print(" + Cleaning competences")
        self.session.execute("delete from competence_grid_sub_item")
        self.session.execute("delete from competence_grid_item")
        self.session.execute("delete from competence_grid")
        self.session.execute("delete from competence_requirement")
        mark_changed(self.session)

        for item in CompetenceDeadline.query():
            self.session.delete(item)

        for item in CompetenceScale.query():
            self.session.delete(item)

        for item in CompetenceOption.query():
            self.session.delete(item)

        for item in CompetenceSubOption.query():
            self.session.delete(item)

    def _clean_all_accompagnement(self):
        from caerp.models.activity import Event

        print(" + Cleaning accompagnement")
        for item in Event.query().options(load_only("id")):
            self.session.delete(item)

        mark_changed(self.session)

    def _clean_all_userdatas(self):
        from caerp.models.user.userdatas import UserDatas

        print(" + Cleaning userdatas")
        for item in UserDatas.query().options(load_only("id")):
            self.session.delete(item)

        mark_changed(self.session)

    def _clean_all_holidays(self):
        print(" + Cleaning holidays")
        self.session.execute("delete from holiday;")
        mark_changed(self.session)

    def _clean_all_mail_history(self):
        print(" + Cleaning mail history")
        self.session.execute("delete from mail_history;")
        mark_changed(self.session)

    def _clean_all_templates(self):
        from caerp.models.files import Template

        print(" + Cleaning templates")
        self.session.execute("delete from template_history")
        mark_changed(self.session)

        for item in Template.query().options(load_only("id")):
            self.session.delete(item)

        mark_changed(self.session)

    # Clean tout ce qui n'est pas associé à l'enseigne
    def _clean_a_tasks(self):
        from caerp.models.task import Task

        print(" + Cleaning tasks")
        i = 0
        tasks = (
            Task.query()
            .options(load_only("id"))
            .filter(Task.company_id != self.company_id)
        )
        cur = 0
        all = tasks.count()
        print("   {} left".format(all))
        for task in tasks:
            if i > 1000:
                print("   {} left".format(all - cur))
                mark_changed(self.session)
                self.session.flush()
                transaction.commit()
                transaction.begin()
                cur += i
                i = 0
            self.session.delete(task)
            i += 1

        mark_changed(self.session)

    def _clean_a_expenses(self):
        from caerp.models.expense.sheet import ExpenseSheet

        print(" + Cleaning expenses")
        query = self.session.query(ExpenseSheet).filter(
            ExpenseSheet.company_id != self.company_id
        )
        for expense in query:
            self.session.delete(expense)

    def _clean_b_third_party(self):
        """
        Remove all third parties not related to the current company
        """
        from caerp.models.third_party import ThirdParty

        print(" + Cleaning third party")
        for item in ThirdParty.query().filter(ThirdParty.company_id != self.company_id):
            self.session.delete(item)

    def _clean_b_bank_remittance(self):
        # lancé après le nettoyage des task -> des paiements
        from caerp.models.task.payment import Payment, BankRemittance

        print(" + Cleaning bank remittances")
        for item in (
            BankRemittance.query()
            .options(load_only("id"))
            .filter(
                BankRemittance.id.notin_(
                    self.session.query(Payment.bank_remittance_id).filter(
                        Payment.bank_remittance_id != None
                    )
                )
            )
        ):
            self.session.delete(item)

        print(" + Cleaning payments")
        # Cas des bases où la cascade est peut-être mal configurée
        for item in Payment.query().filter(Payment.task_id == None):
            self.session.delete(item)

    def _clean_supplier_orders(self):
        from caerp.models.supply.supplier_order import SupplierOrder

        print(" + Cleaning supplier orders")
        for item in (
            SupplierOrder.query()
            .options(load_only("id"))
            .filter(SupplierOrder.company_id != self.company_id)
        ):
            self.session.delete(item)

    def _clean_supplier_invoices(self):
        from caerp.models.supply.supplier_invoice import SupplierInvoice

        print(" + Cleaning supplier invoices")
        for item in (
            SupplierInvoice.query()
            .options(load_only("id"))
            .filter(SupplierInvoice.company_id != self.company_id)
        ):
            self.session.delete(item)

    def _clean_c_project(self):
        from caerp.models.project import Project

        print(" + Cleaning projects")
        for item in (
            Project.query()
            .options(load_only("id"))
            .filter(Project.company_id != self.company_id)
        ):
            self.session.delete(item)

    def _clean_a_sale_product(self):
        # On supprime d'abord les Work pour éviter des soucis de forignkey
        # work_item -> base_sale_product_id
        from caerp.models.sale_product.work import SaleProductWork

        print(" + Cleaning sale products")
        for item in (
            SaleProductWork.query()
            .options(load_only("id"))
            .filter(SaleProductWork.company_id != self.company_id)
        ):
            self.session.delete(item)

        from caerp.models.sale_product import (
            SaleProductServiceDelivery,
            SaleProductWorkForce,
            SaleProductMaterial,
            SaleProductProduct,
        )

        for pclass in (
            SaleProductServiceDelivery,
            SaleProductWorkForce,
            SaleProductMaterial,
            SaleProductProduct,
        ):
            for item in (
                pclass.query()
                .options(load_only("id"))
                .filter(pclass.company_id != self.company_id)
            ):
                self.session.delete(item)

    def _clean_a_price_study(self):
        from caerp.models.price_study.price_study import PriceStudy

        print(" + Cleaning price study")
        for item in PriceStudy.query().options(load_only("id")):
            if item.get_company_id() != self.company_id:
                self.session.delete(item)

    def _clean_accounting(self):
        from caerp.models.accounting.base import BaseAccountingMeasureGrid

        print(" + Cleaning accounting")
        self.session.execute("delete from accounting_operation")
        self.session.execute("delete from accounting_operation_upload")
        mark_changed(self.session)
        for item in (
            BaseAccountingMeasureGrid.query()
            .options(load_only("id"))
            .filter(BaseAccountingMeasureGrid.company_id != self.company_id)
        ):
            self.session.delete(item)

    def _clean_y_users(self):
        from caerp.models.company import Company
        from caerp.models.user.user import User

        print(" + Cleaning users")
        self.session.execute("delete from user_connections")
        # On a besoin de celle-ci car parfois on a des doublons dans
        # company_employee qui posent problème
        self.session.execute(
            "delete from company_employee where "
            "company_id != {}".format(self.company_id)
        )
        mark_changed(self.session)
        self.session.flush()

        ids = [e.id for e in Company.get(self.company_id).employees]
        users = (
            self.session.query(User)
            .filter(User.special == 0)
            .filter(User.id.notin_(ids))
        )
        for user in users:
            self.session.delete(user)

    def _clean_z_companies(self):
        from caerp.models.company import Company

        print(" + Cleaning companies")
        query = self.session.query(Company).options(load_only("id"))
        query = query.filter(Company.id != self.company_id)

        for company in query:
            if company.header_file:
                self.session.delete(company.header_file)
            if company.logo_file:
                self.session.delete(company.logo_file)
            self.session.delete(company)

    def run_method(self, method_name):
        """
        Runs a single clean method

        :param str method_name: The name with or without the _clean_ prefix
        """
        if not method_name.startswith("_clean_"):
            method_name = "_clean_%s" % method_name
        if method_name in self.methods:
            self.logger.debug("Step : {0}".format(method_name))
            self.methods[method_name]()
            transaction.commit()
            transaction.begin()

    def run(self):
        for key in self.methods:
            self.run_method(key)

    def add_admin(self, env):
        from caerp.models.user.user import User
        from caerp.models.user.login import Login
        from caerp.models.company import Company

        user = (
            self.session.query(User)
            .join(Login)
            .filter(Login.login.in_(["admin", "admin.majerti", "endi_admin", "kilya"]))
            .first()
        )

        if user is None:
            print("No admin user found")
            print(
                "caerp-admin config.ini useradd --user=admin --group=admin --email=<email>"
            )

        # Pas utile d'avoir l'admin sur l'enseigne et perturbant pour l'ES
        # company = Company.get(self.company_id)
        # if user not in company.employees:
        #     company.employees.append(user)
        #     self.session.merge(company)


def company_export_command(arguments, env):
    """
    Entry point for the company export tools
    """
    from caerp.models.company import Company

    logger = logging.getLogger(__name__)
    cid = arguments.get("CID")

    if cid is None:
        raise Exception("Missing mandatory cid")
    else:
        cid = int(cid)

    company = Company.get(cid)
    if company is None:
        raise Exception("No company with id {}".format(cid))

    print(
        "Attention, vous vous apprêtez à nettoyer la base de données et à "
        "ne conserver que les données de l'enseigne {}, cette action "
        "est irréversible, assrez-vous d'avoir sauvegardé : la base de "
        "données caerp, la base de données caerp-payment, les fichiers "
        "déposés.\n(y/N)".format(cid)
    )
    choice = input().lower()

    if choice not in ("y", "yes", "o", "oui"):
        print("Canceled")
        sys.exit(1)
    else:
        print("Continue")
        print(" + Cleaning")
        cleaner = DatabaseCleaner(company, logger)
        cleaner.run()
        cleaner.add_admin(env)
        print(" + Done")


def company_export_entry_point():
    """Company export utilitiy tool

    Clean the databases configured in the config_uri file and the files
    directory

    Usage:
        caerp-company-export <config_uri> company CID

    Arguments:
        CID  Company object id

    Options:
        -h --help             Show this screen
    """

    def callback(arguments, env):
        if arguments["company"]:
            func = company_export_command
        return func(arguments, env)

    try:
        return command(callback, company_export_entry_point.__doc__)
    finally:
        pass
