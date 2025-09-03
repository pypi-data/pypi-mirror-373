"""5.1 Add bank on supplier payments

Revision ID: 0f345f86f928
Revises: ae9f83f54480
Create Date: 2019-08-30 17:16:30.260763

"""

# revision identifiers, used by Alembic.
revision = "0f345f86f928"
down_revision = "ae9f83f54480"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column("supplier_payment", sa.Column("bank_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_supplier_payment_bank_id"),
        "supplier_payment",
        "bank_account",
        ["bank_id"],
        ["id"],
    )


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        "fk_supplier_payment_bank_id", "supplier_payment", type_="foreignkey"
    )
    op.drop_column("supplier_payment", "bank_id")
