"""2024.2.0 Rend certains champs de BusinessBPFData nullables

Revision ID: c7f17be86e32
Revises: f57584a7076f
Create Date: 2024-04-19 19:06:59.652536

"""

# revision identifiers, used by Alembic.
revision = "c7f17be86e32"
down_revision = "f57584a7076f"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "business_bpf_data",
        "training_speciality_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.alter_column(
        "business_bpf_data",
        "training_goal_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    op.execute(
        """
        UPDATE business_bpf_data_income_source
          SET income_category_id = 31
          WHERE business_bpf_data_id in (
            SELECT id FROM business_bpf_data WHERE is_subcontract=1
          )
    """
    )

    op.execute(
        """
      UPDATE business_bpf_data 
        SET 
          training_goal_id = NULL, 
          training_speciality_id = NULL
        WHERE is_subcontract = 1
    """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.alter_column(
        "business_bpf_data",
        "training_goal_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "business_bpf_data",
        "training_speciality_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
