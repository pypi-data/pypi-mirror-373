"""4.3.0 Add customer, project, and business links on expense lines

Revision ID: 2389fde383c7
Revises: 2a7da76844bd
Create Date: 2019-02-26 12:18:03.369626

"""

# revision identifiers, used by Alembic.
revision = "2389fde383c7"
down_revision = "665ce85c453"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column(
        "baseexpense_line",
        sa.Column(
            "customer_id", sa.Integer, sa.ForeignKey("customer.id"), nullable=True
        ),
    )
    op.add_column(
        "baseexpense_line",
        sa.Column("project_id", sa.Integer, sa.ForeignKey("project.id"), nullable=True),
    )
    op.add_column(
        "baseexpense_line",
        sa.Column(
            "business_id", sa.Integer, sa.ForeignKey("business.id"), nullable=True
        ),
    )


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("baseexpense_line", "business_id")
    op.drop_column("baseexpense_line", "project_id")
    op.drop_column("baseexpense_line", "customer_id")
