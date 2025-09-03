"""6.4.0 Renumérotation des Company

Revision ID: f80470768fe1
Revises: cf3b3f9cfc11
Create Date: 2022-03-03 10:36:20.904767

"""

# revision identifiers, used by Alembic.
revision = "f80470768fe1"
down_revision = "5d2700d4a141"

from alembic import op
import sqlalchemy as sa


import logging

logger = logging.getLogger(__name__)


def update_database_structure():
    pass


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    dbname = session.bind.url.database
    conn = get_bind()
    company_id_offset = conn.execute("SELECT MAX(node.id) + 100 FROM node").scalar()
    logger.info(f"Going to offset all company.id by +{company_id_offset}")
    foreign_keys_to_company = conn.execute(
        f"""
        select fks.table_name as foreign_table, kcu.column_name as fk_column_name
          from information_schema.referential_constraints fks
          join information_schema.key_column_usage kcu
            on fks.constraint_schema = kcu.table_schema
            and fks.table_name = kcu.table_name
            and fks.constraint_name = kcu.constraint_name
        where fks.constraint_schema = '{dbname}'
        and fks.referenced_table_name= 'company';
        """
    )

    op.execute("SET FOREIGN_KEY_CHECKS=0;")
    for table_name, column_name in foreign_keys_to_company.fetchall():
        logger.info(f"Offseting {table_name}.{column_name}")
        op.execute(
            f"UPDATE {table_name} "
            f"SET {column_name} = {column_name } + {company_id_offset}"
        )
    op.execute(f"UPDATE company SET id = id + {company_id_offset}")
    op.execute("SET FOREIGN_KEY_CHECKS=1;")
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
