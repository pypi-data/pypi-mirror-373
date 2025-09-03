from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.models.task import Estimation
from caerp.models.project.business import Business
from caerp.views import TreeMixin
from caerp.views.business.routes import BUSINESS_ITEM_ESTIMATION_ROUTE
from caerp.views.estimations.lists import CompanyEstimationList
from caerp.views.project.project import ProjectEntryPointView


class BusinessEstimationList(CompanyEstimationList, TreeMixin):
    route_name = BUSINESS_ITEM_ESTIMATION_ROUTE
    add_template_vars = (
        "title",
        "is_admin",
        "with_draft",
        "add_url",
    )
    excluded_fields = (
        "year",
        "customer",
    )

    @property
    def add_url(self):
        return self.request.route_path(
            self.route_name, id=self.request.context.id, _query={"action": "add"}
        )

    @property
    def title(self):
        return "Devis du dossier {0}".format(self.request.context.name)

    def _get_company_id(self, appstruct=None):
        """
        Return the current context's company id
        """
        return self.request.context.project.company_id

    def filter_business(self, query, appstruct):
        self.populate_navigation()
        query = query.filter(Estimation.business_id == self.context.id)
        return query


def add_estimation_view(context, request):
    """
    View used to add an estimation to the current business
    """
    estimation = context.add_estimation(request, request.identity)
    return HTTPFound(request.route_path("/estimations/{id}", id=estimation.id))


def includeme(config):
    config.add_tree_view(
        BusinessEstimationList,
        parent=ProjectEntryPointView,
        renderer="project/estimations.mako",
        permission=PERMISSIONS["company.view"],
        layout="business",
        context=Business,
    )
    config.add_view(
        add_estimation_view,
        route_name=BUSINESS_ITEM_ESTIMATION_ROUTE,
        permission=PERMISSIONS["context.add_estimation"],
        request_param="action=add",
        layout="default",
        request_method="POST",
        require_csrf=True,
        context=Business,
    )
