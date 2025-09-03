"""6.4.0 Passe StatusLogEntry.datetime en DateTime() normal plutôt que mysql.Datetime(fsp=6)

Revision ID: 3db408759e73
Revises: 7ac32c4dd6f1
Create Date: 2022-02-28 17:49:46.166713

"""

# revision identifiers, used by Alembic.
revision = "3db408759e73"
down_revision = "7ac32c4dd6f1"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "status_log_entry",
        "datetime",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "expense_sheet",
        "status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "supplier_order",
        "status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "supplier_invoice",
        "status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "supplier_invoice",
        "paid_status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "expense_sheet",
        "paid_status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.alter_column(
        "status_log_entry",
        "datetime",
        existing_type=mysql.DATETIME(),
        type_=mysql.DATETIME(fsp=6),
    )
    op.alter_column(
        "expense_sheet",
        "status_date",
        existing_type=mysql.DATETIME(),
        type_=mysql.DATETIME(fsp=6),
    )
    op.alter_column(
        "supplier_order",
        "status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "supplier_invoice",
        "status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "supplier_invoice",
        "paid_status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
    op.alter_column(
        "expense_sheet",
        "paid_status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=mysql.DATETIME(),
    )
