"""6.0 Add LineModelMixin FK constraint

Revision ID: 41f072b2df0e
Revises: f81ecd97d8b0
Create Date: 2019-11-20 16:14:02.497494

"""

# revision identifiers, used by Alembic.
revision = "41f072b2df0e"
down_revision = "6fb9c80c6fe3"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.create_foreign_key(
        op.f("fk_supplier_invoice_line_type_id"),
        "supplier_invoice_line",
        "expense_type",
        ["type_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_supplier_order_line_type_id"),
        "supplier_order_line",
        "expense_type",
        ["type_id"],
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
        op.f("fk_supplier_order_line_type_id"),
        "supplier_order_line",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_supplier_invoice_line_type_id"),
        "supplier_invoice_line",
        type_="foreignkey",
    )
