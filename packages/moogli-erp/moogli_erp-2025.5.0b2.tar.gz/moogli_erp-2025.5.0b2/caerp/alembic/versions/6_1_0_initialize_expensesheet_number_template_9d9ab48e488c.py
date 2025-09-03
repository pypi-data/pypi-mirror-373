"""6.1.0 initialize expensesheet_number_template

Revision ID: 9d9ab48e488c
Revises: c2f39b66c90b
Create Date: 2021-01-19 20:45:22.203866

"""

# revision identifiers, used by Alembic.
revision = "9d9ab48e488c"
down_revision = "c2f39b66c90b"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from caerp_base.models.base import DBSESSION
    from caerp.models.config import Config

    session = DBSESSION()

    Config.query().filter_by(name="expensesheet_number_template").delete()

    default_format = Config(name="expensesheet_number_template", value="{SEQGLOBAL}")

    session.add(default_format)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
