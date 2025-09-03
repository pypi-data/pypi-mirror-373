"""4.3 Revision merge

Revision ID: 2abf64552d74
Revises: ('432e6cd0752c', '36fed0cf9bcd')
Create Date: 2019-02-20 15:51:03.425403

"""

# revision identifiers, used by Alembic.
revision = "2abf64552d74"
down_revision = ("432e6cd0752c", "36fed0cf9bcd", "55272ae1d65a")

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
