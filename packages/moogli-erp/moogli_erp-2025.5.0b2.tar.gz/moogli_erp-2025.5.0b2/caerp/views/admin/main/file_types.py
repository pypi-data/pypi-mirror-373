import os

from sqlalchemy.orm import load_only

from caerp.consts.permissions import PERMISSIONS
from caerp.models.files import FileType

from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.admin import get_admin_configurable_option_schema
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminAddView,
    BaseAdminEditView,
    BaseAdminDisableView,
    BaseAdminDeleteView,
)
from caerp.views.admin.main import (
    MAIN_ROUTE,
    MainIndexView,
)

FILE_TYPE_ROUTE = os.path.join(MAIN_ROUTE, "file_types")
FILE_TYPE_ITEM_ROUTE = os.path.join(FILE_TYPE_ROUTE, "{id}")


class FileTypeListView(AdminCrudListView):
    title = "Type de fichiers déposables dans MoOGLi"
    description = "Configurer les types de fichier proposés lors du dépôt de \
fichier dans MoOGLi"

    route_name = FILE_TYPE_ROUTE
    item_route_name = FILE_TYPE_ITEM_ROUTE
    columns = [
        "Libellé",
    ]
    factory = FileType

    permission = PERMISSIONS["global.access_admin"]

    @property
    def help_msg(self):
        from caerp.views.admin.sale.business_cycle.file_types import (
            BUSINESS_FILETYPE_URL,
        )

        return """
    Configurez les types de fichier proposés dans les formulaires de dépôt de
    fichier (notes de dépenses, rendez-vous, dossiers, affaires, devis,
    factures...).<br />
    Ces types sont également utilisés pour requérir des fichiers (par exemple
    les feuilles d'émargement pour les formations).<br />
    Pour cela, vous devez indiquer quel types de fichier sont requis par type
    d'affaires.<br /> <a
    href='{0}'>Configuration générale -> Module Ventes -> Cycle d'affaires ->
    Configuration des fichiers obligatoires/facultatives</a>
    """.format(
            self.request.route_path(BUSINESS_FILETYPE_URL)
        )

    def stream_columns(self, item):
        yield item.label

    def stream_actions(self, item):
        yield Link(
            self._get_item_url(item),
            "Voir ou modifier ce type de document",
            icon="pen",
            css="icon",
        )
        if item.active:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Désactiver",
                title="Désactiver ce type de document : il ne sera plus proposé dans les "
                "formulaires",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Activer ce document pour le proposer dans les formulaires",
                icon="lock-open",
                css="icon",
            )
        if not item.is_used:
            yield POSTButton(
                self._get_item_url(item, action="delete"),
                "Supprimer",
                icon="trash-alt",
                css="icon negative",
            )

    def load_items(self):
        """
        Return the sqlalchemy models representing current queried elements
        :rtype: SQLAlchemy.Query object
        """
        items = self.request.dbsession.query(FileType).options(
            load_only(
                "label",
            )
        )
        items = items.order_by(
            self.factory.active.desc(),
            self.factory.label.asc(),
        )
        return items

    def more_template_vars(self, result):
        result["help_msg"] = self.help_msg
        return result


class FileTypeAddView(BaseAdminAddView):
    title = "Ajouter"
    route_name = FILE_TYPE_ROUTE
    factory = FileType
    schema = get_admin_configurable_option_schema(FileType)


class FileTypeEditView(BaseAdminEditView):
    route_name = FILE_TYPE_ITEM_ROUTE
    factory = FileType
    schema = get_admin_configurable_option_schema(FileType)

    help_msg = FileTypeListView.help_msg

    @property
    def title(self):
        return "Modifier le type de fichier '{0}'".format(self.context.label)


class FileTypeDisableView(BaseAdminDisableView):
    """
    View for FileType disable/enable
    """

    route_name = FILE_TYPE_ITEM_ROUTE

    def on_disable(self):
        for requirement in self.context.query_requirements():
            self.request.dbsession.delete(requirement)


class FileTypeDeleteView(BaseAdminDeleteView):
    """
    View for FileType deletion
    """

    route_name = FILE_TYPE_ITEM_ROUTE


def includeme(config):
    config.add_route(FILE_TYPE_ROUTE, FILE_TYPE_ROUTE)
    config.add_route(
        FILE_TYPE_ITEM_ROUTE,
        FILE_TYPE_ITEM_ROUTE,
        traverse="/configurable_options/{id}",
    )
    config.add_admin_view(
        FileTypeListView,
        parent=MainIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        FileTypeAddView,
        parent=FileTypeListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        FileTypeEditView,
        parent=FileTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        FileTypeDisableView,
        parent=FileTypeListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        FileTypeDeleteView,
        parent=FileTypeListView,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )
