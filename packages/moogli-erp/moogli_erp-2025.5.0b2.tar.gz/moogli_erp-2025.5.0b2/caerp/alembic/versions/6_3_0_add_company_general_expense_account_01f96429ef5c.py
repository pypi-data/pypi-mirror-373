"""6.3.0 Add Company.general_expense_account

Revision ID: 01f96429ef5c
Revises: 6d80ecf34a1a
Create Date: 2021-09-20 13:14:51.008677

"""

# revision identifiers, used by Alembic.
revision = "01f96429ef5c"
down_revision = "6d80ecf34a1a"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "company",
        sa.Column("general_expense_account", sa.String(length=255), nullable=True),
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
    op.drop_column("company", "general_expense_account")
