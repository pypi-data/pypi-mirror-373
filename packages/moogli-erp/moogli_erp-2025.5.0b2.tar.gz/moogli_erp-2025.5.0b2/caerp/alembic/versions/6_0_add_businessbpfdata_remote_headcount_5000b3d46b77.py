"""6.0 Add BusinessBPFData.remote_headcount

Revision ID: 5000b3d46b77
Revises: d187644f5870
Create Date: 2020-10-21 17:34:44.533106

"""

# revision identifiers, used by Alembic.
revision = "5000b3d46b77"
down_revision = "d187644f5870"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "business_bpf_data", sa.Column("remote_headcount", sa.Integer(), nullable=False)
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
    op.drop_column("business_bpf_data", "remote_headcount")
