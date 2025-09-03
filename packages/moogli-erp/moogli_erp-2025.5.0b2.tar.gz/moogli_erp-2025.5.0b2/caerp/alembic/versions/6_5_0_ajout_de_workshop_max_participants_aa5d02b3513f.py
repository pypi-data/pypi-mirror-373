"""6.5.0 Ajout de workshop.max_participants

Revision ID: aa5d02b3513f
Revises: e388e68ad1d7
Create Date: 2022-11-17 08:57:08.839665

"""

# revision identifiers, used by Alembic.
revision = "aa5d02b3513f"
down_revision = "09d79360a4d8"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "workshop", sa.Column("max_participants", sa.Integer(), nullable=False)
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
    migrate_datas()


def downgrade():
    op.drop_column("workshop", "max_participants")
