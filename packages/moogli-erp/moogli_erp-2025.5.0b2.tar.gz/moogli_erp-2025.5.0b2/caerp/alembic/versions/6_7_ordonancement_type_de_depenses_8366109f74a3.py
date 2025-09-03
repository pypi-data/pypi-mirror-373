"""6.7 ordonancement type de depenses

Revision ID: 8366109f74a3
Revises: ceb8faaa2785
Create Date: 2023-11-29 14:54:47.056415

"""

# revision identifiers, used by Alembic.
revision = "8366109f74a3"
down_revision = "ceb8faaa2785"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("expense_type", sa.Column("order", sa.Integer(), nullable=False))


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    session.execute(
        """
    update expense_type,
        (select id, rank() over (partition by type order by label) as 'order' from expense_type) as ranks
    set expense_type.order = ranks.order - 1
    where expense_type.id = ranks.id
    """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("expense_type", "order")
