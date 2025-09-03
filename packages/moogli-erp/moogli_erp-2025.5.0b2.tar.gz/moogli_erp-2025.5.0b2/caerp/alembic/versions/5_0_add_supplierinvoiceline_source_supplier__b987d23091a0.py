"""5.1 Add SupplierInvoiceLine.source_supplier_order_line_id

Revision ID: b987d23091a0
Revises: abd68b15a448
Create Date: 2019-09-26 17:50:59.246132

"""

# revision identifiers, used by Alembic.
revision = "b987d23091a0"
down_revision = "abd68b15a448"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "supplier_invoice_line",
        sa.Column("source_supplier_order_line_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_supplier_invoice_line_source_supplier_order_line_id"),
        "supplier_invoice_line",
        "supplier_order_line",
        ["source_supplier_order_line_id"],
        ["id"],
        ondelete="SET NULL",
    )


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        op.f("fk_supplier_invoice_line_source_supplier_order_line_id"),
        "supplier_invoice_line",
        type_="foreignkey",
    )
    op.drop_column("supplier_invoice_line", "source_supplier_order_line_id")
