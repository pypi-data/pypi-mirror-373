"""6.2.0 Remplit ExpensePayment.mode et .bank pour les abandons de créance

Revision ID: 9c91fbe01305
Revises: 134b7fd3b1e3
Create Date: 2021-06-10 20:38:51.214361

"""

# revision identifiers, used by Alembic.
revision = "9c91fbe01305"
down_revision = "134b7fd3b1e3"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    op.execute(
        """
        UPDATE expense_payment
        SET mode = 'par Abandon de créance'
        WHERE waiver
    """
    )
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
