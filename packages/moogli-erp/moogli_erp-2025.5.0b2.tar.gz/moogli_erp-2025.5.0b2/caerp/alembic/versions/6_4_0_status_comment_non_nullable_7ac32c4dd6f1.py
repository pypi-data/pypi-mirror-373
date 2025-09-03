"""6.4.0 status_comment_non_nullable

Revision ID: 7ac32c4dd6f1
Revises: 3573a1ea51b7
Create Date: 2022-02-28 16:17:58.130611

"""

# revision identifiers, used by Alembic.
revision = "7ac32c4dd6f1"
down_revision = "3573a1ea51b7"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "expense_sheet", "status_comment", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "expense_sheet",
        "paid_status_comment",
        existing_type=mysql.TEXT(),
        nullable=False,
    )
    op.alter_column(
        "status_log_entry", "comment", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "supplier_invoice", "status_comment", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "supplier_invoice",
        "paid_status_comment",
        existing_type=mysql.TEXT(),
        nullable=False,
    )
    op.alter_column(
        "supplier_order", "status_comment", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "task", "status_comment", existing_type=mysql.TEXT(), nullable=False
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    for table, column in [
        ("expense_sheet", "status_comment"),
        ("expense_sheet", "paid_status_comment"),
        ("supplier_invoice", "status_comment"),
        ("supplier_invoice", "paid_status_comment"),
        ("supplier_order", "status_comment"),
        ("task", "status_comment"),
        ("status_log_entry", "comment"),
    ]:
        cmd = f"UPDATE {table} SET {column} = '' WHERE {column} IS NULL"
        op.execute(cmd)

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()
    update_database_structure()


def downgrade():
    op.alter_column(
        "supplier_order", "status_comment", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "supplier_invoice",
        "paid_status_comment",
        existing_type=mysql.TEXT(),
        nullable=True,
    )
    op.alter_column(
        "supplier_invoice", "status_comment", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "status_log_entry", "comment", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "expense_sheet",
        "paid_status_comment",
        existing_type=mysql.TEXT(),
        nullable=True,
    )
    op.alter_column(
        "expense_sheet", "status_comment", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column("task", "status_comment", existing_type=mysql.TEXT(), nullable=True)
