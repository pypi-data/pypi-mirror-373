"""6.4.0 Fix 3168

Revision ID: 5aac86c3c4f8
Revises: 04ae06f3d324
Create Date: 2021-12-20 14:14:29.432934

"""

# revision identifiers, used by Alembic.
revision = "5aac86c3c4f8"
down_revision = "04ae06f3d324"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    conn.execute(
        """update `form_field_definition` set title="Lieu d'exécution" where field_name='workplace'"""
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
