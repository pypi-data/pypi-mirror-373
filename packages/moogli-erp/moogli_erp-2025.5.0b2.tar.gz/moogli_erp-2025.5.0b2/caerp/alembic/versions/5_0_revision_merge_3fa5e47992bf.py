"""5.0 Revision merge

Revision ID: 3fa5e47992bf
Revises: ('3be3fcec8d38', '48f2b841d4fc')
Create Date: 2019-03-28 21:40:55.996486

"""

# revision identifiers, used by Alembic.
revision = "3fa5e47992bf"
down_revision = ("3be3fcec8d38", "48f2b841d4fc")

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
