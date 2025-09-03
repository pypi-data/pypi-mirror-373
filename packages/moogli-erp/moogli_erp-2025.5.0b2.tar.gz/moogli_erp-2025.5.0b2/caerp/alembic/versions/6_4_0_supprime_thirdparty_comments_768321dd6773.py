"""6.4.0 Supprime ThirdParty.comments

Revision ID: 768321dd6773
Revises: 7aa5d4ce2813
Create Date: 2022-02-24 17:17:56.021684

"""

# revision identifiers, used by Alembic.
revision = "768321dd6773"
down_revision = "7aa5d4ce2813"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_column("third_party", "comments")


def upgrade():
    update_database_structure()


def downgrade():
    op.add_column("third_party", sa.Column("comments", mysql.TEXT(), nullable=True))
