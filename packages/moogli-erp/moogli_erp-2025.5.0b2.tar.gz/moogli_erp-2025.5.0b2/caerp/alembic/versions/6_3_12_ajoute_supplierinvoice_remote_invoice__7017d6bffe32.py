"""6.3.12 Ajoute SupplierInvoice.remote_invoice_number

Revision ID: 7017d6bffe32
Revises: 48cbb45ca42d
Create Date: 2021-11-18 10:54:45.242664

"""

# revision identifiers, used by Alembic.
revision = "7017d6bffe32"
down_revision = "7974e0d1308e"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "supplier_invoice",
        sa.Column("remote_invoice_number", sa.String(255), nullable=False, default=""),
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    op.execute(
        """
UPDATE supplier_invoice
  JOIN node ON supplier_invoice.id = node.id
  SET remote_invoice_number = node.name
"""
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("supplier_invoice", "remote_invoice_number")
