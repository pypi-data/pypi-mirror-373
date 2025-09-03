"""2024.3.0 Agrandit SaleProductTraining.gateways

Create Date: 2024-06-07 10:35:27.739550

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "12a5d42d5158"

# Revises (previous revision or revisions):
down_revision = "00ceb1d68304"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "sale_product_training",
        "gateways",
        existing_type=mysql.VARCHAR(length=20),
        type_=sa.Text(),
        existing_nullable=False,
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.alter_column(
        "sale_product_training",
        "gateways",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=20),
        existing_nullable=False,
    )
