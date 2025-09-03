"""${caerp_version} ${message}

Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "${str(up_revision)}"

# Revises (previous revision or revisions):
down_revision = ${repr(down_revision).replace("'", '"')}

from alembic import op
import sqlalchemy as sa
${imports +"\n" if imports else ""}

def update_database_structure():
    ${upgrades if upgrades else "pass"}


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
    ${downgrades if downgrades else "pass"}
