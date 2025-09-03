"""6.7.0 Ajoute FileGenerationJob.force_download

Revision ID: 790f171aa01f
Revises: 686fc8739aa0
Create Date: 2023-10-26 17:23:06.728787

"""

# revision identifiers, used by Alembic.
revision = "790f171aa01f"
down_revision = "686fc8739aa0"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "file_generation_job", sa.Column("force_download", sa.Boolean(), nullable=True)
    )


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
    op.drop_column("file_generation_job", "force_download")
