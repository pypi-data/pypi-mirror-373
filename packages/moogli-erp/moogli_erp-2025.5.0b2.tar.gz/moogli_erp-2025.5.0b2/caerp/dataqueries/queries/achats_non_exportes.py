from sqlalchemy import or_

from caerp.dataqueries.base import BaseDataQuery
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.utils import strings
from caerp.utils.dataqueries import dataquery_class


@dataquery_class()
class AchatsNonExportesQuery(BaseDataQuery):

    name = "achats_non_exportes"
    label = "Liste des achats non exportés en compta"
    description = """
    Liste de tous les achats (NDD et factures fournisseurs) validés et pas 
    encore exportées en comptabilité à l'instant T.
    """

    def headers(self):
        headers = [
            "Type d'achat (NDD / FF)",
            "Numéro",
            "Période",
            "Code analytique",
            "Enseigne",
            "Montant HT",
            "Montant TVA",
            "Montant TTC",
        ]
        return headers

    def data(self):
        data = []
        # Expense sheets
        expense_sheets = (
            ExpenseSheet.query()
            .filter(ExpenseSheet.status == "valid")
            .filter(
                or_(
                    ExpenseSheet.expense_exported == 0,
                    ExpenseSheet.purchase_exported == 0,
                )
            )
            .order_by(ExpenseSheet.date)
        )
        for s in expense_sheets:
            sheet_data = [
                s.date,
                "NDD",
                s.official_number,
                f"{strings.month_name(s.month, True)} {s.year}",
                s.company.code_compta,
                s.company.name,
                strings.format_amount(s.total_ht, grouping=False),
                strings.format_amount(s.total_tva, grouping=False),
                strings.format_amount(s.total, grouping=False),
            ]
            data.append(sheet_data)
        # Supplier invoices
        supplier_invoices = (
            SupplierInvoice.query()
            .filter(SupplierInvoice.status == "valid")
            .filter(SupplierInvoice.exported == 0)
            .order_by(SupplierInvoice.date)
        )
        for i in supplier_invoices:
            invoice_data = [
                i.date.date(),
                "FF",
                i.official_number,
                f"{strings.month_name(i.date.month, True)} {i.date.year}",
                i.company.code_compta,
                i.company.name,
                strings.format_amount(i.total_ht, grouping=False),
                strings.format_amount(i.total_tva, grouping=False),
                strings.format_amount(i.total, grouping=False),
            ]
            data.append(invoice_data)
        # On trie par date puis on la supprime pour ne garder que la période
        data.sort()
        [item.pop(0) for item in data]
        return data
