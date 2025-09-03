"""6.5.0 Enlarge Node.type 30 -> 50

Revision ID: c9c7d6ae5e30
Revises: 115a580ee4a9
Create Date: 2022-12-09 13:19:21.724981

"""

# revision identifiers, used by Alembic.
revision = "c9c7d6ae5e30"
down_revision = "115a580ee4a9"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():

    op.alter_column(
        "node",
        "type_",
        existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=30),
        type_=sa.String(length=50),
        nullable=False,
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
    op.alter_column(
        "node",
        "type_",
        existing_type=sa.String(length=50),
        type_=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=30),
        nullable=True,
    )
