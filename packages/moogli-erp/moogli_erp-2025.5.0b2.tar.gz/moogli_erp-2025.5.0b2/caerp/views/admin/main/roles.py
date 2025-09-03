import itertools
import logging
import os

from sqlalchemy import select, func
from caerp.consts.access_rights import CATEGORIES
from caerp.consts.permissions import PERMISSIONS

from caerp.consts.users import ACCOUNT_TYPES_LABELS
from caerp.forms.admin.main.role import get_add_edit_group_schema
from caerp.models.user import Login, User, Group

from caerp.utils.widgets import Link
from caerp.views.admin.tools import (
    BaseAdminAddView,
    BaseAdminEditView,
    BaseAdminDeleteView,
    AdminCrudListView,
)
from caerp.views.admin.main import (
    MainIndexView,
    MAIN_ROUTE,
)

ROLE_URL = os.path.join(MAIN_ROUTE, "groups")
ROLE_ITEM_URL = os.path.join(ROLE_URL, "{id}")


logger = logging.getLogger(__name__)


class RoleListView(AdminCrudListView):
    title = "Rôles utilisateurs"
    description = (
        "Permet de configurer les rôles utilisateurs ainsi "
        "que les droits d'accès au sein de l’application"
    )
    route_name = ROLE_URL
    item_route_name = ROLE_ITEM_URL
    permission = PERMISSIONS["global.config_cae"]

    def _get_user_count(self, group: Group) -> int:
        return self.dbsession.execute(
            select(func.count("*"))
            .select_from(User)
            .join(User.login)
            .where(Login._groups.contains(group))
            .where(User.special == 0)
        ).scalar_one()

    def _get_access_rights(self, group: Group) -> list:
        """
        Return access_rights grouped by category
        """
        access_rights = [
            access_right.__json__(None) for access_right in group.access_rights
        ]

        def key_func(x):
            return x["category"]

        access_rights.sort(key=key_func)
        result = itertools.groupby(access_rights, key=key_func)
        return dict((category, list(rights)) for category, rights in result)

    def stream_columns(self, item: Group):
        account_types = ACCOUNT_TYPES_LABELS.get(
            item.account_type, "Tous les types de comptes"
        )
        if isinstance(account_types, str):
            account_types = [account_types]
        return {
            "rights": self._get_access_rights(item),
            "user_count": self._get_user_count(item),
            "account_types": account_types,
        }

    def stream_actions(self, item):
        if item.editable:
            yield Link(
                self._get_item_url(item),
                "Modifier",
                icon="pen",
                css="icon",
            )
            yield Link(
                self._get_item_url(item, action="delete"),
                "Supprimer",
                icon="trash-alt",
                css="icon negative",
            )

    def load_items(self):
        return self.dbsession.execute(
            select(Group).order_by(Group.editable, Group.label.asc(), Group.label)
        ).scalars()

    def more_template_vars(self, result):
        result["warn_message"] = (
            """Les droits étiquetés <span class="icon tag caution" """
            """title="Ce droit donne accès à des données personnelles """
            """sensibles">RGPD<span class="screen-reader-text">Ce droit """
            """donne accès à des données personnelles sensibles</span>"""
            """</span> donnent accès à des données """
            """personnelles sensibles. Les utilisateurs """
            """possédant ces droits doivent respecter les procédures """
            """RGPD de la CAE."""
        )
        result["categories"] = CATEGORIES
        return result


class RoleAddView(BaseAdminAddView):
    route_name = ROLE_URL
    title = "Ajouter un rôle utilisateur"
    factory = Group
    msg = "Le rôle a bien été ajouté."
    permission = PERMISSIONS["global.config_cae"]

    def get_schema(self):
        return get_add_edit_group_schema(self.request, edit=False)

    def merge_appstruct(self, appstruct, model):
        if appstruct["account_type"] == "entrepreneur":
            appstruct["access_rights"] = appstruct["access_rights_entrepreneur"]
        elif appstruct["account_type"] == "equipe_appui":
            appstruct["access_rights"] = appstruct["access_rights_equipe_appui"]
        return super().merge_appstruct(appstruct, model)


class RoleEditView(BaseAdminEditView):
    route_name = ROLE_ITEM_URL
    factory = Group
    msg = "Le rôle a bien été modifié."
    permission = PERMISSIONS["global.config_cae"]

    def get_default_appstruct(self):
        result = super().get_default_appstruct()
        result["access_rights_entrepreneur"] = [
            right.id
            for right in self.context.access_rights
            if right.account_type == "entrepreneur"
        ]
        result["access_rights_equipe_appui"] = [
            right.id
            for right in self.context.access_rights
            if right.account_type == "equipe_appui"
        ]
        return result

    @property
    def title(self):
        return "Modifier le rôle '{0}'".format(self.context.label)

    def get_schema(self):
        return get_add_edit_group_schema(self.request, edit=True)


class RoleDeleteView(BaseAdminDeleteView):
    route_name = ROLE_ITEM_URL
    factory = Group
    permission = PERMISSIONS["global.config_cae"]


def includeme(config):
    config.add_route(ROLE_URL, ROLE_URL)
    config.add_route(ROLE_ITEM_URL, ROLE_ITEM_URL, traverse="/groups/{id}")
    config.add_admin_view(
        RoleListView,
        parent=MainIndexView,
        renderer="admin/roles.mako",
    )
    config.add_admin_view(
        RoleAddView,
        parent=RoleListView,
        request_param="action=add",
    )

    config.add_admin_view(
        RoleEditView,
        parent=RoleListView,
    )
    config.add_admin_view(
        RoleDeleteView,
        parent=RoleListView,
        request_param="action=delete",
    )
