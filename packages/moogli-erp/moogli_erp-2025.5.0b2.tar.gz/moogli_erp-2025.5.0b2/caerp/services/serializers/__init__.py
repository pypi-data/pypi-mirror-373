from caerp.services.serializers.company import CompanySerializer
from caerp.services.serializers.expense_sheet import ExpenseSheetSerializer
from caerp.services.serializers.sepa import (
    SepaCreditTransferSerializer,
    SepaWaitingSerializer,
)
from caerp.services.serializers.supplier import SupplierSerializer
from caerp.services.serializers.supplier_invoice import SupplierInvoiceSerializer
from caerp.services.serializers.user import UserSerializer

serializers = {
    "sepa_credit_transfer": SepaCreditTransferSerializer,
    "user": UserSerializer,
    "payer": UserSerializer,
    "supplier": SupplierSerializer,
    "sepa_waiting_payment": SepaWaitingSerializer,
    "expense_sheet": ExpenseSheetSerializer,
    "supplier_invoice": SupplierInvoiceSerializer,
    "company": CompanySerializer,
}
