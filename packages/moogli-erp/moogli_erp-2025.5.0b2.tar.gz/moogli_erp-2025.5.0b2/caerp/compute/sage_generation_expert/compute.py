import datetime
from zope.interface import implementer

from caerp.interfaces import ITreasuryProducer

from caerp.compute.sage.invoice import (
    InternalInvoiceExportProducer,
    InvoiceExportProducer,
)
from caerp.compute.sage.expense import (
    SageExpenseMain,
    ExpenseExportProducer,
)
from caerp.compute.sage.expense_payment import (
    ExpensePaymentExportProducer,
)
from caerp.compute.sage.payment import (
    InternalPaymentExportProducer,
    PaymentExportProducer,
)
from caerp.compute.sage.supplier_invoice import (
    InternalSupplierInvoiceExportProducer,
    SupplierInvoiceExportProducer,
)
from caerp.compute.sage.supplier_invoice_payment import (
    SupplierPaymentExportProducer as SageSupplierPaymentProducer,
    InternalSupplierPaymentExportProducer as SageInternalSupplierPaymentProducer,
    SupplierUserPaymentExportProducer as SageSupplierUserPaymentProducer,
)


# VENTES
@implementer(ITreasuryProducer)
class InvoiceProducer(InvoiceExportProducer):
    """
    Custom producer pour les factures
    c'est lui qui produit les lignes d'export pour les factures
    ici il s'assure de vire une des deux lignes analytiques/générales
    """

    use_general = False
    _available_modules = {}


@implementer(ITreasuryProducer)
class InternalInvoiceProducer(InternalInvoiceExportProducer):
    use_general = False
    _available_modules = {}


@implementer(ITreasuryProducer)
class PaymentProducer(PaymentExportProducer):
    use_general = False


@implementer(ITreasuryProducer)
class InternalPaymentProducer(InternalPaymentExportProducer):
    use_general = False


# NDD
class MainExpense(SageExpenseMain):
    """
    Main expense export module
    """

    def _yield_grouped_expenses(self, category: str = "0"):
        """
        yield entries grouped by type
        """
        total = self.expense.get_total(category)
        if not total:
            return

        # An écriture for every category
        for charge in self.expense.get_lines_by_type(category):
            expense_type = charge[0].expense_type
            ht = sum([line.total_ht for line in charge])
            tva = sum([line.total_tva for line in charge])
            # An écriture summing all expenses
            yield self._credit(ht + tva, libelle=self.libelle, date=self.date)
            yield from self._write_complete_debit(
                expense_type, ht, tva, libelle=self.libelle, date=self.date
            )

    def _yield_detailed_expenses(self, category: str = "0"):
        return super()._yield_detailed_expenses(category)


@implementer(ITreasuryProducer)
class ExpenseProducer(ExpenseExportProducer):
    _default_modules = (MainExpense,)
    use_general = False


@implementer(ITreasuryProducer)
class ExpensePaymentProducer(ExpensePaymentExportProducer):
    use_general = False


# FOURNISSEURS
@implementer(ITreasuryProducer)
class SupplierInvoiceProducer(SupplierInvoiceExportProducer):
    use_general = False


@implementer(ITreasuryProducer)
class InternalSupplierInvoiceProducer(InternalSupplierInvoiceExportProducer):
    use_general = False


@implementer(ITreasuryProducer)
class SupplierPaymentProducer(SageSupplierPaymentProducer):
    use_general = False


@implementer(ITreasuryProducer)
class InternalSupplierPaymentProducer(SageInternalSupplierPaymentProducer):
    use_general = False


@implementer(ITreasuryProducer)
class SupplierUserPaymentProducer(SageSupplierUserPaymentProducer):
    use_general = False
