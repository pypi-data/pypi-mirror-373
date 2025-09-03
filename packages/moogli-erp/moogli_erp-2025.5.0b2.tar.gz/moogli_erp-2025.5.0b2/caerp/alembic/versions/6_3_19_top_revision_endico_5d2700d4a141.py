"""6.3.19 Derniere Revision caerp-co

Revision ID: 5d2700d4a141
Revises: 7017d6bffe32
Create Date: 2021-11-29 17:02:00.879992

"""

# revision identifiers, used by Alembic.
revision = "5d2700d4a141"
down_revision = "7017d6bffe32"

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

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
