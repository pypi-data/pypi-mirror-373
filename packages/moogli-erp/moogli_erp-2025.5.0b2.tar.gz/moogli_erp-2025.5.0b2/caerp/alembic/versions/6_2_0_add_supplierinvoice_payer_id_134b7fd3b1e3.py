"""6.2.0 Add SupplierInvoice.payer_id

Revision ID: 134b7fd3b1e3
Revises: 3b0e44e60ad1
Create Date: 2021-05-24 17:59:01.943403

"""

# revision identifiers, used by Alembic.
revision = "134b7fd3b1e3"
down_revision = "3b0e44e60ad1"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "supplier_invoice", sa.Column("payer_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_supplier_invoice_payer_id"),
        "supplier_invoice",
        "accounts",
        ["payer_id"],
        ["id"],
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    conn.execute(
        """
    CREATE TEMPORARY TABLE status_log_extract (
    WITH temp AS (
          SELECT
             status_log_entry.user_id infered_user_id,
             status_log_entry.node_id existing_node_id,
             ROW_NUMBER() OVER(PARTITION BY node_id ORDER BY datetime, status_log_entry.id DESC) row_number
           FROM status_log_entry
           JOIN supplier_invoice ON status_log_entry.node_id = supplier_invoice.id
           JOIN accounts on status_log_entry.user_id = accounts.id
           JOIN company_employee ON company_employee.account_id = accounts.id
           WHERE supplier_invoice.company_id = company_employee.company_id
        )
        SELECT * FROM temp WHERE row_number = 1
       )
    """
    )

    conn.execute(
        """
       UPDATE supplier_invoice
       JOIN status_log_extract
         ON status_log_extract.existing_node_id = supplier_invoice.id
       SET payer_id = status_log_extract.infered_user_id
       WHERE payer_id IS NULL
       ;
    """
    )

    # On va récupérer une liste

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        op.f("fk_supplier_invoice_payer_id"), "supplier_invoice", type_="foreignkey"
    )
    op.drop_column("supplier_invoice", "payer_id")
