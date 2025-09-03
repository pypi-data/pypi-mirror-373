"""6.0 Add ExpenseLine.manual_ttc

Revision ID: 6000812cf022
Revises: ad67b1ce434c
Create Date: 2020-10-08 12:03:16.663778

"""

# revision identifiers, used by Alembic.
revision = "6000812cf022"
down_revision = "ad67b1ce434c"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("expense_line", sa.Column("manual_ttc", sa.Integer(), nullable=True))


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("expense_line", "manual_ttc")
