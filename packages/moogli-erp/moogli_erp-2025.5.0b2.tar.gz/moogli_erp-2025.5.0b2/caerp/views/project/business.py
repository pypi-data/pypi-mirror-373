"""
Views related to Businesses
"""
from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    distinct,
)
from caerp_base.models.base import DBSESSION
from caerp.models.project import Business, Project
from caerp.utils.widgets import Link
from caerp.views import (
    BaseListView,
    TreeMixin,
)
from caerp.views.company.routes import (
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_INVOICE_ADD_ROUTE,
)
from caerp.views.project.routes import (
    PROJECT_ITEM_BUSINESS_ROUTE,
)
from caerp.views.business.routes import (
    BUSINESS_ITEM_ROUTE,
)
from caerp.views.project.lists import ProjectListView


class ProjectBusinessListView(BaseListView, TreeMixin):
    """
    View listing businesses
    """

    add_template_vars = (
        "stream_actions",
        "add_estimation_url",
        "add_invoice_url",
        "tva_display_mode",
        "tva_on_margin",
    )
    schema = None
    sort_columns = {
        "created_at": Business.created_at,
        "name": Business.name,
    }
    default_sort = "name"
    default_direction = "asc"
    route_name = PROJECT_ITEM_BUSINESS_ROUTE
    item_route_name = BUSINESS_ITEM_ROUTE

    @property
    def title(self):
        return "Affaires du dossier {0}".format(self.current().name)

    def current_id(self):
        if hasattr(self.context, "project_id"):
            return self.context.project_id
        else:
            return self.context.id

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.current_id())

    @property
    def add_estimation_url(self):
        return self.request.route_path(
            COMPANY_ESTIMATION_ADD_ROUTE,
            id=self.context.company_id,
            _query={"project_id": self.context.id},
        )

    @property
    def add_invoice_url(self):
        return self.request.route_path(
            COMPANY_INVOICE_ADD_ROUTE,
            id=self.context.company_id,
            _query={"project_id": self.context.id},
        )

    @property
    def tva_on_margin(self) -> bool:
        # Note that in case of a folder mixing tva on margin / regular tva, we would return True.
        # This is considered acceptable edge case.
        for business in self.context.businesses:
            if business.business_type.tva_on_margin:
                return True
        return self.context.project_type.is_tva_on_margin()

    @property
    def tva_display_mode(self):
        if self.context.mode == "ttc" or self.tva_on_margin:
            return "ttc"
        else:
            return "ht"

    def current(self):
        if hasattr(self.context, "project"):
            return self.context.project
        else:
            return self.context

    def query(self):
        query = DBSESSION().query(distinct(Business.id), Business)
        query = query.filter_by(project_id=self.current().id)
        return query

    def stream_actions(self, item):
        yield Link(self._get_item_url(item), "Voir/Modifier", icon="pen", css="icon")


def includeme(config):
    config.add_tree_view(
        ProjectBusinessListView,
        parent=ProjectListView,
        renderer="caerp:templates/project/business_list.mako",
        layout="project",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )
