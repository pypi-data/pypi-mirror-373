import logging
from typing import Union
from zope.interface import implementer

from caerp.interfaces import IPaymentStateManager
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.task import Invoice
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.models.action_manager import ActionManager, Action
from caerp.utils.strings import PAID_STATUS
from caerp.utils.status_rendering import STATUS_ICON


logger = logging.getLogger(__name__)


def invoice_paid_status_callback(request, task: Invoice, **kw):
    """
    Update the current invoice acl
    Args:
        request (Request): The current pyramid request
        task (Invoice): The current Invoice

    Returns:
        Invoice: The updated Invoice
    """
    return task


def supplier_invoice_paid_status_callback(
    request, supplier_invoice: SupplierInvoice, **kw
):
    logger.debug("In the supplier invoice paid status callback")
    force_resulted = kw.get("force_resulted", False)
    supplier_invoice.check_supplier_resulted(force_resulted=force_resulted)
    supplier_invoice.check_worker_resulted(force_resulted=force_resulted)
    request.dbsession.merge(supplier_invoice)
    return supplier_invoice


def get_paid_status_manager(doctype: str, callbacks: dict = {}) -> ActionManager:
    # Build an ActionManager and add the statuses waiting/paid/resulted
    manager = ActionManager()
    global_callback = callbacks.get("__all__")
    for status in (
        "waiting",
        "paid",
        "resulted",
    ):
        label = title = PAID_STATUS.get(status, "En attente de paiement")
        action = Action(
            status,
            permission=[],
            status_attr="paid_status",
            icon=STATUS_ICON[status],
            label=label,
            title=title,
            callback=callbacks.get(status, global_callback),
        )
        manager.add(action)
    return manager


PAID_STATUS_MANAGER = {
    "invoice": get_paid_status_manager(
        "invoice", callbacks={"__all__": invoice_paid_status_callback}
    ),
    "expense": get_paid_status_manager("expense"),
    "supplier_invoice": get_paid_status_manager(
        "supplier_invoice", callbacks={"__all__": supplier_invoice_paid_status_callback}
    ),
}


@implementer(IPaymentStateManager)
def get_default_payment_state_manager(doctype: str) -> ActionManager:
    """
    This function returns the default payment state manager for the given doctype.

    Returns:
        ActionManager: The default payment state manager for the given doctype.
    """
    return PAID_STATUS_MANAGER[doctype]


def set_status(
    request, node: Union[Invoice, ExpenseSheet, SupplierInvoice], status: str, **kw
) -> Union[Invoice, ExpenseSheet, SupplierInvoice]:
    manager: ActionManager = request.find_service(IPaymentStateManager, context=node)
    return manager.process(request, node, status, **kw)


def check_node_resulted(
    request, node: Union[Invoice, ExpenseSheet, SupplierInvoice], **kw
) -> Union[Invoice, ExpenseSheet, SupplierInvoice]:
    """Set the paid_status of the given node"""
    status = node.compute_paid_status(request, **kw)
    return set_status(request, node, status, **kw)
