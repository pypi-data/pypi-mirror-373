import datetime
import logging
from typing import Optional, Union

from sqlalchemy import select

from caerp.controllers.payment import record_payment
from caerp.controllers.state_managers.payment import check_node_resulted
from caerp.models.sepa import (
    SupplierInvoiceSupplierSepaWaitingPayment,
    SupplierInvoiceUserSepaWaitingPayment,
)
from caerp.models.status import StatusLogEntry
from caerp.models.supply.payment import (
    SupplierInvoiceSupplierPayment,
    SupplierInvoiceUserPayment,
)
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.utils import strings

logger = logging.getLogger(__name__)


def record_supplier_invoice_payment_for_user(
    request,
    supplier_invoice: SupplierInvoice,
    date: datetime.date,
    amount: int,
    mode: str,
    bank_id: int,
    waiver: Optional[bool] = False,
    resulted: Optional[bool] = False,
    bank_remittance_id: Optional[str] = "",
) -> SupplierInvoiceUserPayment:
    payment = get_user_payment(
        request,
        date,
        amount,
        mode,
        bank_id,
        waiver=waiver,
        bank_remittance_id=bank_remittance_id,
    )
    _record_supplier_invoice_payment(
        request, supplier_invoice, payment, resulted=resulted
    )
    return payment


def record_supplier_invoice_payment_for_supplier(
    request,
    supplier_invoice: SupplierInvoice,
    date: datetime.date,
    amount: int,
    mode: str,
    bank_id: int,
    resulted: Optional[bool] = False,
    bank_remittance_id: Optional[str] = "",
) -> SupplierInvoiceSupplierPayment:
    payment = get_supplier_payment(
        request,
        date,
        amount,
        mode,
        bank_id,
        bank_remittance_id=bank_remittance_id,
    )
    _record_supplier_invoice_payment(
        request, supplier_invoice, payment, resulted=resulted
    )
    request.dbsession.merge(supplier_invoice)
    return payment


def _record_supplier_invoice_payment(
    request,
    supplier_invoice: SupplierInvoice,
    payment: Union[SupplierInvoiceSupplierPayment, SupplierInvoiceUserPayment],
    resulted: Optional[bool] = False,
):
    record_payment(request, supplier_invoice, payment)
    check_node_resulted(request, supplier_invoice, force_resulted=resulted)

    status_record = StatusLogEntry(
        status=supplier_invoice.paid_status,
        user_id=request.identity.id,
        comment="",
        state_manager_key="paid_status",
    )
    supplier_invoice.statuses.append(status_record)
    request.dbsession.merge(supplier_invoice)


def get_supplier_payment(
    request,
    date: datetime.date,
    amount: int,
    mode: str,
    bank_id: int,
    bank_remittance_id: Optional[str] = "",
) -> SupplierInvoiceSupplierPayment:
    return SupplierInvoiceSupplierPayment(
        user_id=request.identity.id,
        date=date,
        amount=amount,
        mode=mode,
        bank_id=bank_id,
        bank_remittance_id=bank_remittance_id,
    )


def get_user_payment(
    request,
    date: datetime.date,
    amount: int,
    mode: str,
    bank_id: int,
    waiver: Optional[bool] = False,
    bank_remittance_id: Optional[str] = "",
) -> SupplierInvoiceUserPayment:
    return SupplierInvoiceUserPayment(
        user_id=request.identity.id,
        date=date,
        amount=amount,
        mode=mode,
        bank_id=bank_id,
        bank_remittance_id=bank_remittance_id,
        waiver=waiver,
    )


def delete_supplier_invoice_payment(
    request, supplier_invoice: SupplierInvoice, payment: SupplierInvoiceSupplierPayment
):
    """
    Delete the given payment from the supplier invoice
    """
    logger.info(
        f"Deleting payment {payment.id} for {supplier_invoice.type_} {supplier_invoice.id}"
    )
    supplier_invoice.payments.remove(payment)
    request.dbsession.delete(payment)
    request.dbsession.flush()

    check_node_resulted(request, supplier_invoice)
    request.dbsession.merge(supplier_invoice)


def create_sepa_waiting_payment_for_supplier(
    request, supplier_invoice: SupplierInvoice, amount
):
    waiting_amount = supplier_invoice.cae_amount_waiting_for_payment()
    assert (
        amount <= waiting_amount and amount > 0
    ), f"Le montant du paiement doit être compris entre 0 et le montant {waiting_amount}."
    assert (
        not supplier_invoice.internal
    ), "Cette fonctionnalité n'est pas disponible pour les factures internes"
    waiting_payment = SupplierInvoiceSupplierSepaWaitingPayment(
        supplier_invoice=supplier_invoice, amount=amount
    )
    request.dbsession.add(waiting_payment)
    request.dbsession.flush()
    topay = strings.format_amount(
        waiting_payment.amount, precision=2, html=False, currency=True
    )
    if amount == supplier_invoice.total:

        label = f"À payer en totalité : {topay}"
    else:
        label = f"À payer : {topay}"
    if supplier_invoice.cae_percentage != 100:
        label = f"Part fournisseur {label.lower()}"

    log_entry = StatusLogEntry(
        node=supplier_invoice,
        state_manager_key="wait_for_payment_supplier",
        visibility="management",
        status="valid",
        label=label,
        comment="",
        user=request.identity,
    )
    request.dbsession.add(log_entry)
    request.dbsession.flush()
    return waiting_payment


def create_sepa_waiting_payment_for_user(
    request, supplier_invoice: SupplierInvoice, amount
):
    waiting_amount = supplier_invoice.worker_amount_waiting_for_payment()
    assert (
        amount <= waiting_amount and amount > 0
    ), f"Le montant du paiement doit être compris entre 0 et le montant {waiting_amount}."
    assert (
        not supplier_invoice.internal
    ), "Cette fonctionnalité n'est pas disponible pour les factures internes"
    waiting_payment = SupplierInvoiceUserSepaWaitingPayment(
        supplier_invoice=supplier_invoice, amount=amount
    )
    request.dbsession.add(waiting_payment)
    request.dbsession.flush()
    topay = strings.format_amount(
        waiting_payment.amount, precision=2, html=False, currency=True
    )
    if amount == supplier_invoice.total:

        label = f"À payer en totalité : {topay}"
    else:
        label = f"À payer : {topay}"
    if supplier_invoice.cae_percentage != 100:
        label = f"Part entrepreneur {label.lower()}"

    log_entry = StatusLogEntry(
        node=supplier_invoice,
        state_manager_key="wait_for_payment_user",
        visibility="management",
        status="valid",
        label=label,
        comment="",
        user=request.identity,
    )
    request.dbsession.add(log_entry)
    request.dbsession.flush()
    return waiting_payment


def delete_supplier_invoice_sepa_waiting_payment(
    request,
    waiting_payment: Union[
        SupplierInvoiceSupplierSepaWaitingPayment, SupplierInvoiceUserSepaWaitingPayment
    ],
) -> SupplierInvoice:
    """
    Delete the given waiting payment
    """
    assert not waiting_payment.payment, "Un décaissement est déjà enregistré"
    supplier_invoice = waiting_payment.supplier_invoice

    if isinstance(waiting_payment, SupplierInvoiceSupplierSepaWaitingPayment):
        type_ = "supplier"
    else:
        type_ = "user"
    log_entry = request.dbsession.execute(
        select(StatusLogEntry)
        .where(
            StatusLogEntry.state_manager_key == f"wait_for_payment_{type_}",
            StatusLogEntry.node_id == waiting_payment.node_id,
        )
        .order_by(StatusLogEntry.id.desc())
    ).scalar()
    if log_entry is not None:
        supplier_invoice.statuses.remove(log_entry)
        request.dbsession.delete(log_entry)
    if type_ == "supplier":
        supplier_invoice.supplier_sepa_waiting_payments.remove(waiting_payment)
    else:
        supplier_invoice.user_sepa_waiting_payments.remove(waiting_payment)
    request.dbsession.delete(waiting_payment)
    request.dbsession.flush()
    return supplier_invoice


def cancel_sepa_waiting_payment(
    request,
    waiting_payment: Union[
        SupplierInvoiceSupplierSepaWaitingPayment, SupplierInvoiceUserSepaWaitingPayment
    ],
) -> SupplierInvoice:
    """
    Cancel the given waiting payment (in case the bank refused the payment)

    In this situation, a payment has already been added
    """
    assert (
        waiting_payment.paid_status
        == SupplierInvoiceSupplierSepaWaitingPayment.PAID_STATUS
    )

    supplier_invoice = waiting_payment.supplier_invoice
    # The payment we delete
    supplier_invoice_payment = waiting_payment.payment
    if supplier_invoice_payment:
        delete_supplier_invoice_payment(
            request, supplier_invoice, supplier_invoice_payment
        )
        # Pour être sûr que le paiement n'est plus associé
        # il n'est nettoyé qu'apèrs le transaction.commit()
        waiting_payment.payment = None

    waiting_payment.paid_status = waiting_payment.CANCELLED_STATUS
    request.dbsession.merge(waiting_payment)
    request.dbsession.flush()
    cancelled = strings.format_amount(
        waiting_payment.amount, precision=2, html=False, currency=True
    )
    log_entry = StatusLogEntry(
        node=supplier_invoice,
        state_manager_key="wait_for_payment",
        visibility="management",
        status="valid",
        label=f"Paiement annulé : {cancelled}",
        comment="",
        user=request.identity,
    )
    request.dbsession.add(log_entry)
    request.dbsession.flush()

    return supplier_invoice
