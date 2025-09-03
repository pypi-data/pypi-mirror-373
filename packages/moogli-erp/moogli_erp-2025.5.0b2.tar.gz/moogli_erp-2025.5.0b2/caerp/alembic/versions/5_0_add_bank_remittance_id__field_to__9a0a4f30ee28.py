"""5.0 Add bank_remittance_id_* field to ExpensePayment

Revision ID: 9a0a4f30ee28
Revises: 15f720735537
Create Date: 2019-06-19 20:09:26.086149

"""

# revision identifiers, used by Alembic.
revision = "9a0a4f30ee28"
down_revision = "15f720735537"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "expense_payment",
        sa.Column("bank_remittance_id", sa.String(length=255), nullable=True),
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
    op.drop_column("expense_payment", "bank_remittance_id")
