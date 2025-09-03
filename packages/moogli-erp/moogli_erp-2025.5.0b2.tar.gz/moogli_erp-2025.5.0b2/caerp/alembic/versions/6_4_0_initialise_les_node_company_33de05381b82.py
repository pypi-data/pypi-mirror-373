"""6.4.0 Initialise les Node Company

Revision ID: 33de05381b82
Revises: f80470768fe1
Create Date: 2022-03-03 11:21:36.836930

"""

# revision identifiers, used by Alembic.
revision = "33de05381b82"
down_revision = "f80470768fe1"

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

    # Just in case we have empty or null values in updated_at / created_at
    for field in ("updated_at", "created_at"):
        op.execute(
            f"UPDATE company SET {field} = CURDATE() "
            f"WHERE ({field} IS NULL) OR ({field} = '0000-00-00')"
        )

    op.execute(
        "INSERT INTO node(id, created_at, updated_at, name, type_, parent_id)"
        "  SELECT id, "
        "    date_add(created_at, interval 12 hour), "  # date ➡ datetime
        "    date_add(updated_at, interval 12 hour), "  # date ➡ datetime
        "    name, 'company', NULL"
        "  FROM company"
    )
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
