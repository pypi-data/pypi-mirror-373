"""6.1.0 Set back SupplierInvoice.status → wait when supplier is unknown and status is valid

Revision ID: 7a5daccd86a8
Revises: 93bd3589fa62
Create Date: 2021-02-02 14:10:57.633806

"""

# revision identifiers, used by Alembic.
revision = "7a5daccd86a8"
down_revision = "93bd3589fa62"

from alembic import op
import sqlalchemy as sa


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()

    op.execute(
        """
      UPDATE supplier_invoice SET status = 'wait'
      WHERE status = 'valid' AND supplier_id IS NULL
    """
    )
    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()


def downgrade():
    pass
