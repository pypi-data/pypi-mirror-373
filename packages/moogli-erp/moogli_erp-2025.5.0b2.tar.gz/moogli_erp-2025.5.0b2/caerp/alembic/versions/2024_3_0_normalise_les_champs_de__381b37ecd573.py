"""2024.3.0 Normalise les champs de SaleProductTraining

Revision ID: 381b37ecd573
Revises: fad28b6bd362
Create Date: 2024-04-27 18:32:24.442164

"""

# revision identifiers, used by Alembic.
revision = "381b37ecd573"
down_revision = "fad28b6bd362"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "sale_product_training", "goals", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training",
        "prerequisites",
        existing_type=mysql.TEXT(),
        nullable=False,
    )
    op.alter_column(
        "sale_product_training", "for_who", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training",
        "duration",
        existing_type=mysql.VARCHAR(length=255),
        type_=sa.Text(),
        nullable=False,
    )
    op.alter_column(
        "sale_product_training", "content", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training",
        "teaching_method",
        existing_type=mysql.TEXT(),
        nullable=False,
    )
    op.alter_column(
        "sale_product_training",
        "logistics_means",
        existing_type=mysql.TEXT(),
        nullable=False,
    )
    op.alter_column(
        "sale_product_training",
        "more_stuff",
        existing_type=mysql.TEXT(),
        nullable=False,
    )
    op.alter_column(
        "sale_product_training",
        "evaluation",
        existing_type=mysql.TEXT(),
        nullable=False,
    )
    op.alter_column(
        "sale_product_training", "place", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training", "date", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training", "price", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training", "free_1", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training", "free_2", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "sale_product_training", "free_3", existing_type=mysql.TEXT(), nullable=False
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.alter_column(
        "sale_product_training", "free_3", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training", "free_2", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training", "free_1", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training", "price", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training", "date", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training", "place", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training", "evaluation", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training", "more_stuff", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training",
        "logistics_means",
        existing_type=mysql.TEXT(),
        nullable=True,
    )
    op.alter_column(
        "sale_product_training",
        "teaching_method",
        existing_type=mysql.TEXT(),
        nullable=True,
    )
    op.alter_column(
        "sale_product_training", "content", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training",
        "duration",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=255),
        nullable=True,
    )
    op.alter_column(
        "sale_product_training", "for_who", existing_type=mysql.TEXT(), nullable=True
    )
    op.alter_column(
        "sale_product_training",
        "prerequisites",
        existing_type=mysql.TEXT(),
        nullable=True,
    )
    op.alter_column(
        "sale_product_training", "goals", existing_type=mysql.TEXT(), nullable=True
    )
