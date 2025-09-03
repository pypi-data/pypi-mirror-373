"""6.5.4 Ajoute infos rejet/virement aux demandes de paiement

Revision ID: a3655abb966d
Revises: c9c7d6ae5e30
Create Date: 2022-12-21 12:46:45.556327

"""

# revision identifiers, used by Alembic.
revision = "a3655abb966d"
down_revision = "c9c7d6ae5e30"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "urssaf_payment_request",
        sa.Column("urssaf_reject_message", sa.Text(), nullable=False),
    )
    op.add_column(
        "urssaf_payment_request",
        sa.Column("urssaf_transfer_message", sa.Text(), nullable=False),
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
    op.drop_column("urssaf_payment_request", "urssaf_transfer_message")
    op.drop_column("urssaf_payment_request", "urssaf_reject_message")
