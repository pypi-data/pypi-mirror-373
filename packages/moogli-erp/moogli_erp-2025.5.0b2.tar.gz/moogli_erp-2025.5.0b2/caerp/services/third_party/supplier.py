from sqlalchemy import func, select

from caerp.models.expense.sheet import ExpenseLine
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.models.supply.supplier_order import SupplierOrder
from caerp.models.third_party.supplier import Supplier


def is_supplier_deletable(request, supplier: Supplier) -> bool:
    q1 = select(func.count(SupplierOrder.id)).where(
        SupplierOrder.supplier_id == supplier.id
    )
    q2 = select(func.count(SupplierInvoice.id)).where(
        SupplierInvoice.supplier_id == supplier.id
    )
    q3 = select(func.count(ExpenseLine.id)).where(
        ExpenseLine.supplier_id == supplier.id
    )
    return (
        supplier.archived
        and request.dbsession.execute(q1).scalar() == 0
        and request.dbsession.execute(q2).scalar() == 0
        and request.dbsession.execute(q3).scalar() == 0
    )
