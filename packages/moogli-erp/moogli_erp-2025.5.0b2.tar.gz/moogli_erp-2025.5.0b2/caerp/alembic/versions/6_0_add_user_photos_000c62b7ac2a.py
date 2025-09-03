"""6.0 Add user photos

Revision ID: 000c62b7ac2a
Revises: 82acaab789be
Create Date: 2020-09-28 17:00:35.717184

"""

# revision identifiers, used by Alembic.
revision = "000c62b7ac2a"
down_revision = "3d875d983693"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("accounts", sa.Column("photo_id", sa.Integer(), nullable=True))
    op.add_column(
        "accounts", sa.Column("photo_is_publishable", sa.Boolean(), nullable=False)
    )
    op.create_foreign_key(
        op.f("fk_accounts_photo_id"), "accounts", "file", ["photo_id"], ["id"]
    )


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(op.f("fk_accounts_photo_id"), "accounts", type_="foreignkey")
    op.drop_column("accounts", "photo_is_publishable")
    op.drop_column("accounts", "photo_id")
