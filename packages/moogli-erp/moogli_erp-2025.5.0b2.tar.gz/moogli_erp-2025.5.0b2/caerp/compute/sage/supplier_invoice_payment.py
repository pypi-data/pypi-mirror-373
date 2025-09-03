import logging

from zope.interface import implementer

from caerp.interfaces import ITreasuryProducer
from .base import (
    double_lines,
    BaseSageBookEntryFactory,
    filter_accounting_entry,
)
from ...utils.strings import format_account

logger = log = logging.getLogger(__name__)


class BaseSageSupplierPayment(BaseSageBookEntryFactory):
    """
    Base commune aux paiements de la part CAE et pars ES.

    (qui sont exportés conjointement)
    """

    static_columns = (
        "num_caerp",
        "code_journal",
        "date",
        "mode",
        "libelle",
        "type_",
        "num_analytique",
        "code_taxe",
        "reference",
        "supplier_label",
        "company_name",
        "user_name",
    )

    variable_columns = (
        "compte_cg",
        "compte_tiers",
        "debit",
        "credit",
    )

    @property
    def reference(self):
        if self.payment.bank_remittance_id in (None, ""):
            return str(self.supplier_invoice.official_number)
        else:
            return "{}/{}".format(
                self.supplier_invoice.official_number, self.payment.bank_remittance_id
            )

    @property
    def code_journal(self):
        return self.payment.bank.code_journal

    @property
    def num_caerp(self):
        return str(self.payment.id)

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
        return self.config.get("code_tva_ndf")

    @property
    def supplier_label(self):
        return self.supplier.label

    @property
    def company_name(self):
        return self.company.name

    @property
    def user_name(self):
        if not self.user:
            return ""
        return self.user.label

    def set_payment(self, payment):
        self.payment = payment
        self.supplier_invoice = payment.supplier_invoice
        self.company = payment.supplier_invoice.company
        self.supplier = payment.supplier_invoice.supplier
        self.user = payment.supplier_invoice.payer


class SageSupplierUserPaymentMain(BaseSageSupplierPayment):
    """
    Facture fournisseur, remboursement à l'ES de sa part avancée
    """

    _label_template_key = "bookentry_supplier_invoice_user_payment_label_template"

    @property
    def libelle(self):
        return (
            self.label_template.format(
                supplier_invoice=self.supplier_invoice,
                company=self.company,
                user=self.user,
                supplier=self.supplier,
                beneficiaire=format_account(self.user, reverse=False),
                beneficiaire_LASTNAME=self.user.lastname.upper(),
            )
            .replace("None", "")
            .strip()
        )

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


class SageSupplierUserPaymentWaiver(SageSupplierUserPaymentMain):
    _label_template_key = (
        "bookentry_supplier_invoice_user_payment_waiver_label_template"
    )

    @property
    def code_journal(self):
        return self.config.get(
            "code_journal_waiver_ndf",
            self.config["code_journal_ndf"],
        )

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


class SageSupplierPaymentMain(BaseSageSupplierPayment):
    """
    Facture fournisseur, paiements fournisseur
    """

    _label_template_key = "bookentry_supplier_payment_label_template"

    @property
    def libelle(self):
        return (
            self.label_template.format(
                supplier_invoice=self.supplier_invoice,
                company=self.company,
                supplier=self.supplier,
            )
            .replace("None", "")
            .strip()
        )

    def _get_compte_cg(self):
        return self.payment.bank.compte_cg

    @double_lines
    def credit_bank(self, val):
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_compte_cg(),
            credit=val,
        )
        return entry

    @double_lines
    def debit_supplier(self, val):
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.supplier.get_general_account(prefix=self.config_key_prefix),
            compte_tiers=self.supplier.get_third_party_account(
                prefix=self.config_key_prefix
            ),
            debit=val,
        )
        return entry

    def yield_entries(self):
        yield self.credit_bank(self.payment.amount)
        yield self.debit_supplier(self.payment.amount)


class InternalSageSupplierPaymentMain(SageSupplierPaymentMain):
    config_key_prefix = "internal"

    @property
    def code_journal(self):
        return self._get_config_value("code_journal_paiements_frns")

    @property
    def mode(self):
        return "interne"

    @property
    def reference(self):
        return str(self.supplier_invoice.official_number)

    def _get_compte_cg(self):
        return self.config.get("internalbank_general_account")


class BaseSupplierPaymentExport:
    use_analytic = True
    use_general = True
    waiver_module = None
    main_module = None

    def __init__(self, context, request):
        self.request = request
        self.config = request.config
        self.modules = []
        for module in self.get_modules(context):
            if module is not None:
                self.modules.append(module(context, request))

    def get_modules(self, payment):
        if self.waiver_module and payment.waiver:
            module = self.waiver_module
        else:
            module = self.main_module

        return [module]

    def _get_item_book_entries(self, supplier_payment):
        """
        Return book entries for the given supplier payment

        :param obj payment: A SupplierSupplierPayment object

        :results: An iterable with couples of G lines and A lines
        """
        for module in self.modules:
            module.set_payment(supplier_payment)
            for entry in module.yield_entries():
                gen_line, analytic_line = entry
                if self.use_general:
                    yield filter_accounting_entry(gen_line)
                if self.use_analytic:
                    yield filter_accounting_entry(analytic_line)

    def get_item_book_entries(self, supplier_payment):
        return list(self._get_item_book_entries(supplier_payment))

    def get_book_entries(self, supplier_payments):
        """
        Return book entries for the given supplier invoice payments

        :param list supplier_payments: BaseSupplierPayment objects
        :results: A list of book entries
        """
        result = []
        for supplier_payment in supplier_payments:
            result.extend(list(self._get_item_book_entries(supplier_payment)))
        return result


@implementer(ITreasuryProducer)
class SupplierPaymentExportProducer(BaseSupplierPaymentExport):
    main_module = SageSupplierPaymentMain


@implementer(ITreasuryProducer)
class InternalSupplierPaymentExportProducer(BaseSupplierPaymentExport):
    main_module = InternalSageSupplierPaymentMain


@implementer(ITreasuryProducer)
class SupplierUserPaymentExportProducer(BaseSupplierPaymentExport):
    main_module = SageSupplierUserPaymentMain
    waiver_module = SageSupplierUserPaymentWaiver
