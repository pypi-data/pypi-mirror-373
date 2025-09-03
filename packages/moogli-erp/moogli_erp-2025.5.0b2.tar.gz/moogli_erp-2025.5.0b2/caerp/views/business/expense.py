from caerp.consts.permissions import PERMISSIONS
from caerp.models.project import Business
from caerp.views import BaseView, TreeMixin
from caerp.views.project.project import ProjectEntryPointView
from caerp.views.business.routes import BUSINESS_ITEM_EXPENSES_ROUTE


class BusinessLinkedExpensesView(BaseView, TreeMixin):

    route_name = BUSINESS_ITEM_EXPENSES_ROUTE
    add_template_vars = ("title",)

    @property
    def title(self):
        business = self.context
        return "Achats liés à l'affaire {}".format(business.name)

    def __call__(self):
        self.populate_navigation()
        return dict(title=self.title)


def includeme(config):
    config.add_tree_view(
        BusinessLinkedExpensesView,
        parent=ProjectEntryPointView,
        renderer="caerp:templates/business/expenses.mako",
        permission=PERMISSIONS["company.view"],
        layout="business",
        context=Business,
    )
