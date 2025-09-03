"""6.1.0 Initialize existing supplier_invoice.official_number

Revision ID: 6be1efa57217
Revises: 35e9bfc2ae2c
Create Date: 2021-01-20 18:27:29.570817

"""

# revision identifiers, used by Alembic.
revision = "6be1efa57217"
down_revision = "35e9bfc2ae2c"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    """
    For all the pre-existing SupplierInvoice, there was no official_number, but
    the id was used as such.

    Initialy, supplierinvoice_number_template is initialized to `{SEQGLOBAL}` (see
    migration 35e9bfc2ae2c).

    So, we initialize existing official_number with the SupplierInvoice.id. And
    fill the sequence_number table accordingly. Note that this will create
    holes in sequences for existing ids.

    This migrations considers that no SupplierInvoice have been numbered with the
    new mechanism yet.
    """
    from zope.sqlalchemy import mark_changed

    from caerp_base.models.base import DBSESSION
    from caerp.models.config import Config

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    # Delete all existing supplier_invoice related sequence number. Just in case…
    op.execute("DELETE FROM sequence_number WHERE sequence LIKE 'supplier_invoice_%'")

    # Initialize official_number col for pre-existing expense sheets
    op.execute(
        "UPDATE supplier_invoice SET official_number = id WHERE status = 'valid'"
    )

    # Update the supplier_invoice_global sequence according to those freshly
    # created official_number
    rows = op.execute(
        """
        INSERT INTO sequence_number (node_id, sequence, `index`)
        SELECT id, 'supplier_invoice_global', official_number FROM supplier_invoice
        WHERE status = 'valid'
    """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
