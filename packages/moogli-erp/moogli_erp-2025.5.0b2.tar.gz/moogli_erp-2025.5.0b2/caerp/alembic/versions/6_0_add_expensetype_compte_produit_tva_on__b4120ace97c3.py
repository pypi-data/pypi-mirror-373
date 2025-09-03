"""6.0 Add ExpenseType.compte_produit_tva_on_margin

Revision ID: b4120ace97c3
Revises: ae9a26b79ac0
Create Date: 2020-10-12 17:53:24.656257

"""

# revision identifiers, used by Alembic.
revision = "b4120ace97c3"
down_revision = "ae9a26b79ac0"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "expense_type",
        sa.Column("compte_produit_tva_on_margin", sa.String(length=15), nullable=True),
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
    op.drop_column("expense_type", "compte_produit_tva_on_margin")
