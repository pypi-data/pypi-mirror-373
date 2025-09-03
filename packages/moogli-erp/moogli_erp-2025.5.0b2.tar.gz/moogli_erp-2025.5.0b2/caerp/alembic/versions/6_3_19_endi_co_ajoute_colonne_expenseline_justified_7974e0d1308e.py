"""6.3.19 Caerp-co Ajoute colonne ExpenseLine.justified

Revision ID: 7974e0d1308e
Revises: b3d7f32aea9d
Create Date: 2021-11-14 10:24:46.577492

"""

# revision identifiers, used by Alembic.
revision = "7974e0d1308e"
down_revision = "b3d7f32aea9d"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("expense_line", sa.Column("justified", sa.Boolean(), nullable=False))


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    op.execute(
        """
    UPDATE expense_line el
      JOIN baseexpense_line bel ON el.id = bel.id
      JOIN expense_sheet es ON bel.sheet_id = es.id
      SET el.justified = es.justified
    """
    )
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("expense_line", "justified")
