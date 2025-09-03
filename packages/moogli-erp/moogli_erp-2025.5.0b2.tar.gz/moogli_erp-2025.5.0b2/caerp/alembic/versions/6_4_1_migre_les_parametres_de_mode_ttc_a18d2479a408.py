"""6.4.1 Migre les paramètres de mode TTC

Revision ID: a18d2479a408
Revises: 14fb928359ce
Create Date: 2022-06-17 12:06:38.808975

"""

# revision identifiers, used by Alembic.
revision = "a18d2479a408"
down_revision = "14fb928359ce"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION
    from caerp.models.config import Config

    op.execute("UPDATE project_type SET ht_compute_mode_allowed = 1")

    ttc_compute_mode_allowed = Config.get("sale_use_ttc_mode", default=False)

    if ttc_compute_mode_allowed:
        op.execute(
            """
            UPDATE project_type pt JOIN base_project_type bpt ON pt.id = bpt.id
            SET ttc_compute_mode_allowed = 1
            WHERE bpt.name IN ('default', 'travel')
        """
        )
        op.execute(
            """
            UPDATE project_type pt JOIN base_project_type bpt ON pt.id = bpt.id
            SET ht_compute_mode_allowed = 0
            WHERE bpt.name = 'travel'
        """
        )
    op.execute("DELETE FROM config WHERE name = 'sale_use_ttc_mode'")

    session = DBSESSION()
    conn = get_bind()

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
