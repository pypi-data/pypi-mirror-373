"""6.1.0 Add supplier_invoice.official_number

Revision ID: 6373d1701a81
Revises: aa25b30b2736
Create Date: 2021-01-20 17:52:38.140778

"""

# revision identifiers, used by Alembic.
revision = "6373d1701a81"
down_revision = "aa25b30b2736"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column(
        "supplier_invoice",
        sa.Column("official_number", sa.String(length=255), nullable=True),
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.drop_column("supplier_invoice", "official_number")
