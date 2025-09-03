"""6.4.0 Fix #2716: Ajout d'une colonne invert_sign dans base_accounting_measure_type

Revision ID: 69f3bf19d0fc
Revises: 5aac86c3c4f8
Create Date: 2022-02-09 10:35:35.301607

"""

# revision identifiers, used by Alembic.
revision = "69f3bf19d0fc"
down_revision = "5aac86c3c4f8"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "base_accounting_measure_type",
        sa.Column("invert_default_cd_or_dc", sa.Boolean(), nullable=True),
    )
    op.execute(
        "UPDATE base_accounting_measure_type SET\
    invert_default_cd_or_dc=0"
    )


def change_income_statement_measures_sign():
    # In order to avoid wrong sign in income statement measures after
    # migrating
    op.execute(
        "UPDATE base_accounting_measure\
            SET value=value*-1\
            WHERE type_='income_statement'"
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
    change_income_statement_measures_sign()
    migrate_datas()


def downgrade():
    op.drop_column("base_accounting_measure_type", "invert_default_cd_or_dc")
