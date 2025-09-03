from caerp.consts.permissions import PERMISSIONS
from caerp.models.task import Estimation
from caerp.models.third_party.customer import Customer
from caerp.views.estimations.lists import CompanyEstimationList
from caerp.views import TreeMixin
from caerp.views.company.routes import COMPANY_ESTIMATION_ADD_ROUTE
from .routes import CUSTOMER_ITEM_ESTIMATION_ROUTE
from caerp.views.third_party.customer.lists import (
    CustomersListView,
)


class CustomerEstimationListView(CompanyEstimationList, TreeMixin):
    route_name = CUSTOMER_ITEM_ESTIMATION_ROUTE
    is_global = False
    excluded_fields = (
        "year",
        "customer",
    )
    add_template_vars = CompanyEstimationList.add_template_vars + ("add_url",)

    @property
    def add_url(self):
        return self.request.route_path(
            COMPANY_ESTIMATION_ADD_ROUTE,
            id=self.context.company_id,
            _query={"customer_id": self.context.id},
        )

    @property
    def title(self):
        return "Devis du client {0}".format(self.context.label)

    def _get_company_id(self, appstruct=None):
        """
        Return the current context's company id
        """
        return self.context.company_id

    def filter_customer(self, query, appstruct):
        self.populate_navigation()
        query = query.filter(Estimation.customer_id == self.context.id)
        return query


def includeme(config):
    config.add_tree_view(
        CustomerEstimationListView,
        parent=CustomersListView,
        renderer="customers/estimations.mako",
        layout="customer",
        context=Customer,
        permission=PERMISSIONS["company.view"],
    )
