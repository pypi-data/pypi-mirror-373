"""5.1 Add additional fields on payments

Revision ID: 13bbeb791326
Revises: 0f345f86f928
Create Date: 2019-09-10 09:30:50.825013

"""

# revision identifiers, used by Alembic.
revision = "13bbeb791326"
down_revision = "0f345f86f928"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column("payment", sa.Column("customer_bank_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_payment_customer_bank_id"),
        "payment",
        "bank",
        ["customer_bank_id"],
        ["id"],
    )
    op.add_column("payment", sa.Column("check_number", sa.String(50), nullable=True))


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint("fk_payment_customer_bank_id", "payment", type_="foreignkey")
    op.drop_column("payment", "customer_bank_id")
    op.drop_column("payment", "check_number")
