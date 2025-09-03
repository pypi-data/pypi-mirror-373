import logging
import datetime
from sqla_inspect.excel import XlsExporter
from caerp.models.config import Config
from caerp.compute import math_utils

logger = logging.getLogger(__name__)

DOC_HEADERS = (
    {"name": "date", "label": "Date piece", "typ": "date"},
    {"name": "code_journal", "label": "Code journal"},
    {"name": "compte_cg", "label": "N° compte general"},
    {"name": "num_caerp", "label": "Numéro de pièce"},
    {"name": "libelle", "label": "Libelle ecriture"},
    {"name": "debit", "label": "Montant debit", "typ": "number"},
    {"name": "credit", "label": "Montant credit", "typ": "number"},
    {"name": "currency", "label": "Devise"},
    {"name": "num_analytique", "label": "code analytique"},
)

DOC_EXPENSE_HEADERS = (
    {"name": "date", "label": "Date piece", "typ": "date"},
    {"name": "code_journal", "label": "Code journal"},
    {"name": "compte_cg", "label": "N° compte general"},
    {"name": "num_feuille", "label": "Numéro de note de dépenses"},
    {"name": "libelle", "label": "Libelle ecriture"},
    {"name": "debit", "label": "Montant debit", "typ": "number"},
    {"name": "credit", "label": "Montant credit", "typ": "number"},
    {"name": "currency", "label": "Devise"},
    {"name": "num_analytique", "label": "code analytique"},
)

PAYMENT_HEADERS = (
    {"name": "date", "label": "Date piece", "typ": "date"},
    {"name": "code_journal", "label": "Code journal"},
    {"name": "compte_cg", "label": "N° compte general"},
    {"name": "reference", "label": "N° pièce"},
    {"name": "libelle", "label": "Libelle ecriture"},
    {"name": "debit", "label": "Montant debit", "typ": "number"},
    {"name": "credit", "label": "Montant credit", "typ": "number"},
    {"name": "currency", "label": "Devise"},
    {"name": "num_analytique", "label": "code analytique"},
)
# (
#     {"name": "reference", "label": "N° pièce"},
#     {"name": "code_journal", "label": "Code journal"},
#     {"name": "date", "label": "Date piece", "typ": "date"},
#     {"name": "compte_cg", "label": "N° compte general"},
#     {"name": "libelle", "label": "Libelle ecriture"},
#     {"name": "debit", "label": "Montant debit", "typ": "number"},
#     {"name": "credit", "label": "Montant credit", "typ": "number"},
#     {"name": "currency", "label": "Devise"},
#     {"name": "num_analytique", "label": "code analytique"},
#     {"name": "mode", "label": "Mode de règlement"},
# )


DATE_FORMAT = "%d/%m/%Y"


class BaseWriter(XlsExporter):
    encoding = "utf-8"
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    extension = "xlsx"
    amount_precision = 5

    def __init__(self, context, request):
        super().__init__()
        self.libelle_length = 0
        if request:
            self.libelle_length = Config.get_value(
                "accounting_label_maxlength",
                default=0,
                type_=int,
            )

        if self.libelle_length == 0:
            logger.warning(
                "No accounting label length defined, fallback : " "truncating disabled"
            )

    def format_libelle(self, libelle):
        """
        truncate the libelle in order to suit the accounting software specs
        """
        if self.libelle_length > 0:
            return libelle[: self.libelle_length]
        else:
            return libelle

    def format_debit(self, value):
        """
        Format the debit entry to get a clean float in our export
        12000 => 120,00
        """
        if value in ("", None):
            return 0
        else:
            if self.amount_precision > 2:
                value = math_utils.floor_to_precision(
                    value, precision=2, dialect_precision=self.amount_precision
                )
            return math_utils.integer_to_amount(value, precision=self.amount_precision)

    def format_credit(self, credit):
        """
        format the credit entry to get a clean float
        """
        return self.format_debit(credit)

    def format_currency(self, value):
        return "E"

    def format_compte_cg(self, value):
        if value:
            value = value[:6]
        return value

    def format_num_analytique(self, value):
        return f"axe1:{value}"

    def format_date(self, date_object):
        if isinstance(date_object, (datetime.date, datetime.datetime)):
            return date_object.strftime(DATE_FORMAT)
        else:
            return date_object


class InvoiceWriter(BaseWriter):
    """
    Invoice writer
    """

    headers = DOC_HEADERS


class SupplierInvoiceWriter(BaseWriter):
    """
    Supplier invoice writer
    """

    amount_precision = 2
    headers = DOC_HEADERS


class SupplierPaymentWriter(BaseWriter):
    """
    Supplier payment xlsx writer
    """

    amount_precision = 2
    headers = PAYMENT_HEADERS


class PaymentWriter(BaseWriter):
    """
    expense xlsx writer
    """

    headers = PAYMENT_HEADERS


class ExpenseWriter(BaseWriter):
    """
    expense xlsx writer
    """

    headers = DOC_EXPENSE_HEADERS
    amount_precision = 2


class ExpensePaymentWriter(BaseWriter):
    amount_precision = 2
    headers = PAYMENT_HEADERS
