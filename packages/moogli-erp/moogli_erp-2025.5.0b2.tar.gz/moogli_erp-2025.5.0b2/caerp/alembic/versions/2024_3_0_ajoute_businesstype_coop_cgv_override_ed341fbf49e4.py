"""2024.3.0 Ajoute BusinessType.coop_cgv_override

Create Date: 2024-06-10 17:25:06.332182

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "ed341fbf49e4"

# Revises (previous revision or revisions):
down_revision = "265b409ec218"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column(
        "business_type", sa.Column("coop_cgv_override", sa.Text(), nullable=False)
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.drop_column("business_type", "coop_cgv_override")
