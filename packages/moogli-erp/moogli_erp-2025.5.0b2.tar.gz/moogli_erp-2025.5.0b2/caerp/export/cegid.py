import logging
import datetime
from typing import List
from caerp.compute import math_utils
from sqla_inspect.excel import XlsExporter
from caerp.models.config import Config

logger = logging.getLogger(__name__)

DOC_HEADERS = (
    {"name": "type_", "label": "Type"},
    {"name": "date", "label": "DATE", "typ": "date"},
    {"name": "code_journal", "label": "JOURNAL"},
    {"name": "compte_cg", "label": "GENERAL"},
    {"name": "compte_tiers", "label": "AUXILIAIRE"},
    {"name": "sens", "label": "SENS"},
    {"name": "credit_debit", "label": "MONTANT", "typ": "number"},
    {"name": "libelle", "label": "LIBELLE"},
    {"name": "num_caerp", "label": "REFERENCE"},
    {"name": "num_analytique", "label": "SECTION/AXE A1"},
    {"name": "void", "label": "SECTION/AXE A2"},
    {"name": "void", "label": "SECTION/AXE A3"},
    {"name": "void", "label": "SECTION/AXE A4"},
    {"name": "void", "label": "SECTION/AXE A5"},
)

DOC_EXPENSE_HEADERS = (
    {"name": "type_", "label": "Type"},
    {"name": "date", "label": "DATE", "typ": "date"},
    {"name": "code_journal", "label": "JOURNAL"},
    {"name": "compte_cg", "label": "GENERAL"},
    {"name": "compte_tiers", "label": "AUXILIAIRE"},
    {"name": "sens", "label": "SENS"},
    {"name": "credit_debit", "label": "MONTANT", "typ": "number"},
    {"name": "libelle", "label": "LIBELLE"},
    {"name": "reference", "label": "REFERENCE"},
    {"name": "num_analytique", "label": "SECTION/AXE A1"},
    {"name": "void", "label": "SECTION/AXE A2"},
    {"name": "void", "label": "SECTION/AXE A3"},
    {"name": "void", "label": "SECTION/AXE A4"},
    {"name": "void", "label": "SECTION/AXE A5"},
)

PAYMENT_HEADERS = (
    {"name": "type_", "label": "Type"},
    {"name": "date", "label": "DATE", "typ": "date"},
    {"name": "code_journal", "label": "JOURNAL"},
    {"name": "compte_cg", "label": "GENERAL"},
    {"name": "compte_tiers", "label": "AUXILIAIRE"},
    {"name": "sens", "label": "SENS"},
    {"name": "credit_debit", "label": "MONTANT", "typ": "number"},
    {"name": "libelle", "label": "LIBELLE"},
    {"name": "reference", "label": "REFERENCE"},
    {"name": "num_analytique", "label": "SECTION/AXE A1"},
    {"name": "void", "label": "SECTION/AXE A2"},
    {"name": "void", "label": "SECTION/AXE A3"},
    {"name": "void", "label": "SECTION/AXE A4"},
    {"name": "void", "label": "SECTION/AXE A5"},
)
SUPPLIER_PAYMENT_HEADERS = (
    {"name": "type_", "label": "Type"},
    {"name": "date", "label": "DATE", "typ": "date"},
    {"name": "code_journal", "label": "JOURNAL"},
    {"name": "compte_cg", "label": "GENERAL"},
    {"name": "compte_tiers", "label": "AUXILIAIRE"},
    {"name": "sens", "label": "SENS"},
    {"name": "credit_debit", "label": "MONTANT", "typ": "number"},
    {"name": "libelle", "label": "LIBELLE"},
    {"name": "num_caerp", "label": "REFERENCE"},
    {"name": "num_analytique", "label": "SECTION/AXE A1"},
    {"name": "void", "label": "SECTION/AXE A2"},
    {"name": "void", "label": "SECTION/AXE A3"},
    {"name": "void", "label": "SECTION/AXE A4"},
    {"name": "void", "label": "SECTION/AXE A5"},
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

    def format_type_(self, value):
        if value == "A":
            return "A1"
        else:
            return "G"

    def format_libelle(self, libelle):
        """
        truncate the libelle in order to suit the accounting software specs
        """
        if self.libelle_length is not None and self.libelle_length > 0:
            return libelle[: self.libelle_length]
        else:
            return libelle

    def format_credit_debit(self, value):
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

    def format_compte_cg(self, value):
        if value:
            value = value[:6]
        return value

    def format_row(self, row) -> List:
        if row.get("debit", 0) and not row.get("credit", 0):
            row["sens"] = "D"
            row["credit_debit"] = row["debit"]
        elif row.get("credit", 0) and not row.get("debit", 0):
            row["sens"] = "C"
            row["credit_debit"] = row["credit"]
        else:  # Credit or debit is 0
            if "debit" in row:
                row["sens"] = "D"
                row["credit_debit"] = row["debit"]
            else:
                row["sens"] = "C"
                row["credit_debit"] = row["credit"]
        result = super().format_row(row)
        return result

    def format_date(self, date_object):
        if isinstance(date_object, (datetime.date, datetime.datetime)):
            return date_object.strftime("%d%m%Y")
        else:
            return date_object


class InvoiceWriter(BaseWriter):
    """
    Invoice writer
    """

    headers = DOC_HEADERS


class PaymentWriter(BaseWriter):
    """
    expense xlsx writer
    """

    headers = PAYMENT_HEADERS


class ExpenseWriter(BaseWriter):
    """
    expense xlsx writer
    """

    headers = DOC_HEADERS
    amount_precision = 2


class ExpensePaymentWriter(BaseWriter):
    amount_precision = 2
    headers = PAYMENT_HEADERS


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
    headers = SUPPLIER_PAYMENT_HEADERS
