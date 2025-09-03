from caerp.models.task.invoice import Invoice


def is_invoice_canceled(request, invoice: Invoice) -> bool:
    """
    Check if an invoice has been canceled with a CancelInvoice
    """
    if invoice.paid_status != "resulted":
        return False

    if len(invoice.payments) == 0:
        return True

    if sum([payment.amount for payment in invoice.payments]) == 0:
        return True
    return False
