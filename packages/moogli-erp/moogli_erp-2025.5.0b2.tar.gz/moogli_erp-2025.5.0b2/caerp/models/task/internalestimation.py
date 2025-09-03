import logging

from sqlalchemy import (
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .estimation import Estimation

from .services import (
    InternalEstimationProcessService,
)


logger = logging.getLogger(__name__)


class InternalEstimation(Estimation):
    __tablename__ = "internalestimation"
    __mapper_args__ = {
        "polymorphic_identity": "internalestimation",
    }
    internal = True
    # Préfixe utilisé pour différencier les clés de configuration
    prefix = "internal"

    _internal_process_service = InternalEstimationProcessService

    # Columns
    id = Column(
        ForeignKey("estimation.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    supplier_order_id = Column(
        ForeignKey("internalsupplier_order.id", ondelete="SET NULL"),
    )

    # Relationships
    supplier_order = relationship(
        "InternalSupplierOrder", back_populates="source_estimation"
    )

    # Template pour les noms des documents
    _number_tmpl = "{s.company.name} {s.date:%Y-%m} FI{s.company_index}"
    _deposit_name_tmpl = "Facture d'acompte {0}"
    _sold_name_tmpl = "Facture de solde {0}"

    def sync_with_customer(self, request):
        return self._internal_process_service.sync_with_customer(self, request)
