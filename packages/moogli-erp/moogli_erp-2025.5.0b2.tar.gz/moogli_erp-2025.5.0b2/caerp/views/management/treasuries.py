import colander
import logging

from sqlalchemy import desc, func

from caerp_base.models.base import DBSESSION
from caerp.consts.permissions import PERMISSIONS
from caerp.export.utils import write_file_to_request
from caerp.export.excel import XlsExporter
from caerp.export.ods import OdsExporter
from caerp.forms.management.treasuries import get_list_schema
from caerp.models.accounting.treasury_measures import TreasuryMeasureGrid
from caerp.models.company import Company
from caerp.utils.accounting import (
    get_financial_year_data,
    get_current_financial_year_value,
)
from caerp.views import BaseListView
from caerp.views.accounting.treasury_measures import TreasuryGridCompute


logger = logging.getLogger(__name__)


class TreasuriesManagementView(BaseListView):
    """
    Tableau de suivi des trésoreries
    """

    title = "Suivi des trésoreries de la CAE"
    schema = get_list_schema()
    use_paginate = False
    active_companies_only = False
    treasury_date = None

    def get_last_treasury_date(self, year=None):
        grid_query = (
            DBSESSION()
            .query(TreasuryMeasureGrid)
            .order_by(desc(TreasuryMeasureGrid.date))
        )
        if year is not None:
            financial_year_data = get_financial_year_data(year)
            grid_query = grid_query.filter(
                TreasuryMeasureGrid.date.between(
                    financial_year_data["start_date"], financial_year_data["end_date"]
                )
            )
        last_grid = grid_query.first()
        return last_grid.date if last_grid else None

    def query(self):
        return TreasuryMeasureGrid.query().join(Company).order_by(Company.name)

    def filter_date(self, query, appstruct):
        financial_year = appstruct.get("financial_year")
        if financial_year in (None, colander.null):
            financial_year = get_current_financial_year_value()
        self.treasury_date = self.get_last_treasury_date(financial_year)
        query = query.filter(TreasuryMeasureGrid.date == self.treasury_date)
        return query

    def filter_follower_id(self, query, appstruct):
        follower_id = appstruct.get("follower_id")
        if follower_id not in (None, colander.null):
            if follower_id == -2:
                # -2 means no follower configured
                query = query.filter(Company.follower_id == None)
            else:
                query = query.filter(Company.follower_id == follower_id)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            if antenne_id == -2:
                # -2 means no antenne configured
                query = query.filter(Company.antenne_id == None)
            else:
                query = query.filter(Company.antenne_id == antenne_id)
        return query

    def filter_active(self, query, appstruct):
        active_only = appstruct.get("active")
        if active_only not in (None, colander.null, False):
            self.active_companies_only = True
        return query

    def filter_internal(self, query, appstruct):
        no_internal = appstruct.get("internal")
        if no_internal not in (None, colander.null, False):
            query = query.filter(Company.internal == False)
        return query

    def get_treasury_headers(self, treasury_grids):
        treasury_headers = []
        if treasury_grids.count() > 0:
            computed_grid = TreasuryGridCompute(treasury_grids[0])
            for row in computed_grid.rows:
                treasury_headers.append(row[0].label)
        return treasury_headers

    def compute_treasury_grid_values(self, grid):
        values = []
        for row in TreasuryGridCompute(grid).rows:
            values.append(row[1])
        return values

    def _build_return_value(self, schema, appstruct, query):
        treasury_grids = query

        treasury_headers = self.get_treasury_headers(treasury_grids)

        treasury_data = []
        for grid in treasury_grids:
            treasury_ana = grid.company.code_compta
            if not treasury_ana:
                continue
            treasury_companies = Company.get_companies_by_analytical_account(
                treasury_ana, self.active_companies_only
            )
            treasury_values = self.compute_treasury_grid_values(grid)
            if len(treasury_companies) > 0:
                treasury_data.append(
                    (treasury_ana, treasury_companies, treasury_values)
                )

        if schema is not None:
            if self.error is not None:
                form_object = self.error
                form_render = self.error.render()
            else:
                form = self.get_form(schema)
                if appstruct and "__formid__" in self.request.GET:
                    form.set_appstruct(appstruct)
                form_object = form
                form_render = form.render()

        return dict(
            title=self.title,
            form_object=form_object,
            form=form_render,
            nb_results=len(treasury_data),
            treasuries_date=self.treasury_date,
            treasury_headers=treasury_headers,
            treasury_data=treasury_data,
            export_xls_url=self.request.route_path(
                "management_treasuries_export",
                extension="xls",
                _query=self.request.GET,
            ),
            export_ods_url=self.request.route_path(
                "management_treasuries_export",
                extension="ods",
                _query=self.request.GET,
            ),
        )


class TreasuriesManagementXlsView(TreasuriesManagementView):
    """
    Export du tableau de suivi des trésoreries au format XLSX
    """

    _factory = XlsExporter

    @property
    def filename(self):
        return "suivi_tresoreries_{}.{}".format(
            self.treasury_date,
            self.request.matchdict["extension"],
        )

    def _build_return_value(self, schema, appstruct, query):
        writer = self._factory()
        writer._datas = []
        # Récupération des données
        treasury_grids = query
        treasury_headers = self.get_treasury_headers(treasury_grids)
        treasury_data = []
        for grid in treasury_grids:
            treasury_ana = grid.company.code_compta
            if not treasury_ana:
                continue
            treasury_companies = Company.get_companies_by_analytical_account(
                treasury_ana, self.active_companies_only
            )
            treasury_values = self.compute_treasury_grid_values(grid)
            if len(treasury_companies) > 0:
                treasury_data.append(
                    (treasury_ana, treasury_companies, treasury_values)
                )
        # En-têtes
        headers = treasury_headers
        headers.insert(0, "Analytique")
        headers.insert(1, "Enseigne(s)")
        writer.add_headers(headers)
        # Données des enseignes
        for code_ana, companies, treasury_values in treasury_data:
            row_data = [
                code_ana,
                " / ".join(c.name for c in companies),
            ]
            for value in treasury_values:
                row_data.append(value)
            writer.add_row(row_data)
        # Génération du fichier d'export
        write_file_to_request(self.request, self.filename, writer.render())
        return self.request.response


class TreasuriesManagementOdsView(TreasuriesManagementXlsView):
    """
    Export du tableau de suivi des trésoreries au format ODS
    """

    _factory = OdsExporter


def includeme(config):
    config.add_route(
        "management_treasuries",
        "management/treasuries",
    )
    config.add_route(
        "management_treasuries_export", "management/treasuries.{extension}"
    )
    config.add_view(
        TreasuriesManagementView,
        route_name="management_treasuries",
        renderer="management/treasuries.mako",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        TreasuriesManagementXlsView,
        route_name="management_treasuries_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        TreasuriesManagementOdsView,
        route_name="management_treasuries_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_admin_menu(
        parent="management",
        order=0,
        label="Trésoreries",
        href="/management/treasuries",
    )
