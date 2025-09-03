"""2025.5.0 float dans les ecritures et supplier non supprimable

Create Date: 2025-07-07 18:15:03.994985

"""
from sqlalchemy import text, bindparam

# revision identifiers, used by Alembic.

# Revision ID:
revision = "8b17a86cbb9b"

# Revises (previous revision or revisions):
down_revision = "f4e8e8beb2df"

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "accounting_operation",
        "debit",
        existing_type=mysql.FLOAT(),
        type_=sa.Numeric(precision=9, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        "accounting_operation",
        "credit",
        existing_type=mysql.FLOAT(),
        type_=sa.Numeric(precision=9, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        "accounting_operation",
        "balance",
        existing_type=mysql.FLOAT(),
        type_=sa.Numeric(precision=9, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        "supplier_invoice",
        "supplier_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    # ### end Alembic commands ###


def migrate_datas():
    """
    On nettoie les factures fournisseurs sans fournisseur

    Si elles sont internes ou draft ou invalid ou en attente, on les supprime

    Sinon on crée un fournisseur anonyme par enseigne et on le lie aux factures
    """
    from alembic.context import get_bind
    from caerp_base.models.base import DBSESSION
    from sqlalchemy import select
    from zope.sqlalchemy import mark_changed

    from caerp.models.supply import SupplierInvoice
    from caerp.models.third_party import Supplier

    session = DBSESSION()
    conn = get_bind()

    # DELETE from node, so that child inheritance tables rows get deleted by cascade
    ids_to_delete = (
        conn.execute(
            """
    SELECT node.id FROM node
    INNER JOIN supplier_invoice ON supplier_invoice.id = node.id    
    WHERE
        supplier_id IS NULL
        AND 
        (
            (status IN ('draft', 'invalid', 'wait'))
            OR 
            (node.type_ = 'internalsupplier_invoice')
        )
    """
        )
        .scalars()
        .all()
    )

    delete_reqs = (
        # Delete linked nodes (file attachments)
        """
            DELETE file FROM file
            INNER JOIN node ON file.id = node.id
            WHERE parent_id IN :ids_to_delete
        """,
        "DELETE node FROM node WHERE parent_id IN :ids_to_delete",
        # Delete node and child tables
        "DELETE FROM internalsupplier_invoice WHERE id IN :ids_to_delete",
        "DELETE FROM supplier_invoice WHERE id IN :ids_to_delete",
        "DELETE FROM node WHERE id IN :ids_to_delete",
    )
    for req in delete_reqs:
        req = text(req)
        req = req.bindparams(bindparam("ids_to_delete", expanding=True))
        session.execute(req, {"ids_to_delete": ids_to_delete})
    mark_changed(session)
    session.flush()
    if (
        session.execute(
            select(SupplierInvoice).where(
                SupplierInvoice.status == "valid", SupplierInvoice.supplier_id.is_(None)
            )
        ).first()
        is not None
    ):
        suppliers_cache = {}
        for invoice in session.execute(
            select(SupplierInvoice).where(
                SupplierInvoice.status == "valid",
                SupplierInvoice.type_ == "supplier_invoice",
                SupplierInvoice.supplier_id.is_(None),
            )
        ).scalars():
            supplier = suppliers_cache.get(invoice.company_id, None)
            if supplier is None:
                supplier = Supplier(
                    name="Anonymous",
                    archived=True,
                    type="company",
                    company_id=invoice.company_id,
                )
                session.add(supplier)
            suppliers_cache[invoice.company_id] = supplier
            # Have to use relationship attr, not _id attr for sqlalchemy to handle it well at merge() time
            invoice.supplier = supplier
            session.merge(invoice)
            session.flush()
    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()
    update_database_structure()
