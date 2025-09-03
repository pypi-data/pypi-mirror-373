import os

from sqlalchemy import desc
from sqlalchemy.orm import load_only

from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import CompanyActivity

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
from caerp.views.admin.main.companies import (
    COMPANIES_INDEX_URL,
    MainCompaniesIndex,
)

COLLECTION_ROUTE = os.path.join(COMPANIES_INDEX_URL, "company_activity_types")
ITEM_ROUTE = os.path.join(COLLECTION_ROUTE, "{id}")


class CompanyActivityListView(AdminCrudListView):
    title = "Domaine d’activité des enseignes dans MoOGLi"
    description = "Configurer les domaines d’activité proposés lors de la \
création d’une enseigne dans MoOGLi"

    route_name = COLLECTION_ROUTE
    item_route_name = ITEM_ROUTE
    columns = [
        "Libellé",
    ]
    factory = CompanyActivity

    def stream_columns(self, item):
        yield item.label

    def stream_actions(self, item):
        yield Link(self._get_item_url(item), "Voir/Modifier", icon="pen", css="icon")
        if item.active:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Désactiver",
                title="Ce domaine d'activité ne sera plus proposé dans les "
                "formulaires",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Activer",
                icon="lock-open",
                css="icon",
            )
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
        items = self.request.dbsession.query(CompanyActivity).options(
            load_only(
                "label",
            )
        )
        items = items.order_by(desc(self.factory.active))
        return items


class CompanyActivityAddView(BaseAdminAddView):
    title = "Ajouter"
    route_name = COLLECTION_ROUTE
    factory = CompanyActivity
    schema = get_admin_configurable_option_schema(CompanyActivity)


class CompanyActivityEditView(BaseAdminEditView):
    route_name = ITEM_ROUTE
    factory = CompanyActivity
    schema = get_admin_configurable_option_schema(CompanyActivity)

    @property
    def title(self):
        return "Modifier ce domain d'activité '{0}'".format(self.context.label)


class CompanyActivityDisableView(BaseAdminDisableView):
    """
    View for CompanyActivity disable/enable
    """

    route_name = ITEM_ROUTE


class CompanyActivityDeleteView(BaseAdminDeleteView):
    """
    View for CompanyActivity deletion
    """

    route_name = ITEM_ROUTE


def includeme(config):
    config.add_route(COLLECTION_ROUTE, COLLECTION_ROUTE)
    config.add_route(ITEM_ROUTE, ITEM_ROUTE, traverse="/configurable_options/{id}")
    config.add_admin_view(
        CompanyActivityListView,
        parent=MainCompaniesIndex,
        renderer="admin/crud_list.mako",
        permission=PERMISSIONS["global.config_company"],
    )
    config.add_admin_view(
        CompanyActivityAddView,
        parent=CompanyActivityListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
        permission=PERMISSIONS["global.config_company"],
    )
    config.add_admin_view(
        CompanyActivityEditView,
        parent=CompanyActivityListView,
        renderer="admin/crud_add_edit.mako",
        permission=PERMISSIONS["global.config_company"],
    )
    config.add_admin_view(
        CompanyActivityDisableView,
        parent=CompanyActivityListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
        permission=PERMISSIONS["global.config_company"],
    )
    config.add_admin_view(
        CompanyActivityDeleteView,
        parent=CompanyActivityListView,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
        permission=PERMISSIONS["global.config_company"],
    )
