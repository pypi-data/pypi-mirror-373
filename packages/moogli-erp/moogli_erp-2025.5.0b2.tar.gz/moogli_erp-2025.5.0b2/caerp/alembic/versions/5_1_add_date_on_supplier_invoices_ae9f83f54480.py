"""5.1 Add date on supplier invoices

Revision ID: ae9f83f54480
Revises: 273d4944c9e0
Create Date: 2019-08-29 14:42:13.075452

"""

# revision identifiers, used by Alembic.
revision = "ae9f83f54480"
down_revision = "273d4944c9e0"

from alembic import op
import sqlalchemy as sa
from caerp_base.models.base import DBSESSION
from zope.sqlalchemy import mark_changed


def update_database_structure():
    op.add_column("supplier_invoice", sa.Column("date", sa.Date(), nullable=True))


def migrate_datas():
    session = DBSESSION()
    op.execute("UPDATE `supplier_invoice` SET `date`=`status_date`")
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("supplier_invoice", "date")
