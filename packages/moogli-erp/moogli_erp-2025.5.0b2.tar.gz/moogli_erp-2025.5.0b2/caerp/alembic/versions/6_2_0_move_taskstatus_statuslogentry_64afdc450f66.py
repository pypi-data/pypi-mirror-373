"""6.2.0 Move TaskStatus ➡ StatusLogEntry

Revision ID: 64afdc450f66
Revises: c4b03f713cae
Create Date: 2021-05-07 14:54:00.496440

"""

# revision identifiers, used by Alembic.
revision = "64afdc450f66"
down_revision = "65a3bfcfb616"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_table("task_status")


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()

    # convert old status code geninv
    op.execute(
        """
        UPDATE task_status
        SET status_code = 'signed'
        WHERE status_code = 'geninv';
        """
    )

    # Move validation status history of all tasks to status_log_entry
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
           task_id,
           status_code,
           status_comment,
           status_date,
           status_person_id

        FROM task_status
        WHERE status_code IN ('wait', 'valid', 'invalid', 'draft')
        """
    )

    # Move payment status of all invoices to status_log_entry
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
           'paid_status',
           task_id,
           status_code,
           status_comment,
           status_date,
           status_person_id


        FROM task_status
        JOIN invoice ON task_status.task_id = invoice.id
        WHERE status_code IN ('resulted', 'waiting', 'paid');
        """
    )

    # Move payment customer status of all estimations to status_log_entryç
    # aboinv/aboest statuses will be lost ; that is expected
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
           'signed_status',
           task_id,
           status_code,
           status_comment,
           status_date,
           status_person_id

        FROM task_status
        JOIN estimation ON task_status.task_id = estimation.id
        WHERE status_code IN ('waiting', 'aborted', 'sent', 'signed');
        """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()
    update_database_structure()


def downgrade():
    op.create_table(
        "task_status",
        sa.Column(
            "id", mysql.INTEGER(display_width=11), autoincrement=True, nullable=False
        ),
        sa.Column(
            "task_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("status_code", mysql.VARCHAR(length=10), nullable=True),
        sa.Column("status_comment", mysql.TEXT(), nullable=True),
        sa.Column(
            "status_person_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("status_date", sa.DATE(), nullable=True),
        sa.ForeignKeyConstraint(
            ["status_person_id"],
            ["accounts.id"],
            name="fk_task_status_status_person_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["task.id"], name="task_status_ibfk_1", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_default_charset="utf8",
        mysql_engine="InnoDB",
    )
