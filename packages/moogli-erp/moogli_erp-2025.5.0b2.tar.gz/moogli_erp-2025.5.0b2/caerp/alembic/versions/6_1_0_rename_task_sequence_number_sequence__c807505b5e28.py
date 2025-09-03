"""6.1.0 Rename task_sequence_number → sequence_number

Revision ID: c807505b5e28
Revises: 06342a8aa5df
Create Date: 2021-01-19 11:09:13.886083

"""

# revision identifiers, used by Alembic.
revision = "c807505b5e28"
down_revision = "06342a8aa5df"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from caerp.alembic.utils import force_rename_table, rename_column


def update_database_structure():
    op.drop_constraint(
        "fk_task_sequence_number_task_id", "task_sequence_number", type_="foreignkey"
    )
    force_rename_table("task_sequence_number", "sequence_number")
    rename_column("sequence_number", "task_id", "node_id")
    op.create_foreign_key(
        op.f("fk_task_sequence_number_node_id"),
        "sequence_number",
        "node",
        ["node_id"],
        ["id"],
        ondelete="cascade",
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
    rename_column("sequence_number", "node_id", "task_id")
    force_rename_table("sequence_number", "task_sequence_number")
