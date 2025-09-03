"""6.7.0 Ajout d'une FK sur les task_line-product_id

Revision ID: 686fc8739aa0
Revises: 9459d94ec4e2
Create Date: 2023-09-28 17:21:01.375392

"""

# revision identifiers, used by Alembic.
revision = "686fc8739aa0"
down_revision = "9459d94ec4e2"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.create_foreign_key(
        op.f("fk_task_line_product_id"),
        "task_line",
        "product",
        ["product_id"],
        ["id"],
        ondelete="SET NULL",
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    # Set to NULL the broken foreign keys
    op.execute(
        """
UPDATE task_line LEFT JOIN product ON product_id = product.id
SET product_id = NULL
WHERE product.id IS NULL AND product_id IS NOT NULL;
"""
    )
    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()
    update_database_structure()


def downgrade():
    op.drop_constraint(op.f("fk_task_line_product_id"), "task_line", type_="foreignkey")
