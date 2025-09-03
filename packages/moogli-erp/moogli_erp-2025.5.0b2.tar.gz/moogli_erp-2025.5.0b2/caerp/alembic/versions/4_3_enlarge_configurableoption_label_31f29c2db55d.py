"""4.3 Enlarge ConfigurableOption.label

Revision ID: 31f29c2db55d
Revises: 544149b913e4
Create Date: 2019-03-06 16:55:32.212708

"""

# revision identifiers, used by Alembic.
revision = "31f29c2db55d"
down_revision = "544149b913e4"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "configurable_option",
        "label",
        existing_type=mysql.VARCHAR(length=100),
        type_=sa.String(length=200),
        existing_nullable=False,
    )


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.alter_column(
        "configurable_option",
        "label",
        existing_type=sa.String(length=200),
        type_=mysql.VARCHAR(length=100),
        existing_nullable=False,
    )
