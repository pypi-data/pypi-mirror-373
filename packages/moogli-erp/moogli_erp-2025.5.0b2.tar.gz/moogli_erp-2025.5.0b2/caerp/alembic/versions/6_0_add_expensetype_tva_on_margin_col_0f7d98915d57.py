"""6.0 Add ExpenseType.tva_on_margin col

Revision ID: 0f7d98915d57
Revises: 41f072b2df0e
Create Date: 2019-12-04 16:42:17.319750

"""

# revision identifiers, used by Alembic.
revision = "0f7d98915d57"
down_revision = "41f072b2df0e"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "expense_type", sa.Column("tva_on_margin", sa.Boolean(), nullable=True)
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
    op.drop_column("expense_type", "tva_on_margin")
