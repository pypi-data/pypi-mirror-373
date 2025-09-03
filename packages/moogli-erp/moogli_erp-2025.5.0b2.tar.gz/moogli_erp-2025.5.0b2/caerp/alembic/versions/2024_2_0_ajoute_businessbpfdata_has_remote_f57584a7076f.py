"""2024.2.0 Ajoute BusinessBPFData.has_remote

Revision ID: f57584a7076f
Revises: 7c3bc9b26029
Create Date: 2024-04-26 15:56:57.933147

"""

# revision identifiers, used by Alembic.
revision = "f57584a7076f"
down_revision = "7c3bc9b26029"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "business_bpf_data", sa.Column("has_remote", sa.Boolean(), nullable=False)
    )


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()

    # Initialize the has_remote field correctly
    op.execute("UPDATE business_bpf_data SET has_remote = (remote_headcount > 0)")

    # Retrospectively upgrade 2023 and 2024 BPF's to 10443*17 cerfa version
    op.execute(
        """
        UPDATE business_bpf_data 
        SET cerfa_version = '10443*17' 
        WHERE financial_year IN (2023, 2024) AND cerfa_version = '10443*16'
        """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("business_bpf_data", "has_remote")
