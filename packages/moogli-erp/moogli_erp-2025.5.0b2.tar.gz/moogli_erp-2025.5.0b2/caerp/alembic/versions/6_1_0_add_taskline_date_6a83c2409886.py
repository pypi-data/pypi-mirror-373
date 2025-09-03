"""6.1.0 Add TaskLine.date

Revision ID: 6a83c2409886
Revises: d7c5e3dce471
Create Date: 2021-02-16 16:50:35.165471

"""

# revision identifiers, used by Alembic.
revision = "6a83c2409886"
down_revision = "d7c5e3dce471"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("task_line", sa.Column("date", sa.Date(), nullable=True))


def upgrade():
    update_database_structure()


def downgrade():
    op.drop_column("task_line", "date")
