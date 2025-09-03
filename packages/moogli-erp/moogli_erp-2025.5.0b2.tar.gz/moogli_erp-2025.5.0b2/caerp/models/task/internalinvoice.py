import logging

from sqlalchemy import (
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from caerp.models.task.services.invoice import InternalCancelInvoiceProcessService

from .invoice import CancelInvoice, Invoice

from .services import (
    InternalInvoiceService,
    InternalInvoiceProcessService,
)


logger = logging.getLogger(__name__)


class InternalInvoice(Invoice):
    __tablename__ = "internalinvoice"
    __mapper_args__ = {
        "polymorphic_identity": "internalinvoice",
    }
    invoice_computer = None
    internal = True
    # Préfixe utilisé pour différencier les clés de configuration
    prefix = "internal"
    _caerp_service = InternalInvoiceService
    _internal_process_service = InternalInvoiceProcessService

    id = Column(
        ForeignKey("invoice.id", ondelete="CASCADE"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    supplier_invoice_id = Column(
        ForeignKey("internalsupplier_invoice.id", ondelete="SET NULL"),
    )

    # Relationships
    supplier_invoice = relationship(
        "InternalSupplierInvoice", back_populates="source_invoice"
    )

    # Template pour les noms des documents
    _number_tmpl = "{s.company.name} {s.date:%Y-%m} FI{s.company_index}"
    _deposit_name_tmpl = "Facture d'acompte {0}"
    _sold_name_tmpl = "Facture de solde {0}"

    def sync_with_customer(self, request):
        return self._internal_process_service.sync_with_customer(self, request)


class InternalCancelInvoice(CancelInvoice):
    __tablename__ = "internalcancelinvoice"
    __mapper_args__ = {
        "polymorphic_identity": "internalcancelinvoice",
    }
    internal = True
    # Préfixe utilisé pour différencier les clés de configuration
    prefix = "internal"
    _caerp_service = InternalInvoiceService
    _internal_process_service = InternalCancelInvoiceProcessService

    id = Column(
        ForeignKey("cancelinvoice.id", ondelete="CASCADE"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    supplier_invoice_id = Column(
        ForeignKey("internalsupplier_invoice.id", ondelete="SET NULL"),
    )

    # Relationships
    supplier_invoice = relationship(
        "InternalSupplierInvoice", back_populates="source_cancelinvoice"
    )

    # Template pour les noms des documents
    _number_tmpl = "{s.company.name} {s.date:%Y-%m} AI{s.company_index}"

    def sync_with_customer(self, request):
        return self._internal_process_service.sync_with_customer(self, request)
