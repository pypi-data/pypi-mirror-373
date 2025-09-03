"""
    Customer views
"""
import logging
import colander

from sqlalchemy import func, select
from sqlalchemy import (
    or_,
    not_,
)
from sqlalchemy.orm import undefer_group

from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.models.task import Task
from caerp.models.third_party.customer import Customer
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.third_party.customer import (
    get_list_schema,
)
from caerp.views import (
    BaseListView,
    BaseCsvView,
    TreeMixin,
)
from caerp.views.project.routes import (
    COMPANY_PROJECTS_ROUTE,
)

from .routes import (
    COMPANY_CUSTOMERS_ROUTE,
    COMPANY_CUSTOMERS_ADD_ROUTE,
    CUSTOMER_ITEM_ROUTE,
)


logger = log = logging.getLogger(__name__)


class CustomersListTools:
    """
    Customer list tools
    """

    title = "Liste des clients"
    schema = get_list_schema()
    sort_columns = {
        "label": Customer.label,
        "code": Customer.code,
        "lastname": Customer.lastname,
        "created_at": Customer.created_at,
    }
    default_sort = "max_date"
    default_direction = "desc"

    def query(self):
        query = self.request.dbsession.query(Customer)
        return query

    def sort_by_max_date(self, query, appstruct):
        sort_direction = appstruct.get("direction", self.default_direction)
        subq = (
            select([func.max(Task.date).label("maxdate")])
            .where(Task.customer_id == Customer.id)
            .scalar_subquery()
        )
        return query.order_by(getattr(subq, sort_direction)())

    def filter_company(self, query, appstruct):
        company = self.context
        return query.filter(Customer.company_id == company.id)

    def filter_archived(self, query, appstruct):
        archived = appstruct.get("archived", False)
        logger.debug("In filter archived")
        logger.debug(archived)
        if archived in (False, colander.null, "false"):
            query = query.filter(Customer.archived == False)
        return query

    def filter_type(self, query, appstruct):
        individual = appstruct.get("individual")
        company = appstruct.get("company")
        internal = appstruct.get("internal")
        if not individual:
            query = query.filter(not_(Customer.type == "individual"))
        if not company:
            query = query.filter(not_(Customer.type == "company"))
        if not internal:
            query = query.filter(not_(Customer.type == "internal"))
        return query

    def filter_name_or_contact(self, records, appstruct):
        """
        Filter the records by customer name or contact lastname
        """
        search = appstruct.get("search")
        if search:
            records = records.filter(
                or_(
                    Customer.label.like("%" + search + "%"),
                    Customer.lastname.like("%" + search + "%"),
                )
            )
        return records


class CustomersListView(CustomersListTools, BaseListView, TreeMixin):
    """
    Customer listing view
    """

    add_template_vars = (
        "stream_actions",
        "title",
        "stream_main_actions",
        "stream_more_actions",
        "stream_max_date",
    )
    route_name = COMPANY_CUSTOMERS_ROUTE
    item_route_name = CUSTOMER_ITEM_ROUTE

    @property
    def tree_url(self):
        """
        Compile the url to be used in the breadcrumb for this view

        The context can be either :

        - A Company
        - A Customer
        - A Task
        """
        if isinstance(self.context, Company):
            cid = self.context.id
        elif isinstance(self.context, Customer):
            cid = self.context.company_id
        elif hasattr(self.context, "project"):
            cid = self.context.project.company_id
        else:
            raise Exception(
                "Can't retrieve company id for breadcrumb generation %s"
                % (self.context,)
            )
        return self.request.route_path(self.route_name, id=cid)

    def stream_main_actions(self):
        if self.request.has_permission(PERMISSIONS["context.add_customer"]):
            yield Link(
                self.request.route_path(
                    COMPANY_CUSTOMERS_ADD_ROUTE, id=self.context.id
                ),
                label="Ajouter<span class='no_mobile'>&nbsp;un client</span>",
                icon="plus",
                css="btn btn-primary",
                title="Ajouter un nouveau client",
            )
            yield Link(
                self.request.route_path(
                    "company_customers_import_step1", id=self.context.id
                ),
                label="Importer<span class='no_mobile'>&nbsp;des clients</span>",
                title="Importer des clients",
                icon="file-import",
                css="btn icon",
            )

    def stream_more_actions(self):
        if self.request.has_permission(PERMISSIONS["context.add_customer"]):
            yield Link(
                self.request.route_path("customers.csv", id=self.context.id),
                label="<span class='no_mobile no_tablet'>Exporter les clients au format&nbsp;"
                "</span>CSV",
                title="Exporter les clients au format CSV",
                icon="file-csv",
                css="btn icon_only_mobile",
            )

    def stream_actions(self, customer):
        """
        Return action buttons with permission handling
        """

        if self.request.has_permission(
            PERMISSIONS["context.delete_customer"], customer
        ):
            yield POSTButton(
                self.request.route_path(
                    CUSTOMER_ITEM_ROUTE,
                    id=customer.id,
                    _query=dict(action="delete"),
                ),
                "Supprimer",
                title="Supprimer définitivement ce client",
                icon="trash-alt",
                css="negative",
                confirm="Êtes-vous sûr de vouloir supprimer ce client ?",
            )

        yield Link(
            self.request.route_path(CUSTOMER_ITEM_ROUTE, id=customer.id),
            "Voir ce client",
            title="Voir ou modifier ce client",
            icon="arrow-right",
        )

        yield Link(
            self.request.route_path(
                COMPANY_PROJECTS_ROUTE,
                id=customer.company.id,
                _query=dict(action="add", customer=customer.id),
            ),
            "Ajouter un dossier",
            title="Ajouter un dossier pour ce client",
            icon="folder-plus",
        )

        if customer.archived:
            label = "Désarchiver"
        else:
            label = "Archiver"
        yield POSTButton(
            self.request.route_path(
                CUSTOMER_ITEM_ROUTE,
                id=customer.id,
                _query=dict(action="archive"),
            ),
            label,
            icon="archive",
        )

    def stream_max_date(self, customer):

        return self.request.dbsession.execute(
            select(func.max(Task.date)).where(Task.customer_id == customer.id)
        ).scalar()


class CustomersCsv(CustomersListTools, BaseCsvView):
    """
    Customer csv view
    """

    model = Customer

    @property
    def filename(self):
        return "clients.csv"

    def query(self):
        company = self.request.context
        query = Customer.query().options(undefer_group("edit"))
        return query.filter(Customer.company_id == company.id)


def includeme(config):
    config.add_view(
        CustomersListView,
        route_name=COMPANY_CUSTOMERS_ROUTE,
        renderer="customers/list.mako",
        request_method="GET",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )

    config.add_view(
        CustomersCsv,
        route_name="customers.csv",
        request_method="GET",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
