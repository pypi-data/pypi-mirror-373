"""6.2.0 Move Communication ➡ StatusLogEntry

Revision ID: 35a5b1ceaa31
Revises: 64afdc450f66
Create Date: 2021-05-09 20:36:20.670537

"""

# revision identifiers, used by Alembic.
revision = "35a5b1ceaa31"
down_revision = "64afdc450f66"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_table("communication")


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()

    # Move validation status history of all tasks to status_log_entry
    # Note that, previously
    op.execute(
        """
        INSERT INTO status_log_entry (
            state_manager_key,
            node_id,
            status,
            comment,
            datetime,
            user_id

        ) SELECT
           'status',
           expense_sheet_id,
           'unknown',
           content,
           date,
           user_id

        FROM communication
        """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()
    update_database_structure()


def downgrade():
    op.create_table(
        "communication",
        sa.Column(
            "id", mysql.INTEGER(display_width=11), autoincrement=True, nullable=False
        ),
        sa.Column(
            "user_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("content", mysql.TEXT(), nullable=True),
        sa.Column("date", sa.DATE(), nullable=True),
        sa.Column(
            "expense_sheet_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["expense_sheet_id"], ["expense_sheet.id"], name="communication_ibfk_2"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["accounts.id"], name="fk_communication_user_id"
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_default_charset="utf8",
        mysql_engine="InnoDB",
    )
