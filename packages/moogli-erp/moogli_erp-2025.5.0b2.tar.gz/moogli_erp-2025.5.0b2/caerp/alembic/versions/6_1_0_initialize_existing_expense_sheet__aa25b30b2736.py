"""6.1.0 Initialize existing expense_sheet.official_number

Revision ID: aa25b30b2736
Revises: 60e32edeb921
Create Date: 2021-01-20 10:51:49.437779

"""

# revision identifiers, used by Alembic.
revision = "aa25b30b2736"
down_revision = "60e32edeb921"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    """
    For all the pre-existing ExpenseSheet, there was no official_number, but
    the id was used as such.

    Initialy, expensesheet_number_template is initialized to `{SEQGLOBAL}` (see
    migration 9d9ab48e488c).

    So, we initialize existing official_number with the ExpenseSheet.id. And
    fill the sequence_number table accordingly. Note that this will create
    holes in sequences for existing ids.

    This migrations considers that no ExpenseSheet have been numbered with the
    new mechanism yet.
    """
    from zope.sqlalchemy import mark_changed

    from caerp_base.models.base import DBSESSION
    from caerp.models.config import Config

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    # Delete all existing expense_sheet related sequence number. Just in case…
    op.execute("DELETE FROM sequence_number WHERE sequence LIKE 'expense_sheet_%'")

    # Initialize official_number col for pre-existing *valid* expense sheets
    op.execute("UPDATE expense_sheet SET official_number = id WHERE status = 'valid'")

    # Update the expense_sheet_global sequence according to those freshly
    # created official_number
    rows = op.execute(
        """
        INSERT INTO sequence_number (node_id, sequence, `index`)
        SELECT id, 'expense_sheet_global', official_number FROM expense_sheet
        WHERE status = 'valid'
    """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
