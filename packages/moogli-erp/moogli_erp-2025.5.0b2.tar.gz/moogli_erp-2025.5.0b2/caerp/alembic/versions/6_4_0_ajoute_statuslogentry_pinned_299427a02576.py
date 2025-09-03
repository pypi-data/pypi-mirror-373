"""6.4.0 Ajoute StatusLogEntry.pinned

Revision ID: 299427a02576
Revises: 783c9072821f
Create Date: 2022-02-24 12:18:59.017330

"""

# revision identifiers, used by Alembic.
revision = "299427a02576"
down_revision = "783c9072821f"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("status_log_entry", sa.Column("pinned", sa.Boolean(), nullable=False))


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
    op.drop_column("status_log_entry", "pinned")
