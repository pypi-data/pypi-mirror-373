import logging

from caerp.models.expense.sheet import BaseExpenseLine
from caerp.models.project import Project, Business
from caerp.models.supply.supplier_invoice import SupplierInvoiceLine
from caerp.models.third_party import Customer


logger = logging.getLogger(__name__)


class LinkedExpensesListPanel:
    """
    List both expenses and supplier invoices related to context

    Context can be either project, business, or customer
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if isinstance(self.context, Project):
            filter_col = "project_id"
        elif isinstance(self.context, Business):
            filter_col = "business_id"
        elif isinstance(self.context, Customer):
            filter_col = "customer_id"
        else:
            raise Exception("Unsupported context type")

        logger.info(f"Display linked expenses for {filter_col} {self.context.id}")

        expense_lines = (
            BaseExpenseLine.query()
            .filter(getattr(BaseExpenseLine, filter_col) == self.context.id)
            .order_by(BaseExpenseLine.date.desc())
            .all()
        )
        supplier_invoice_lines = (
            SupplierInvoiceLine.query()
            .filter(getattr(SupplierInvoiceLine, filter_col) == self.context.id)
            .order_by(SupplierInvoiceLine.id.desc())
            .all()
        )

        # Compute summary
        total_ht = 0
        total_ttc = 0
        with_tva_on_margin = False
        total_tva_on_margin = 0
        expenses_ht = 0
        expenses_ttc = 0
        for line in expense_lines:
            if line.expense_type.tva_on_margin:
                with_tva_on_margin = True
                total_tva_on_margin += line.total
            expenses_ht += line.ht
            expenses_ttc += line.total
        supplier_invoices_ht = 0
        supplier_invoices_ttc = 0
        for line in supplier_invoice_lines:
            if line.expense_type.tva_on_margin:
                with_tva_on_margin = True
                total_tva_on_margin += line.total
            supplier_invoices_ht += line.ht
            supplier_invoices_ttc += line.total
        total_ht = expenses_ht + supplier_invoices_ht
        total_ttc = expenses_ttc + supplier_invoices_ttc

        return {
            "expense_lines": expense_lines,
            "supplier_invoice_lines": supplier_invoice_lines,
            "total_ht": total_ht,
            "total_ttc": total_ttc,
            "with_tva_on_margin": with_tva_on_margin,
            "total_tva_on_margin": total_tva_on_margin,
            "expenses_ht": expenses_ht,
            "expenses_ttc": expenses_ttc,
            "supplier_invoices_ht": supplier_invoices_ht,
            "supplier_invoices_ttc": supplier_invoices_ttc,
        }


def includeme(config):
    config.add_panel(
        LinkedExpensesListPanel,
        "linked_expenses",
        renderer="panels/expense/linked_expenses.mako",
    )
