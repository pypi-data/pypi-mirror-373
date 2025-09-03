"""6.1.0 Rename initialization config keys for invoice sequence nums

Revision ID: c2f39b66c90b
Revises: c807505b5e28
Create Date: 2021-01-19 11:41:48.003710

"""

# revision identifiers, used by Alembic.
revision = "c2f39b66c90b"
down_revision = "c807505b5e28"

from alembic import op
import sqlalchemy as sa
from zope.sqlalchemy import mark_changed

from caerp.alembic.utils import rename_column


def update_database_structure():
    rename_column(
        "company",
        "month_company_sequence_init_value",
        "month_company_invoice_sequence_init_value",
        nullable=True,
    )
    rename_column(
        "company",
        "month_company_sequence_init_date",
        "month_company_invoice_sequence_init_date",
        type_=sa.Date,
        nullable=True,
    )


def downgrade_database_structure():
    rename_column(
        "company",
        "month_company_invoice_sequence_init_value",
        "month_company_sequence_init_value",
        nullable=True,
    )
    rename_column(
        "company",
        "month_company_invoice_sequence_init_date",
        "month_company_sequence_init_date",
        type_=sa.Date,
        nullable=True,
    )


def migrate_datas(reverse=False):
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()

    renames = [
        ("global_sequence_init_value", "global_invoice_sequence_init_value"),
        ("year_sequence_init_value", "year_invoice_sequence_init_value"),
        ("year_sequence_init_date", "year_invoice_sequence_init_date"),
        ("month_sequence_init_value", "month_invoice_sequence_init_value"),
        ("month_sequence_init_date", "month_invoice_sequence_init_date"),
    ]

    for old_name, new_name in renames:
        if reverse:  # Twist !
            old_name, new_name = new_name, old_name
        conn.execute(f"UPDATE config SET name='{new_name}' WHERE name='{old_name}'")
        mark_changed(session)
        session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    migrate_datas(reverse=True)
    downgrade_database_structure()
