"""
Utilitaires pour la création et l'exécution d'ordre de virement sepa


Peut-être utilisé dans pshell avec le code suivant :

.. code-block:: python

    from pyramid.security import remember
    from caerp.controllers.sepa import (
        create_sepa_credit_transfer,
        generate_sepa_credit_transfer_xml_file,
        add_expense_sheet_to_sepa_credit_transfer,
        add_supplier_invoice_to_sepa_credit_transfer,
    )
    from caerp.models.payments import BankAccount
    from caerp.models.expense.sheet import ExpenseSheet
    from caerp.models.supply.supplier_invoice import SupplierInvoice

    remember(request, "monlogin")
    expense_sheet = ExpenseSheet.query.first()
    supplier_invoice = SupplierInvoice.query.first()
    bank_account = BankAccount.query().filter(BankAccount.default == True).first()
    order = create_sepa_credit_transfer(request, bank_account.id)
    add_expense_sheet_to_sepa_credit_transfer(request, order, expense_sheet)
    add_supplier_invoice_to_sepa_credit_transfer(request, order, supplier_invoice)
    xml_file = generate_sepa_credit_transfer_xml_file(request, order)
    print(xml_file.getvalue())
"""
import datetime
import io
import logging
from typing import Optional, Union

from caerp.controllers.expense.payment import (
    cancel_sepa_waiting_payment as cancel_expense_sepa_payment,
)
from caerp.controllers.expense.payment import record_expense_payment
from caerp.controllers.supplier_invoice.payment import (
    cancel_sepa_waiting_payment as cancel_supplier_invoice_sepa_payment,
)
from caerp.controllers.supplier_invoice.payment import (
    record_supplier_invoice_payment_for_supplier,
    record_supplier_invoice_payment_for_user,
)
from caerp.models.expense.payment import ExpensePayment
from caerp.models.files import File
from caerp.models.sepa import (
    ExpenseSepaWaitingPayment,
    SepaCreditTransfer,
    SupplierInvoiceSupplierSepaWaitingPayment,
    SupplierInvoiceUserSepaWaitingPayment,
)
from caerp.models.supply.payment import (
    SupplierInvoiceSupplierPayment,
    SupplierInvoiceUserPayment,
)
from caerp.services.sepa import get_cae_debtor, waiting_payment_to_abstract_payment
from caerp.utils.sepa.credit_transfer import SepaCreditTransferXmlFactory

logger = logging.getLogger(__name__)


def create_sepa_credit_transfer(
    request,
    bank_account_id: Optional[int] = None,
    execution_date: Optional[datetime.date] = None,
) -> SepaCreditTransfer:
    """
    Crée un ordre de virement SEPA pour un compte bancaire

    :param request: la requête Pyramid
    :param bank_account_id: l'identifiant du compte bancaire
    :param execution_date: date d'exécution du virement
    :return: l'ordre de virement créé
    """
    if execution_date is None:
        execution_date = datetime.date.today()
    sepa_credit_transfer = SepaCreditTransfer(
        bank_account_id=bank_account_id,
        execution_date=execution_date,
        user_id=request.identity.id,
    )

    request.dbsession.add(sepa_credit_transfer)
    request.dbsession.flush()
    return sepa_credit_transfer


def add_waiting_payment_to_sepa_credit_transfer(
    request,
    sepa_credit_transfer: SepaCreditTransfer,
    waiting_payment: Union[
        ExpenseSepaWaitingPayment, SupplierInvoiceSupplierSepaWaitingPayment
    ],
) -> SepaCreditTransfer:
    """
    Attache un paiement en attente à un ordre de virement SEPA

    :param request: la requête Pyramid
    :param sepa_credit_transfer: l'ordre de virement SEPA
    :param expense_sheet: La note de dépense
    """
    sepa_credit_transfer.sepa_waiting_payments.append(waiting_payment)
    request.dbsession.merge(sepa_credit_transfer)
    request.dbsession.flush()
    return sepa_credit_transfer


def remove_waiting_payment_from_sepa_credit_transfer(
    request,
    sepa_credit_transfer: SepaCreditTransfer,
    waiting_payment: Union[
        ExpenseSepaWaitingPayment, SupplierInvoiceSupplierSepaWaitingPayment
    ],
):
    """
    Retire un paiement en attente d'un ordre de virement SEPA

    :param request: la requête Pyramid
    :param sepa_credit_transfer: l'ordre de virement SEPA
    :param waiting_payment: Le paiement en attente
    """
    sepa_credit_transfer.sepa_waiting_payments.remove(waiting_payment)
    request.dbsession.merge(sepa_credit_transfer)
    request.dbsession.flush()
    return sepa_credit_transfer


def generate_expense_payment(
    request,
    sepa_credit_transfer: SepaCreditTransfer,
    waiting_payment: ExpenseSepaWaitingPayment,
) -> ExpensePayment:
    """
    Génère le décaissement d'une note de dépense depuis un paiement en attente
    """
    sheet = waiting_payment.expense_sheet
    date = sepa_credit_transfer.execution_date
    amount = waiting_payment.amount
    mode = "Virement SEPA"
    bank_id = sepa_credit_transfer.bank_account_id
    return record_expense_payment(
        request, sheet, date=date, amount=amount, mode=mode, bank_id=bank_id
    )


def generate_supplier_invoice_supplier_payment(
    request,
    sepa_credit_transfer: SepaCreditTransfer,
    waiting_payment: SupplierInvoiceSupplierSepaWaitingPayment,
) -> SupplierInvoiceSupplierPayment:
    """
    Génère le décaissement d'une facture fournisseur depuis un paiement en attente
    """
    invoice = waiting_payment.supplier_invoice
    date = sepa_credit_transfer.execution_date
    amount = waiting_payment.amount
    mode = "Virement SEPA"
    bank_id = sepa_credit_transfer.bank_account_id
    return record_supplier_invoice_payment_for_supplier(
        request, invoice, date=date, amount=amount, mode=mode, bank_id=bank_id
    )


def generate_supplier_invoice_user_payment(
    request,
    sepa_credit_transfer: SepaCreditTransfer,
    waiting_payment: SupplierInvoiceUserSepaWaitingPayment,
) -> SupplierInvoiceUserPayment:
    invoice = waiting_payment.supplier_invoice
    date = sepa_credit_transfer.execution_date
    amount = waiting_payment.amount
    mode = "Virement SEPA"
    bank_id = sepa_credit_transfer.bank_account_id
    return record_supplier_invoice_payment_for_user(
        request, invoice, date=date, amount=amount, mode=mode, bank_id=bank_id
    )


def generate_payment(
    request,
    sepa_credit_transfer: SepaCreditTransfer,
    waiting_payment: Union[
        ExpenseSepaWaitingPayment, SupplierInvoiceSupplierSepaWaitingPayment
    ],
) -> Union[ExpensePayment, SupplierInvoiceSupplierPayment, SupplierInvoiceUserPayment]:
    """
    Génère un décaissement depuis un paiement en attente
    """
    if isinstance(waiting_payment, ExpenseSepaWaitingPayment):
        payment = generate_expense_payment(
            request, sepa_credit_transfer, waiting_payment
        )
    elif isinstance(waiting_payment, SupplierInvoiceSupplierSepaWaitingPayment):
        payment = generate_supplier_invoice_supplier_payment(
            request, sepa_credit_transfer, waiting_payment
        )
    elif isinstance(waiting_payment, SupplierInvoiceUserSepaWaitingPayment):
        payment = generate_supplier_invoice_user_payment(
            request, sepa_credit_transfer, waiting_payment
        )
    else:
        raise ValueError(f"Unsupported waiting payment type: {type(waiting_payment)}")

    waiting_payment.payment = payment
    request.dbsession.merge(waiting_payment)
    request.dbsession.flush()
    return payment


def generate_sepa_credit_transfer_xml_file(
    request, sepa_credit_transfer: SepaCreditTransfer
) -> File:
    """
    Génère un fichier XML pour un ordre de virement SEPA
    - Génère les décaissements
    - Vérifie le statut "payé" de chaque documents (NDD, facture fournisseur...)

    :raises MissingConfigError: si le nom de la CAE, l'adresse de la CAE ou l'IBAN
    du compte bancaire n'ont pas été configurés

    :param request: la requête Pyramid
    :param sepa_credit_transfer: l'ordre de virement SEPA
    :return: le contenu du fichier XML
    """
    # On crée un objet abstrait débiteur
    debtor = get_cae_debtor(request, sepa_credit_transfer.bank_account)
    # On initialise la factory pour générer le XML
    xml_factory = SepaCreditTransferXmlFactory(
        debtor,
        sepa_credit_transfer.execution_date,
        pain_version=sepa_credit_transfer.sepa_pain_version,
    )
    # On stocke la référence dans l'ordre de virement SEPA
    sepa_credit_transfer.reference = xml_factory.get_msg_id()

    # On ajoute les paiements au xml et on génère les décaissements
    for waiting_payment in sepa_credit_transfer.sepa_waiting_payments:
        abstract_payment_order = waiting_payment_to_abstract_payment(
            request, waiting_payment
        )
        xml_factory.add_payment(abstract_payment_order)
        generate_payment(request, sepa_credit_transfer, waiting_payment)
        waiting_payment.paid_status = waiting_payment.PAID_STATUS

    # On génère le XML sous forme de string
    xml_data: bytes = xml_factory.generate_xml()
    # On crée un objet File avec le contenu du XML et on l'enregistre
    # dans la base de données
    sepa_credit_transfer.file = File(
        description=f"Fichier XML pour l'ordre de virement SEPA "
        f"{sepa_credit_transfer.id}",
        mimetype="application/xml",
        size=len(xml_data),
        is_signed=False,
        name=f"{sepa_credit_transfer.reference}.xml",
    )
    sepa_credit_transfer.file.data = io.BytesIO(xml_data)
    sepa_credit_transfer.status = SepaCreditTransfer.CLOSED_STATUS
    request.dbsession.merge(sepa_credit_transfer)
    request.dbsession.flush()
    return sepa_credit_transfer.file


def cancel_sepa_waiting_payment(
    request,
    waiting_payment: Union[
        ExpenseSepaWaitingPayment,
        SupplierInvoiceSupplierSepaWaitingPayment,
        SupplierInvoiceUserSepaWaitingPayment,
    ],
):
    if isinstance(waiting_payment, ExpenseSepaWaitingPayment):
        return cancel_expense_sepa_payment(request, waiting_payment)
    else:
        return cancel_supplier_invoice_sepa_payment(request, waiting_payment)


def cancel_sepa_credit_transfer(request, sepa_credit_transfer: SepaCreditTransfer):
    """
    Annule l'ordre de virement SEPA

    :param request: la requête Pyramid
    :param sepa_credit_transfer: l'ordre de virement SEPA
    """
    logger.debug(
        f"Cancel SEPA credit transfer {sepa_credit_transfer.id} "
        f"{sepa_credit_transfer.reference}"
    )
    sepa_credit_transfer.status = SepaCreditTransfer.CANCELLED_STATUS

    for waiting_payment in sepa_credit_transfer.sepa_waiting_payments:
        if waiting_payment.paid_status == waiting_payment.PAID_STATUS:
            cancel_sepa_waiting_payment(request, waiting_payment)

    request.dbsession.merge(sepa_credit_transfer)
    request.dbsession.flush()
    return sepa_credit_transfer
