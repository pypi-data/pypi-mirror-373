"""6.2.0 Fix #2672: Add a column user_id in SupplierInvoicePayment

Revision ID: 3b0e44e60ad1
Revises: 2ae94459f6e7
Create Date: 2021-06-07 16:06:47.621586

"""

# revision identifiers, used by Alembic.
revision = "3b0e44e60ad1"
down_revision = "2ae94459f6e7"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "base_supplier_payment", sa.Column("user_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_base_supplier_payment_user_id"),
        "base_supplier_payment",
        "accounts",
        ["user_id"],
        ["id"],
        ondelete="set null",
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        op.f("fk_base_supplier_payment_user_id"),
        "base_supplier_payment",
        type_="foreignkey",
    )
    op.drop_column("base_supplier_payment", "user_id")
