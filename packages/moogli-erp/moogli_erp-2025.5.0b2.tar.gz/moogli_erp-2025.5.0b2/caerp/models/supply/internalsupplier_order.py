from sqlalchemy import (
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .supplier_order import (
    SupplierOrder,
    SupplierOrderLine,
)


class InternalSupplierOrder(SupplierOrder):
    __tablename__ = "internalsupplier_order"
    __mapper_args__ = {"polymorphic_identity": "internalsupplier_order"}
    internal = True

    id = Column(
        ForeignKey("supplier_order.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    # relationship
    source_estimation = relationship(
        "InternalEstimation", uselist=False, back_populates="supplier_order"
    )

    @classmethod
    def from_estimation(cls, estimation, supplier):
        """
        Create an instance based on the given estimation
        """
        instance = cls(
            name="Devis {}".format(estimation.internal_number),
            cae_percentage=100,
        )
        instance.supplier = supplier
        instance.company = estimation.customer.source_company

        instance.lines.append(SupplierOrderLine.from_task(estimation))
        return instance
