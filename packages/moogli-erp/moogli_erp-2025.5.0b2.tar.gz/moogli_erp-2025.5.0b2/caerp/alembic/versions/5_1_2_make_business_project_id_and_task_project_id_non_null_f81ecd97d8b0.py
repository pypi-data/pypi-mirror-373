"""5.1.2 Make Business.project_id and Task.project_id non-nullable

Revision ID: f81ecd97d8b0
Revises: 092c50781ff5
Create Date: 2019-11-13 12:02:46.232788

"""

# revision identifiers, used by Alembic.
revision = "f81ecd97d8b0"
down_revision = "092c50781ff5"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.execute("set foreign_key_checks=0;")
    op.alter_column(
        "business",
        "project_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "task",
        "project_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.execute("set foreign_key_checks=1;")


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.execute("set foreign_key_checks=0;")
    op.alter_column(
        "business",
        "project_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.alter_column(
        "task",
        "project_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.execute("set foreign_key_checks=1;")
