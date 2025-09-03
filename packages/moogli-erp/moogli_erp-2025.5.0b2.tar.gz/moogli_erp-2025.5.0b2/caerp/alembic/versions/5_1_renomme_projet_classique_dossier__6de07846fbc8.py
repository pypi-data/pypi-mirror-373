"""5.1 Renomme « projet classique » → « dossier classique »

Revision ID: 6de07846fbc8
Revises: d824a2ca7973
Create Date: 2019-11-07 17:10:12.285377

"""

# revision identifiers, used by Alembic.
revision = "6de07846fbc8"
down_revision = "d824a2ca7973"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    pass


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    conn.execute(
        "UPDATE project_type join base_project_type on base_project_type.id = project_type.id set label = 'Dossier classique' WHERE label = 'Projet classique' AND name = 'default'"
    )
    from zope.sqlalchemy import mark_changed

    mark_changed(session)


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    conn.execute(
        "UPDATE project_type join base_project_type on base_project_type.id = project_type.id set label = 'Projet classique' WHERE label = 'Dossier classique' AND name = 'default'"
    )
    from zope.sqlalchemy import mark_changed

    mark_changed(session)
