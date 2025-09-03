"""6.5.5 Rend l'id URSSAF des demandes de paiement unique

Revision ID: c7ea385d87e3
Revises: a3655abb966d
Create Date: 2023-01-20 10:54:31.946896

"""

# revision identifiers, used by Alembic.
revision = "c7ea385d87e3"
down_revision = "a3655abb966d"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.create_unique_constraint(
        op.f("uq_urssaf_payment_request_urssaf_id"),
        "urssaf_payment_request",
        ["urssaf_id"],
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        op.f("uq_urssaf_payment_request_urssaf_id"),
        "urssaf_payment_request",
        type_="unique",
    )
