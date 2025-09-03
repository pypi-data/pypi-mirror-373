"""6.4.0 Ajoute StatusLogEntry.label

Revision ID: 27e3d45bfea3
Revises: 69f3bf19d0fc
Create Date: 2022-02-07 17:45:50.335900

"""

# revision identifiers, used by Alembic.
revision = "27e3d45bfea3"
down_revision = "69f3bf19d0fc"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "status_log_entry", sa.Column("label", sa.String(length=255), nullable=False)
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
    op.drop_column("status_log_entry", "label")
