"""2025.1.1 : Droits d'accès aux états de gestion des enseignes

Create Date: 2025-01-16 16:26:35.282952

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "b987d67518eb"

# Revises (previous revision or revisions):
down_revision = "820a37d9c692"

from alembic import op
import sqlalchemy as sa

from caerp.models.populate import populate_access_rights


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION
    from caerp.models.user.group import Group
    from caerp.models.user.access_right import AccessRight

    session = DBSESSION()

    # On crée le nouvel access right dans la bdd
    populate_access_rights(session)
    session.flush()

    new_access_right = session.execute(
        sa.select(AccessRight).filter(
            AccessRight.name == "global_company_access_accounting"
        )
    ).scalar_one()

    for group in session.execute(
        sa.select(Group).filter(
            Group.access_rights.any(AccessRight.name == "global_company_supervisor")
        )
    ).scalars():
        group.access_rights.append(new_access_right)
        session.merge(group)
    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()


def downgrade():
    pass
