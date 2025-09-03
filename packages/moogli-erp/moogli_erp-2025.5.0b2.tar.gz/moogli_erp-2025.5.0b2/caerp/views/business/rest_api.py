from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.models.project import Project
from caerp.models.project.business import Business
from caerp.models.task import Task

from caerp.views import (
    RestListMixinClass,
    BaseRestView,
)

from caerp.forms.project.business import APIBusinessListSchema
from caerp.views.business.controller import (
    BusinessPy3oController,
)
from caerp.views.business.routes import (
    BUSINESS_ITEM_API,
    COMPANY_ITEM_BUSINESSES_API,
    BUSINESS_TEMPLATE_COLLECTION_API,
)


class BusinessRestView(RestListMixinClass, BaseRestView):
    """
    Businesses REST view, scoped to company

       GET : return list of businesses (company should be provided as context)
    """

    list_schema = APIBusinessListSchema()

    def query(self):
        company = self.request.context
        assert isinstance(company, Company)

        q = Business.query()
        q = q.join(Business.project)
        q = q.filter(Project.company_id == company.id)
        return q

    def filter_search(self, query, appstruct):
        search = appstruct["search"]
        if search:
            query = query.filter(
                Business.name.like("%" + search + "%"),
            )
        return query

    def filter_project_id(self, query, appstruct):
        project_id = appstruct.get("project_id")
        if project_id:
            query = query.filter(Business.project_id == project_id)
        return query

    def filter_customer_id(self, query, appstruct):
        customer_id = appstruct.get("customer_id")
        if customer_id:
            query = query.join(Business.tasks)
            query = query.filter(Task.customer_id == customer_id)
        return query


def business_py3o_list_view(context, request):
    """
    Return a list of available templates for a given business
    """
    controller = BusinessPy3oController(context, request)
    return controller.get_available_templates(context.business_type_id)


def includeme(config):
    config.add_rest_service(
        factory=BusinessRestView,
        route_name=BUSINESS_ITEM_API,
        collection_route_name=COMPANY_ITEM_BUSINESSES_API,
        collection_context=Company,
        collection_view_rights=PERMISSIONS["company.view"],
        context=Business,
        view_rights=PERMISSIONS["company.view"],
    )
    config.add_view(
        business_py3o_list_view,
        route_name=BUSINESS_TEMPLATE_COLLECTION_API,
        permission=PERMISSIONS["company.view"],
        renderer="json",
        context=Business,
    )
