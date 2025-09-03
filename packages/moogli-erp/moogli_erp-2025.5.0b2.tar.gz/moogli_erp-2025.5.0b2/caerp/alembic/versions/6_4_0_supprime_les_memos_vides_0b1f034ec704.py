"""6.4.0 Supprime les mémos vides

Revision ID: 0b1f034ec704
Revises: cf3b3f9cfc11
Create Date: 2022-03-02 15:53:55.343709

"""

# revision identifiers, used by Alembic.
revision = "0b1f034ec704"
down_revision = "cf3b3f9cfc11"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    op.execute(
        "DELETE from status_log_entry  where status = 'unknown' and comment = ''"
    )
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
