import logging
from typing import List

from sqlalchemy import and_, func, or_, orm, select

from caerp.models.project.business import BusinessPaymentDeadline
from caerp.models.task import CancelInvoice, Estimation, Invoice, Task

logger = logging.getLogger(__name__)


def currently_invoicing(request, business):
    query = (
        select(func.count(Task.id))
        .where(Task.type_.in_(Task.invoice_types))
        .where(Task.business_id == business.id)
        .where(Task.status != "valid")
    )

    return request.dbsession.execute(query).scalar() != 0


def find_payment_deadline_by_id(request, business, deadline_id):
    """Return the payment deadline with the given id attached to the business"""
    return (
        request.dbsession.query(BusinessPaymentDeadline)
        .filter_by(business_id=business.id)
        .filter_by(id=deadline_id)
        .first()
    )


def get_deadlines_by_estimation(
    request, business
) -> List[List[BusinessPaymentDeadline]]:
    """
    Group a business' payment deadlines by estimation
    """
    result = {}
    query = (
        select(BusinessPaymentDeadline)
        .join(BusinessPaymentDeadline.estimation)
        .where(BusinessPaymentDeadline.business_id == business.id)
        .order_by(
            Estimation.date,
            BusinessPaymentDeadline.deposit.desc(),
            BusinessPaymentDeadline.order,
        )
    )
    for deadline in request.dbsession.execute(query).scalars():
        result.setdefault(deadline.estimation_id, []).append(deadline)
    return list(result.values())


def get_estimation_deadlines(request, estimation) -> List[BusinessPaymentDeadline]:
    query = (
        select(BusinessPaymentDeadline)
        .where(BusinessPaymentDeadline.estimation_id == estimation.id)
        .order_by(BusinessPaymentDeadline.deposit.desc(), BusinessPaymentDeadline.order)
    )
    return request.dbsession.execute(query).scalars().all()


def get_deposit_deadlines(
    request, business, estimation=None
) -> List[BusinessPaymentDeadline]:
    """Return the deposit payment deadline of a business"""
    query = select(BusinessPaymentDeadline).where(
        BusinessPaymentDeadline.business_id == business.id,
        BusinessPaymentDeadline.deposit.is_(True),
    )
    if estimation:
        query = query.where(BusinessPaymentDeadline.estimation_id == estimation.id)
    return request.dbsession.execute(query).scalars().all()


def get_estimation_intermediate_deadlines(
    request, estimation
) -> List[BusinessPaymentDeadline]:
    """Collect the intermediate payment deadlines of an estimation"""
    deadlines = get_estimation_deadlines(request, estimation)

    return [deadline for deadline in deadlines[:-1] if not deadline.deposit]


def get_estimation_sold_deadline(request, estimation) -> BusinessPaymentDeadline:
    query = (
        select(BusinessPaymentDeadline)
        .where(
            BusinessPaymentDeadline.estimation_id == estimation.id,
            BusinessPaymentDeadline.deposit.is_(False),
        )
        .order_by(BusinessPaymentDeadline.order.desc())
        .limit(1)
    )
    return request.dbsession.execute(query).scalar()


def get_sold_deadlines(request, business) -> List[BusinessPaymentDeadline]:
    """Collect the sold payment deadlines of a business"""
    return [a[-1] for a in get_deadlines_by_estimation(request, business) if len(a) > 0]


def _get_amount_to_invoice(request, business, estimation=None, mode="ht"):
    polymorphic_task = orm.with_polymorphic(Task, [Invoice, CancelInvoice])
    invoiced_query = select(func.sum(getattr(polymorphic_task, mode))).where(
        polymorphic_task.business_id == business.id,
        polymorphic_task.type_.in_(Task.invoice_types),
    )
    if estimation:
        # On restreint à un devis et aux factures qui le concerne
        estimated = getattr(estimation, mode)
        invoice_alias = orm.aliased(Invoice)
        invoiced_query = invoiced_query.outerjoin(
            invoice_alias, polymorphic_task.CancelInvoice.invoice_id == invoice_alias.id
        ).where(
            or_(
                polymorphic_task.Invoice.estimation_id == estimation.id,
                invoice_alias.estimation_id == estimation.id,
            )
        )
    else:
        estimated_query = (
            select(func.sum(getattr(Estimation, mode)))
            .where(Estimation.business_id == business.id)
            .where(Estimation.signed_status != "aborted")
        )
        estimated = request.dbsession.execute(estimated_query).scalar() or 0
    invoiced = request.dbsession.execute(invoiced_query).scalar() or 0

    return int(estimated - invoiced)


def get_amount_to_invoice_ht(request, business, estimation=None):
    """
    Compute the amount to invoice for this business
    if an estimation is provided, restrict to the given estimation
    """
    return _get_amount_to_invoice(request, business, estimation, mode="ht")


def get_amount_to_invoice_ttc(request, business, estimation=None):
    """
    Compute the amount to invoice for this business
    if an estimation is provided, restrict to the given estimation
    """
    return _get_amount_to_invoice(request, business, estimation, mode="ttc")


def _get_invoiced_amount(request, business, estimation=None, mode="ht"):
    polymorphic_task = orm.with_polymorphic(Task, [Invoice, CancelInvoice])
    invoiced_query = select(func.sum(getattr(polymorphic_task, mode))).where(
        Task.business_id == business.id,
        Task.type_.in_(Task.invoice_types),
    )
    if estimation:
        # On restreint à un devis et aux factures qui le concerne
        invoice_alias = orm.aliased(Invoice)
        invoiced_query = invoiced_query.outerjoin(
            invoice_alias, polymorphic_task.CancelInvoice.invoice_id == invoice_alias.id
        ).where(
            or_(
                polymorphic_task.Invoice.estimation_id == estimation.id,
                invoice_alias.estimation_id == estimation.id,
            )
        )
    return request.dbsession.execute(invoiced_query).scalar() or 0


def get_invoiced_amount_ht(request, business, estimation=None):
    return _get_invoiced_amount(request, business, estimation, mode="ht")


def get_invoiced_amount_ttc(request, business, estimation=None):
    return _get_invoiced_amount(request, business, estimation, mode="ttc")


def get_amount_foreseen_to_invoice_ht(request, business, estimation=None):
    query = (
        select(func.sum(BusinessPaymentDeadline.amount_ht))
        .where(BusinessPaymentDeadline.business_id == business.id)
        .where(BusinessPaymentDeadline.invoiced.is_(False))
    )
    if estimation:
        query = query.where(BusinessPaymentDeadline.estimation_id == estimation.id)
    return request.dbsession.execute(query).scalar() or 0


def get_amount_foreseen_to_invoice_ttc(request, business, estimation=None):
    query = (
        select(func.sum(BusinessPaymentDeadline.amount_ttc))
        .where(BusinessPaymentDeadline.business_id == business.id)
        .where(BusinessPaymentDeadline.invoiced.is_(False))
    )
    if estimation:
        query = query.where(BusinessPaymentDeadline.estimation_id == estimation.id)
    return request.dbsession.execute(query).scalar() or 0


def get_invoices_without_deadline(request, business):
    query = (
        select(Invoice)
        .where(Invoice.business_id == business.id)
        .where(
            Invoice.id.not_in(
                [d.invoice_id for d in business.payment_deadlines if d.invoice_id]
            )
        )
    )

    return request.dbsession.execute(query).scalars().all()


def guess_payment_deadline_from_invoice(request, business, invoice):
    """Try to guess the payment deadline from an invoice"""
    query = (
        select(BusinessPaymentDeadline)
        .where(BusinessPaymentDeadline.business_id == business.id)
        .where(BusinessPaymentDeadline.invoice_id.is_(None))
        .order_by(BusinessPaymentDeadline.order.asc())
    )
    for deadline in request.dbsession.execute(query).scalars():
        if deadline.amount_ttc == invoice.ttc:
            deadline.invoice_id = invoice.id
            if invoice.status == "valid":
                deadline.invoiced = True
            request.dbsession.merge(deadline)
            return deadline
    return None


def get_invoice_outside_payment_deadline(
    request, business, estimation=None, min_date=None, max_date=None
):
    """
    Collect Invoice objects not attached to a payment deadline
    """
    polymorphic_task = orm.with_polymorphic(Task, [Invoice, CancelInvoice])
    cinv_invoice = orm.aliased(Invoice)
    query = select(polymorphic_task)
    if estimation is not None:
        query = query.outerjoin(cinv_invoice, polymorphic_task.CancelInvoice.invoice)
    query = (
        query.filter(polymorphic_task.business_id == business.id)
        .filter(polymorphic_task.type_.in_(Task.invoice_types))
        .filter(
            polymorphic_task.id.notin_(
                select(BusinessPaymentDeadline.invoice_id).where(
                    BusinessPaymentDeadline.business_id == business.id,
                    BusinessPaymentDeadline.invoice_id.is_not(None),
                )
            ),
        )
        .order_by(polymorphic_task.date.asc())
    )
    if estimation:
        query = query.filter(
            or_(
                polymorphic_task.Invoice.estimation_id == estimation.id,
                cinv_invoice.estimation_id == estimation.id,
            )
        )
    if min_date:
        query = query.filter(Task.date > min_date)
    if max_date:
        query = query.filter(Task.date <= max_date)
    return request.dbsession.execute(query).scalars().all()


def get_invoices_outside_estimation(request, business):
    """
    Return invoices and cancelinvoices in the business that are not related
    to an estimation
    """
    polymorphic_task = orm.with_polymorphic(Task, [Invoice, CancelInvoice])
    cinv_invoice = orm.aliased(Invoice)

    query = select(polymorphic_task)
    query = query.outerjoin(cinv_invoice, polymorphic_task.CancelInvoice.invoice)
    query = (
        query.filter(polymorphic_task.business_id == business.id)
        .filter(polymorphic_task.type_.in_(Task.invoice_types))
        .filter(
            and_(
                polymorphic_task.Invoice.estimation_id.is_(None),
                cinv_invoice.estimation_id.is_(None),
            )
        )
        .order_by(polymorphic_task.date.asc())
    )
    return request.dbsession.execute(query).scalars().all()


def get_business_estimations(
    request,
    business,
    min_date=None,
    max_date=None,
    only_valid=False,
    include_aborted=True,
):
    query = (
        select(Estimation)
        .filter(Estimation.business_id == business.id)
        .filter(Estimation.type_.in_(Task.estimation_types))
        .order_by(Estimation.date.desc())
    )
    if min_date:
        query = query.filter(Estimation.date > min_date)
    if max_date:
        query = query.filter(Estimation.date <= max_date)
    if only_valid:
        query = query.filter(Estimation.status == "valid")
    if not include_aborted:
        query = query.filter(Estimation.signed_status != "aborted")
    return request.dbsession.execute(query).scalars().all()
