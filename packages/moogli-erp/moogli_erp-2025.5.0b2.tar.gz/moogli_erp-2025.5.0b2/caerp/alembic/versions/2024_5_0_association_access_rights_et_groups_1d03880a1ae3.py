"""2024.5.0 Association access_rights et groupes par défaut

Create Date: 2024-10-23 11:01:53.253957

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "1d03880a1ae3"

# Revises (previous revision or revisions):
down_revision = "e22f7bc4b1ca"
from sqlalchemy import select
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from caerp.alembic import utils


def update_database_schema():
    utils.add_column("login", sa.Column("account_type", sa.String(14), nullable=False))
    if utils.column_exists("groups", "primary"):
        op.drop_column("groups", "primary")
    utils.add_column("groups", sa.Column("account_type", sa.String(14), nullable=False))
    utils.add_column(
        "groups", sa.Column("default_for_account_type", sa.Boolean(), nullable=False)
    )
    op.alter_column(
        "groups", "name", existing_type=mysql.VARCHAR(length=30), nullable=False
    )
    op.alter_column(
        "groups", "label", existing_type=mysql.VARCHAR(length=255), nullable=False
    )


def set_primary_groups_on_login(session):
    from caerp.models.user import Login

    for login in Login.query():
        if "admin" in login.groups or "manager" in login.groups:
            login.account_type = "equipe_appui"
            session.merge(login)
        else:
            login.account_type = "entrepreneur"
            session.merge(login)


def ensure_access_rights_populate(session):
    from caerp.models.populate import populate_access_rights, populate_groups

    populate_access_rights(session)
    session.flush()
    populate_groups(session)
    session.flush()


def create_default_access_right_group_relationship(session):
    from caerp.models.user.access_right import AccessRight
    from caerp.models.user.group import Group
    from caerp.consts.access_rights import ACCESS_RIGHTS

    EA_RIGHTS = [
        right
        for right in ACCESS_RIGHTS.values()
        if right["account_type"] in ["equipe_appui"]
    ]

    # On modifie les groupes existants
    admin = Group._find_one("admin")
    if admin:
        admin.account_type = "equipe_appui"
        for right in EA_RIGHTS:
            access_right = session.execute(
                select(AccessRight).filter(AccessRight.name == right["name"])
            ).scalar_one()
            admin.access_rights.append(access_right)
        session.merge(admin)

    manager = Group._find_one("manager")
    if manager:
        manager.account_type = "equipe_appui"
        manager.editable = True
        manager.default_for_account_type = True
        manager.label = "Membre de l'équipe d'appui"

        for right in EA_RIGHTS:
            if "configuration" not in right["tags"]:
                access_right = session.execute(
                    select(AccessRight).filter(AccessRight.name == right["name"])
                ).scalar_one()
                manager.access_rights.append(access_right)
        session.merge(manager)

    contractor = Group._find_one("contractor")
    if contractor:
        contractor.account_type = "entrepreneur"
        contractor.default_for_account_type = True
        contractor.editable = True
        session.merge(contractor)

    from caerp.consts.users import PREDEFINED_GROUPS

    for group_def in PREDEFINED_GROUPS:
        if group_def["account_type"] == "equipe_appui":
            continue
        group = Group._find_one(group_def["name"])
        if group:
            group.editable = group_def["editable"]
            group.account_type = group_def["account_type"]
            group.label = group_def["label"]
            for right in group_def["access_rights"]:
                access_right = session.execute(
                    select(AccessRight).filter(AccessRight.name == right["name"])
                ).scalar_one()
                group.access_rights.append(access_right)
            session.merge(group)
    # ### end Alembic commands ###


def rename_file_acls(session):
    # On renomme les permissions stockées directement en BDD
    op.execute("Update node set _acl=REPLACE(_acl,  'view.file', 'context.view_file')")
    op.execute("Update node set _acl=REPLACE(_acl,  'edit.file', 'context.edit_file')")
    op.execute(
        "Update node set _acl=REPLACE(_acl,  'delete.file', 'context.delete_file')"
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    set_primary_groups_on_login(session)
    ensure_access_rights_populate(session)
    create_default_access_right_group_relationship(session)

    rename_file_acls(session)
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_schema()
    migrate_datas()


def downgrade():
    op.drop_column("login", "account_type")
    op.drop_column("groups", "account_type")
    op.add_column("groups", sa.Column("primary", sa.Boolean(), nullable=True))
    op.drop_table("groups_access_rights")
    op.drop_table("access_rights")
