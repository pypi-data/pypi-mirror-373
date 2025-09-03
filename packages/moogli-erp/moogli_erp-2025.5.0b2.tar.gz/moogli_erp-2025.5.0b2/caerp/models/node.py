"""
    Nodes model is a base model for many other models (projects, documents,
    files, events)
    This way we can easily use the parent/children relationship on an agnostic
    way as in a CMS
"""
from caerp.consts.permissions import PERMISSIONS
from caerp.utils.compat import Iterable

import colander
from pyramid.request import Request
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from caerp_base.models.mixins import (
    PersistentACLMixin,
    TimeStampedMixin,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)

from caerp.models.status import (
    status_history_relationship,
    StatusLogEntry,
)


class Node(PersistentACLMixin, TimeStampedMixin, DBBASE):
    """
    A base node providing a parent<->children structure for most of the models
    (usefull for file attachment)
    """

    __tablename__ = "node"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "nodes",
    }

    id = Column(
        Integer,
        primary_key=True,
    )
    name = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Nom",
                "missing": colander.required,
            },
        },
        nullable=True,
    )
    parent_id = Column(
        ForeignKey("node.id"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    smtp_history = relationship(
        "NodeSmtpHistory",
        primaryjoin="Node.id==NodeSmtpHistory.node_id",
        back_populates="node",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    children = relationship(
        "Node",
        primaryjoin="Node.id==Node.parent_id",
        cascade="all",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        back_populates="parent",
    )
    parent = relationship(
        "Node",
        primaryjoin="Node.id==Node.parent_id",
        remote_side=[id],
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        uselist=False,
        back_populates="children",
    )
    files = relationship(
        "File",
        primaryjoin="Node.id==File.parent_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        viewonly=True,
    )
    # All linked StatusLogEntry, regardless of their nature or permission
    statuses = status_history_relationship()

    type_ = Column(
        "type_",
        String(50),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )
    file_requirements = relationship(
        "SaleFileRequirement",
        back_populates="node",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )

    NODE_LABELS = {
        "estimation": "Devis",
        "internalestimation": "Devis interne",
        "invoice": "Facture",
        "internalinvoice": "Facture interne",
        "internalcancelinvoice": "Avoir interne",
        "cancelinvoice": "Avoir",
        "business": "Affaire",
        "project": "Dossier",
        "expensesheet": "Note de dépenses",
        "workshop": "Atelier",
        "activity": "Rendez-vous",
        "third_party": "Tiers",
        "supplier_order": "Commande fournisseur",
        "internalsupplier_order": "Commande fournisseur interne",
        "supplier_invoice": "Facture fournisseur",
        "internalsupplier_invoice": "Facture fournisseur interne",
        "sap_attestation": "Attestation fiscale SAP",
    }

    @property
    def type_label(self):
        return self.NODE_LABELS.get(self.type_, self.type_)

    def extra_statuses(self) -> Iterable[StatusLogEntry]:
        """
        Can be overriden to provide additionan StatusLogEtnries
        """
        return []

    def get_allowed_statuses(
        self, request: Request, permission=PERMISSIONS["context.view_statuslogentry"]
    ):
        return [
            status
            for status in self.statuses + list(self.extra_statuses())
            if request.has_permission(permission, status)
        ]
