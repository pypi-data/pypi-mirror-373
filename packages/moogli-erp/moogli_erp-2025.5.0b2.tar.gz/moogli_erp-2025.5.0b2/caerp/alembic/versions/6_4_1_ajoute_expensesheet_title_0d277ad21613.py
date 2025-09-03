"""6.4.1 Ajoute ExpenseSheet.title

Revision ID: 0d277ad21613
Revises: a18d2479a408
Create Date: 2022-07-14 17:41:21.870205

"""

# revision identifiers, used by Alembic.
revision = "0d277ad21613"
down_revision = "a18d2479a408"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "expense_sheet", sa.Column("title", sa.String(length=255), nullable=True)
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
    op.drop_column("expense_sheet", "title")
