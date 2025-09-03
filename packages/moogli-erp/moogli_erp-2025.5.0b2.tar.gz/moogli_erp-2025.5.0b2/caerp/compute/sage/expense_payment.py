import logging
import datetime

from zope.interface import implementer
from caerp.interfaces import ITreasuryProducer
from caerp.utils.strings import format_account
from .base import (
    double_lines,
    BaseSageBookEntryFactory,
    filter_accounting_entry,
)

logger = log = logging.getLogger(__name__)


class SageExpensePaymentMain(BaseSageBookEntryFactory):
    static_columns = (
        "reference",
        "code_journal",
        "date",
        "mode",
        "libelle",
        "type_",
        "num_analytique",
        "code_taxe",
    )

    variable_columns = (
        "compte_cg",
        "compte_tiers",
        "debit",
        "credit",
    )

    _label_template_key = "bookentry_expense_payment_main_label_template"

    @property
    def libelle(self):
        return (
            self.label_template.format(
                beneficiaire=format_account(self.expense.user, reverse=False),
                beneficiaire_LASTNAME=self.expense.user.lastname.upper(),
                code_compta=self.expense.company.code_compta,
                expense=self.expense,
                expense_date=datetime.date(self.expense.year, self.expense.month, 1),
                titre=self.expense.title if self.expense.title else "",
            )
            .replace("None", "")
            .strip()
        )

    def set_payment(self, payment):
        self.expense = payment.expense
        self.payment = payment
        self.company = self.expense.company
        self.user = self.expense.user
        # Ne sert à rien pour l'instant (si on déplace le compte tiers, si)
        self.user = self.expense.user

    @property
    def reference(self):
        return self.expense.official_number

    @property
    def code_journal(self):
        return self.payment.bank.code_journal

    @property
    def date(self):
        return self.payment.date.date()

    @property
    def mode(self):
        return self.payment.mode

    @property
    def num_analytique(self):
        return self.company.code_compta

    @property
    def code_taxe(self):
        if "code_tva_ndf" in self.config:
            return self.config["code_tva_ndf"]
        else:
            return ""

    @double_lines
    def credit_bank(self, val):
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.payment.bank.compte_cg,
            credit=val,
        )
        return entry

    @double_lines
    def debit_user(self, val):
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.company.get_general_expense_account(),
            compte_tiers=self.user.compte_tiers,
            debit=val,
        )
        return entry

    def yield_entries(self):
        yield self.credit_bank(self.payment.amount)
        yield self.debit_user(self.payment.amount)


class SageExpensePaymentWaiver(SageExpensePaymentMain):
    """
    Module d'export pour les paiements par abandon de créance
    """

    _label_template_key = "bookentry_expense_payment_waiver_label_template"

    @property
    def code_journal(self):
        res = self.config.get("code_journal_waiver_ndf")
        if not res:
            res = self.config["code_journal_ndf"]
        return res

    @property
    def mode(self):
        return "Abandon de créance"

    @property
    def code_taxe(self):
        return ""

    @double_lines
    def credit_bank(self, val):
        """
        Un compte CG spécifique aux abandons de créances est utilisé ici
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.config["compte_cg_waiver_ndf"],
            credit=val,
        )
        return entry


@implementer(ITreasuryProducer)
class ExpensePaymentExportProducer:
    main_module_factory = SageExpensePaymentMain
    waiver_module_factory = SageExpensePaymentWaiver
    _available_modules = {}
    use_analytic = True
    use_general = True

    def __init__(self, context, request):
        self.request = request
        self.config = request.config
        self.modules = []
        self.main_module = self.main_module_factory(context, request)
        self.waiver_module = self.waiver_module_factory(context, request)

    def get_modules(self, expense_payment):
        """
        Retrieve the modules to use regarding the payment to export

        :param obj expense_payment: A ExpensePayment object
        :results: The module to use
        :rtype: list
        """
        if expense_payment.waiver:
            module = self.waiver_module
        else:
            module = self.main_module

        return [module]

    def _get_item_book_entries(self, payment):
        """
        Return book entries for the given payment

        :param obj payment: A ExpensePayment object

        :results: An iterable with couples of G lines and A lines
        """
        for module in self.get_modules(payment):
            module.set_payment(payment)
            for entry in module.yield_entries():
                gen_line, analytic_line = entry
                if self.use_general:
                    yield filter_accounting_entry(gen_line)
                if self.use_analytic:
                    yield filter_accounting_entry(analytic_line)

    def get_item_book_entries(self, payment):
        return list(self._get_item_book_entries(payment))

    def get_book_entries(self, payments):
        """
        Return book entries for the given payments

        :param list payments: ExpensePayment objects
        :results: A list of book entries
        """
        result = []
        for payment in payments:
            result.extend(list(self._get_item_book_entries(payment)))
        return result
