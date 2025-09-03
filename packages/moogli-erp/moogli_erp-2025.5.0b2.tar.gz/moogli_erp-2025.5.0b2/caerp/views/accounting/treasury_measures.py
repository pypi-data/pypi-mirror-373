import logging
import colander
from sqlalchemy import (
    extract,
    asc,
    desc,
)
from pyramid.decorator import reify

from caerp.consts.permissions import PERMISSIONS
from caerp.models.accounting.operations import AccountingOperationUpload
from caerp.utils.datetimes import format_date
from caerp.utils.widgets import Link
from caerp.models.accounting.treasury_measures import (
    TreasuryMeasureGrid,
    TreasuryMeasure,
    TreasuryMeasureTypeCategory,
    TreasuryMeasureType,
)
from caerp.models.config import Config
from caerp.models.company import Company
from caerp.forms.accounting import (
    get_treasury_measures_list_schema,
    get_upload_treasury_list_schema,
)
from caerp.views import BaseListView
from caerp.views.accounting.routes import (
    UPLOAD_ITEM_ROUTE,
    UPLOAD_ITEM_TREASURY_ROUTE,
    COMPANY_TREASURY_ROUTE,
    TREASURY_ITEM_ROUTE,
)


logger = logging.getLogger(__name__)


class TreasuryGridListView(BaseListView):
    sort_columns = {
        "company": "Custom",
    }
    add_template_vars = (
        "stream_actions",
        "highlight_entry",
    )
    default_sort = "company"
    default_direction = "asc"
    schema = get_upload_treasury_list_schema()
    title = "Liste des états de trésorerie"

    def sort_by_company(self, query, appstruct):
        sort_direction = self._get_sort_direction(appstruct)
        self.logger.debug("  + Direction : %s" % sort_direction)

        query = query.join(TreasuryMeasureGrid.company)
        if sort_direction == "asc":
            func = asc
        else:
            func = desc
        query = query.order_by(func(Company.name))
        return query

    def populate_actionmenu(self, appstruct):
        self.request.navigation.breadcrumb.append(
            Link(
                self.request.route_path(UPLOAD_ITEM_ROUTE, id=self.context.id),
                "Revenir à la liste des écritures",
            )
        )
        self.request.navigation.breadcrumb.append(Link("", self.title))

    def query(self):
        query = (
            TreasuryMeasureGrid.query()
            .filter_by(upload_id=self.context.id)
            .filter_by(date=self.context.updated_at)
        )
        return query

    def filter_company_id(self, query, appstruct):
        company_id = appstruct.get("company_id")
        if company_id not in (colander.null, None):
            query = query.filter_by(company_id=company_id)
        return query

    @property
    def highlight_entry(self):
        result = {}
        config_key = Config.get_value("treasury_measure_ui", default=-1, type_=int)
        if config_key == -1:
            result = TreasuryMeasureType.query().first()
        else:
            result = TreasuryMeasureType.get(config_key)
            if result is None:
                result = TreasuryMeasureType.query().first()
        return result

    def stream_actions(self, item):
        url = self.request.route_path(TREASURY_ITEM_ROUTE, id=item.id)
        return (
            Link(
                url,
                "Voir cet état",
                title="Voir le détail de cet état de trésorerie",
                icon="arrow-right",
                css="icon",
            ),
        )


class TreasuryGridCompute:
    """
    Computation grid collecting the rows of the Treasury and providing an easy
    to use interface used for html rendering

    Collect static database stored datas
    Compute dynamically computed rows
    """

    def __init__(self, grid):
        self.grid = grid
        self.categories = TreasuryMeasureTypeCategory.get_categories()
        self.types = self._type_by_category()
        self.rows = list(self.compile_rows())

        self.label = self._get_date_label(self.grid)

    @staticmethod
    def _get_date_label(grid: TreasuryMeasureGrid) -> str:
        """
        Build a string indicating the date of the data used to build the grid
        and its date of update
        """
        date = "au <strong>{}</strong>".format(format_date(grid.date))
        if grid.upload:
            upload: AccountingOperationUpload = grid.upload
            # Si on est dans le cas d'une remontée fichier, on ajoute la date de
            # mise à jour qui ne correspond pas forcément à la date des données
            if (
                upload.filetype != upload.SYNCHRONIZED_ACCOUNTING
                and upload.updated_at != grid.date
            ):
                date += " (mise à jour le {})".format(format_date(upload.updated_at))
        return date

    def _type_by_category(self):
        """
        Stores TreasuryMeasureType by category (to keep the display
        order)

        :returns: A dict {'category.id': [TreasuryMeasureType]}
        :rtype: dict
        """
        result = dict((category.id, []) for category in self.categories)
        types = TreasuryMeasure.get_measure_types(self.grid.id)
        for type_ in types:
            # Les types donc la catégorie a été désactivé entre temps doit
            # toujours apparaitre
            if type_.category not in self.categories:
                self.categories.append(type_.category)
                result[type_.category.id] = []
            result[type_.category.id].append(type_)
        return result

    def _get_measure(self, type_id):
        """
        Retrieve a measure value for type_id
        """
        result = 0
        measure = self.grid.get_measure_by_type(type_id)
        if measure is not None:
            result = measure.get_value()
        return result

    def compile_rows(self):
        """
        Compile values for Treasury presentation
        """
        for category in self.categories:
            for type_ in self.types[category.id]:
                value = self._get_measure(type_.id)
                yield type_, value


class CompanyTreasuryMeasuresListView(BaseListView):
    add_template_vars = (
        "info_msg",
        "current_grid",
        "stream_actions",
        "last_grid",
        "highlight_entry",
    )
    sort_columns = {
        "date": "date",
    }
    default_sort = "date"
    default_direction = "desc"

    def get_schema(self):
        return get_treasury_measures_list_schema(self.get_company_id())

    @property
    def title(self):
        return f"État de trésorerie"

    @property
    def title_detail(self):
        return f"(enseigne {self.get_company_label()})"

    @property
    def highlight_entry(self):
        result = {}
        if self.current_grid:
            rows = self.current_grid.rows

            if rows:
                result = rows[0]
                config_key = Config.get_value(
                    "treasury_measure_ui", default=-1, type_=int
                )
                if config_key != -1:
                    for item in rows:
                        if item[0].id == config_key:
                            result = item
                            break
        return result

    @property
    def info_msg(self):
        return (
            "Ces données sont déposées à intervalle régulier dans "
            "MoOGLi par l'équipe comptable de votre CAE"
        )

    def get_company_label(self):
        if isinstance(self.context, TreasuryMeasureGrid):
            return self.context.company.name
        else:
            return self.context.name

    def get_company_id(self):
        if isinstance(self.context, TreasuryMeasureGrid):
            code_compta = self.context.company.code_compta
        else:
            code_compta = self.context.code_compta
        return Company.get_id_by_analytical_account(code_compta)

    @reify
    def last_grid(self):
        company_id = self.get_company_id()
        last_grid_model = TreasuryMeasureGrid.last(company_id)
        logger.debug("Last grid : %s" % last_grid_model)
        last_grid = None
        if last_grid_model is not None:
            last_grid = TreasuryGridCompute(last_grid_model)
        return last_grid

    @reify
    def current_grid(self):
        logger.debug("Loading the current grid")
        if isinstance(self.context, TreasuryMeasureGrid):
            current_grid_model = self.context
            current_grid = TreasuryGridCompute(current_grid_model)
        else:
            current_grid = self.last_grid
        return current_grid

    def query(self):
        if not self.request.GET and not isinstance(self.context, TreasuryMeasureGrid):
            return None
        else:
            company_id = self.get_company_id()
            query = TreasuryMeasureGrid.query().filter_by(company_id=company_id)
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year")
        if year not in (None, colander.null, -1):
            query = query.filter(extract("year", TreasuryMeasureGrid.date) == year)
        return query

    def stream_actions(self, item):
        url = self.request.route_path(TREASURY_ITEM_ROUTE, id=item.id)
        return (
            Link(
                url,
                "Voir cet état",
                title="Voir le détail de cet état de trésorerie",
                icon="arrow-right",
                css="icon",
            ),
        )


def includeme(config):
    config.add_view(
        TreasuryGridListView,
        route_name=UPLOAD_ITEM_TREASURY_ROUTE,
        permission=PERMISSIONS["global.generate_accounting_measures"],
        renderer="/accounting/treasury_grids.mako",
    )
    config.add_view(
        CompanyTreasuryMeasuresListView,
        route_name=COMPANY_TREASURY_ROUTE,
        permission=PERMISSIONS["company.view_accounting"],
        renderer="/accounting/treasury_measures.mako",
    )
    config.add_view(
        CompanyTreasuryMeasuresListView,
        route_name=TREASURY_ITEM_ROUTE,
        permission=PERMISSIONS["company.view_accounting"],
        renderer="/accounting/treasury_measures.mako",
    )
    config.add_company_menu(
        parent="accounting",
        order=0,
        label="États de trésorerie",
        route_name=COMPANY_TREASURY_ROUTE,
        route_id_key="company_id",
    )
