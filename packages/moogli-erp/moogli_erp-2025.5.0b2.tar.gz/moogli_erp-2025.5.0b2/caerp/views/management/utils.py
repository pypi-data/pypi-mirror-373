"""
Fonctions utilitaires pour les tableaux de suivi de gestion
"""
from sqlalchemy import and_, or_

from caerp_base.models.base import DBSESSION
from caerp.models.company import Company
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.models.task import Task


def compute_diff_percent(new_value, init_value):
    """
    Calcule l'écart en pourcentage entre 2 valeurs
    """
    if init_value == 0 or new_value == 0:
        if new_value > init_value:
            return 100
        elif new_value < init_value:
            return -100
        else:
            return 0
    else:
        return (init_value - new_value) / abs(init_value) * -100


def get_active_companies_on_period(period_start, period_end):
    """
    Retourne les enseignes "actives" sur une période donnée
    (qui ont au moins un document, une note de dépense,
    ou une facture fournisseur validé sur la période)
    """
    query = DBSESSION().query(Company)
    tasks_condition = and_(
        Task.type_.in_(Task.invoice_types),
        Task.status == "valid",
        Task.date.between(period_start, period_end),
    )
    expenses_condition = and_(
        ExpenseSheet.status == "valid",
        ExpenseSheet.date.between(period_start, period_end),
    )
    supplier_invoices_condition = and_(
        SupplierInvoice.status == "valid",
        SupplierInvoice.date.between(period_start, period_end),
    )
    query = query.filter(
        or_(
            Company.tasks.any(tasks_condition),
            Company.expense.any(expenses_condition),
            Company.supplier_invoices.any(supplier_invoices_condition),
        )
    )
    query = query.order_by(Company.active.desc(), Company.name)
    return query
