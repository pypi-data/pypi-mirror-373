"""4.3 Add business_type.bpf_related

Revision ID: 4f37cb2ebd97
Revises: e4acc2150d9
Create Date: 2019-02-13 15:01:00.961695

"""

# revision identifiers, used by Alembic.
revision = "4f37cb2ebd97"
down_revision = "e4acc2150d9"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "business_type", sa.Column("bpf_related", sa.Boolean(), nullable=False)
    )


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    from caerp.models.project.types import BusinessType

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    query = BusinessType.query().filter_by(label="Formation")
    query.update(dict(bpf_related=True))
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("business_type", "bpf_related")
