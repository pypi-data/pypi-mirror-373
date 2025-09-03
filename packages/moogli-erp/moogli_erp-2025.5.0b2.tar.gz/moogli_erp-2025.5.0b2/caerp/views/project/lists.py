import colander

from pyramid.httpexceptions import HTTPFound
from sqlalchemy import or_
from sqlalchemy import func, select

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.project import get_list_schema

from caerp.models.task import Task
from caerp.models.company import Company
from caerp.models.third_party.customer import Customer
from caerp.models.project.project import Project
from caerp.utils.compat import Iterable
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.views import (
    BaseListView,
    TreeMixin,
)
from caerp.views.company.routes import (
    COMPANY_INVOICE_ADD_ROUTE,
    COMPANY_ESTIMATION_ADD_ROUTE,
)
from caerp.views.third_party.customer.routes import COMPANY_CUSTOMERS_ROUTE
from caerp.views.project.routes import (
    COMPANY_PROJECTS_ROUTE,
    PROJECT_ITEM_ROUTE,
)


def redirect_to_customerslist(request, company):
    """
    Force project page to be redirected to customer page
    """
    request.session.flash(
        "Vous avez été redirigé vers la liste \
des clients"
    )
    request.session.flash(
        "Vous devez créer des clients afin \
de créer de nouveaux dossiers"
    )
    raise HTTPFound(request.route_path(COMPANY_CUSTOMERS_ROUTE, id=company.id))


class ProjectListTools:
    def query(self) -> Iterable[Project]:
        company = self.request.context
        main_query = Project.query()
        main_query = main_query.outerjoin(Project.customers)
        return main_query.filter(Project.company_id == company.id).distinct()

    def filter_archived(self, query, appstruct):
        archived = appstruct.get("archived", False)
        if archived in (False, colander.null):
            query = query.filter(Project.archived == False)
        return query

    def filter_search(self, query, appstruct):
        search = appstruct["search"]
        if search:
            query = query.filter(
                or_(
                    Project.name.like("%" + search + "%"),
                    Project.customers.any(Customer.label.like("%" + search + "%")),
                )
            )
        return query

    def filter_project_type(self, query, appstruct):
        val = appstruct.get("project_type_id")
        if val:
            query = query.filter(Project.project_type_id == val)
        return query


class ProjectListView(ProjectListTools, BaseListView, TreeMixin):
    """
    The project list view is compound of :
        * the list of projects with action buttons (view, delete ...)
        * an action menu with:
            * links
            * an add projectform popup
            * a searchform
    """

    add_template_vars = ("title", "stream_actions", "add_url", "stream_max_date")
    title = "Liste des dossiers"
    schema = get_list_schema()
    default_sort = "max_date"
    default_direction = "desc"
    sort_columns = {
        "name": Project.name,
        "code": Project.code,
        "created_at": Project.created_at,
    }
    route_name = COMPANY_PROJECTS_ROUTE
    item_route_name = PROJECT_ITEM_ROUTE

    @property
    def tree_url(self):
        """
        Compile the url to be used in the breadcrumb for this view

        The context can be either :

        - A Project
        - A Business
        - A Task
        """
        if hasattr(self.context, "get_company_id"):
            cid = self.context.get_company_id()
        elif isinstance(self.context, Company):
            cid = self.context.id
        elif isinstance(self.context, Project):
            cid = self.context.company_id
        elif hasattr(self.context, "project"):
            cid = self.context.project.company_id
        else:
            raise Exception(
                "Can't retrieve company id for breadcrumb generation %s"
                % (self.context,)
            )
        return self.request.route_path(self.route_name, id=cid)

    def query(self):
        company = self.request.context
        # We can't have projects without having customers
        if not company.customers:
            redirect_to_customerslist(self.request, company)
        else:
            return super().query()

    def sort_by_max_date(self, query, appstruct):
        sort_direction = appstruct.get("direction", self.default_direction)
        subq = (
            select([func.max(Task.date).label("maxdate")])
            .where(Task.project_id == Project.id)
            .scalar_subquery()
        )
        return query.order_by(getattr(subq, sort_direction)())

    def stream_actions(self, project):
        """
        Stream actions available for the given project

        :param obj project: A Project instance
        :rtype: generator
        """
        yield Link(self._get_item_url(project), "Voir/Modifier", icon="pen", css="icon")
        if self.request.has_permission(PERMISSIONS["context.add_estimation"]):
            yield Link(
                self.request.route_path(
                    COMPANY_ESTIMATION_ADD_ROUTE,
                    id=project.company_id,
                    _query={"project_id": project.id},
                ),
                "Nouveau devis",
                icon="file-list",
                css="icon",
            )
        if self.request.has_permission(PERMISSIONS["context.add_invoice"]):
            yield Link(
                self.request.route_path(
                    COMPANY_INVOICE_ADD_ROUTE,
                    id=project.company_id,
                    _query={"project_id": project.id},
                ),
                "Nouvelle facture",
                icon="file-invoice-euro",
                css="icon",
            )
        if self.request.has_permission(PERMISSIONS["context.edit_project"], project):
            if project.archived:
                yield POSTButton(
                    self._get_item_url(project, action="archive"),
                    "Désarchiver le dossier",
                    icon="archive",
                    css="icon",
                )
            else:
                yield POSTButton(
                    self._get_item_url(project, action="archive"),
                    "Archiver le dossier",
                    icon="archive",
                    css="icon",
                )
        if self.request.has_permission(PERMISSIONS["context.delete_project"], project):
            yield POSTButton(
                self._get_item_url(project, action="delete"),
                "Supprimer",
                icon="trash-alt",
                confirm="Êtes-vous sûr de vouloir supprimer ce dossier ?",
                css="icon negative",
            )

    @property
    def add_url(self):
        return self.request.route_path(
            COMPANY_PROJECTS_ROUTE, id=self.context.id, _query={"action": "add"}
        )

    def stream_max_date(self, project):
        return self.request.dbsession.execute(
            select(func.max(Task.date)).where(Task.project_id == project.id)
        ).scalar()


def includeme(config):
    config.add_tree_view(
        ProjectListView,
        renderer="project/list.mako",
        request_method="GET",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    config.add_company_menu(
        parent="sale",
        order=0,
        label="Dossiers",
        route_name=COMPANY_PROJECTS_ROUTE,
        route_id_key="company_id",
        routes_prefixes=[PROJECT_ITEM_ROUTE],
    )
