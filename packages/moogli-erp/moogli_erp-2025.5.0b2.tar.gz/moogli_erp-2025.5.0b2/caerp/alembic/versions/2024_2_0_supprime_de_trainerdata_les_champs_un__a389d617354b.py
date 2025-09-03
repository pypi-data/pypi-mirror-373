"""2024.2.0 Supprime de TrainerData les champs « un petit peu de vous »

Revision ID: a389d617354b
Revises: c7f17be86e32
Create Date: 2024-04-27 16:29:15.822414

"""

# revision identifiers, used by Alembic.
revision = "a389d617354b"
down_revision = "c7f17be86e32"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_column("trainer_datas", "temperament")
    op.drop_column("trainer_datas", "indulgence")
    op.drop_column("trainer_datas", "sound")
    op.drop_column("trainer_datas", "object_")


def upgrade():
    update_database_structure()


def downgrade():
    op.add_column("trainer_datas", sa.Column("object_", mysql.TEXT(), nullable=True))
    op.add_column("trainer_datas", sa.Column("sound", mysql.TEXT(), nullable=True))
    op.add_column("trainer_datas", sa.Column("indulgence", mysql.TEXT(), nullable=True))
    op.add_column(
        "trainer_datas", sa.Column("temperament", mysql.TEXT(), nullable=True)
    )
