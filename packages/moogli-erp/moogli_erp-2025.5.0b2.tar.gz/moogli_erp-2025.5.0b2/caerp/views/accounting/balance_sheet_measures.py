import datetime
import colander
import logging

from pyramid.decorator import reify
from sqlalchemy import extract

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.accounting import get_balance_sheet_measures_list_schema
from caerp.models.accounting.balance_sheet_measures import (
    BalanceSheetMeasureGrid,
    BalanceSheetMeasure,
    ActiveBalanceSheetMeasureType,
    PassiveBalanceSheetMeasureType,
)
from caerp.models.company import Company
from caerp.utils.datetimes import format_date
from caerp.views import BaseListView
from caerp.views.accounting.routes import COMPANY_BALANCE_SHEET_ROUTE

logger = logging.getLogger(__name__)


class BalanceSheetGridCompute:
    """
    Computation grid collecting the rows of the Balance Sheet and providing an easy
    to use interface used for html rendering

    Collect static database stored datas
    Compute dynamically computed rows
    """

    def __init__(self, grid):
        self.grid = grid
        self.active_types = self._get_types(True)
        self.passive_types = self._get_types(False)
        self.active_rows = list(self.compile_rows(True))
        self.passive_rows = list(self.compile_rows(False))

        self.label = "Bilan <small>au <strong>{}</strong></small>".format(
            format_date(grid.date)
        )

    def _get_types(self, active):
        """
        Stores TreasuryMeasureType by category (to keep the display
        order)

        :returns: A dict {'category.id': [TreasuryMeasureType]}
        :rtype: dict
        """
        if active:
            measure_type_cls = ActiveBalanceSheetMeasureType
        else:
            measure_type_cls = PassiveBalanceSheetMeasureType

        result = []
        types = BalanceSheetMeasure.get_measure_types(self.grid.id)
        for type_ in types:
            if isinstance(type_, measure_type_cls):
                result.append(type_)
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

    def compile_rows(self, active):
        """
        Compile values for Treasury presentation
        """
        if active:
            types = self.active_types
        else:
            types = self.passive_types

        for type_ in types:
            value = self._get_measure(type_.id)
            yield type_, value


class CompanyBalanceSheetMeasuresListView(BaseListView):
    add_template_vars = (
        "current_grid",
        "last_grid",
    )
    use_paginate = False
    filter_button_label = "Changer"
    filter_button_icon = False
    filter_button_css = "btn btn-primary"
    year = None

    def get_schema(self):
        return get_balance_sheet_measures_list_schema(self.get_company_id())

    @property
    def title(self):
        return f"Bilan"

    @property
    def title_detail(self):
        return f"(enseigne {self.get_company_label()})"

    def get_company_label(self):
        if isinstance(self.context, BalanceSheetMeasureGrid):
            return self.context.company.name
        else:
            return self.context.name

    def get_company_id(self):
        if isinstance(self.context, BalanceSheetMeasureGrid):
            code_compta = self.context.company.code_compta
        else:
            code_compta = self.context.code_compta
        return Company.get_id_by_analytical_account(code_compta)

    @reify
    def last_grid(self):
        company_id = self.get_company_id()
        last_grid_model = BalanceSheetMeasureGrid.last(company_id)
        logger.debug("Last grid : %s" % last_grid_model)
        last_grid = None
        if last_grid_model is not None:
            last_grid = BalanceSheetGridCompute(last_grid_model)
        return last_grid

    @reify
    def current_grid(self):
        logger.debug("Loading the current grid")
        if isinstance(self.context, BalanceSheetMeasureGrid):
            current_grid_model = self.context
            current_grid = BalanceSheetGridCompute(current_grid_model)
        elif self.year:
            company_id = self.get_company_id()
            current_grid_model = BalanceSheetMeasureGrid.get_grid_from_year(
                company_id, self.year
            )
            current_grid = BalanceSheetGridCompute(current_grid_model)
        else:
            current_grid = self.last_grid
        return current_grid

    def query(self):
        if not self.request.GET and not isinstance(
            self.context, BalanceSheetMeasureGrid
        ):
            return None
        else:
            company_id = self.get_company_id()
            query = BalanceSheetMeasureGrid.query().filter_by(company_id=company_id)
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year")
        if year not in (None, colander.null, -1):
            query = query.filter(extract("year", BalanceSheetMeasureGrid.date) == year)
            self.year = year
        else:
            self.year = datetime.date.today().year
        return query


def includeme(config):
    config.add_view(
        CompanyBalanceSheetMeasuresListView,
        route_name=COMPANY_BALANCE_SHEET_ROUTE,
        permission=PERMISSIONS["company.view_accounting"],
        renderer="/accounting/balance_sheet_measures.mako",
    )
    config.add_company_menu(
        parent="accounting",
        order=4,
        label="Bilan",
        route_name=COMPANY_BALANCE_SHEET_ROUTE,
        route_id_key="company_id",
    )
