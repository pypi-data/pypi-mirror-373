from caerp.consts.permissions import PERMISSIONS
from caerp.models.project import Project
from caerp.views import BaseView, TreeMixin
from caerp.views.project.project import ProjectListView
from caerp.views.project.routes import PROJECT_ITEM_EXPENSES_ROUTE


class ProjectLinkedExpensesView(BaseView, TreeMixin):

    route_name = PROJECT_ITEM_EXPENSES_ROUTE
    add_template_vars = ("title",)

    @property
    def title(self):
        project = self.context
        return "Achats liés au dossier {}".format(project.name)

    def __call__(self):
        self.populate_navigation()
        return dict(title=self.title)


def includeme(config):
    config.add_tree_view(
        ProjectLinkedExpensesView,
        parent=ProjectListView,
        renderer="caerp:templates/project/expenses.mako",
        permission=PERMISSIONS["company.view"],
        layout="project",
        context=Project,
    )
