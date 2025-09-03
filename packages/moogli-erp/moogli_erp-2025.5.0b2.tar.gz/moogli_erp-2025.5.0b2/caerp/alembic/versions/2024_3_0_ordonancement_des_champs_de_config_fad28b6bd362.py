"""2024.3.0 ordonancement des champs de config

Revision ID: fad28b6bd362
Revises: 077f73d16a76
Create Date: 2024-05-21 18:33:56.753700

"""

# revision identifiers, used by Alembic.
revision = "fad28b6bd362"
down_revision = "077f73d16a76"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("activity_modes", sa.Column("order", sa.Integer(), nullable=False))
    op.add_column("activity_type", sa.Column("order", sa.Integer(), nullable=False))
    op.add_column("workunity", sa.Column("order", sa.Integer(), nullable=False))


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
    op.drop_column("activity_modes", "order")
    op.drop_column("activity_type", "order")
    op.drop_column("workunity", "order")
