import colander
import datetime

from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import distinct

from caerp_base.models.base import DBSESSION
from caerp.export.utils import write_file_to_request
from caerp.export.excel import XlsExporter
from caerp.export.ods import OdsExporter
from caerp.forms.management.kms import get_list_schema
from caerp.models.user import User
from caerp.models.expense.sheet import ExpenseSheet, ExpenseKmLine
from caerp.utils.strings import short_month_name
from caerp.views import BaseListView


class KmsManagementView(BaseListView):
    """
    Tableau de suivi des kms
    """

    title = "Suivi des kilomètres par salarié"
    schema = get_list_schema()
    use_paginate = False
    sort_columns = dict(name=User.lastname)

    def get_year(self):
        year = self.appstruct.get("year")
        if year in (None, colander.null):
            year = datetime.date.today().year
        return year

    def get_months(self, year):
        months = []
        for month in range(1, 13):
            months.append((year, month))
        return months

    def get_users_with_kms(self, year):
        """
        Return users with valid expense's kmlines on the given year
        """
        sheets = (
            DBSESSION()
            .query(distinct(ExpenseSheet.user_id))
            .filter(ExpenseSheet.year == year)
            .filter(ExpenseSheet.status == "valid")
            .filter(ExpenseSheet.kmlines.any())
        )
        users_ids = [sheet[0] for sheet in sheets.all()]
        return (
            User.query()
            .filter(User.id.in_(users_ids))
            .order_by(User.lastname, User.firstname)
        )

    def get_user_month_kms_data(self, user_id, year, month):
        """
        Return number of valid kms, associated paid amount, and rate
        for the given user on the given month
        """
        sheets = (
            ExpenseSheet.query()
            .filter(ExpenseSheet.year == year)
            .filter(ExpenseSheet.month == month)
            .filter(ExpenseSheet.user_id == user_id)
            .filter(ExpenseSheet.status == "valid")
            .filter(ExpenseSheet.kmlines.any())
        )
        sheets_id = [sheet.id for sheet in sheets.all()]
        kmlines = (
            ExpenseKmLine.query().filter(ExpenseKmLine.sheet_id.in_(sheets_id)).all()
        )
        kms = sum([line.km for line in kmlines])
        amount = sum([line.ht for line in kmlines])
        rate = round(amount / kms, 3) if kms != 0 else 0
        return kms, amount, rate

    def compute_kms_data(self, users, year):
        """
        Return kms data for the given users for each month of the given year
        """
        kms_data = {}
        for user in users:
            kms_data[user.id] = []
            for year, month in self.get_months(year):
                kms_data[user.id].append(
                    self.get_user_month_kms_data(user.id, year, month) or 0
                )

        return kms_data

    def compute_aggregate_data(self, kms_data):
        """
        Calcule les totaux à partir des données des utilisateurs
        """
        kms_list = []
        aggregate_data = []
        for user_id, user_kms_data in kms_data.items():
            kms_list.append(user_kms_data)
        for month_data in zip(*kms_list):
            month_kms = 0
            month_amount = 0
            for nb_kms, amount, rate in month_data:
                month_kms += nb_kms
                month_amount += amount
            aggregate_data.append((month_kms, month_amount))
        return aggregate_data

    def query(self):
        return self.get_users_with_kms(self.get_year())

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the data expected by the template
        """
        year = self.get_year()
        users = query
        kms_data = self.compute_kms_data(users, year)

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
            year=year,
            months=self.get_months(year),
            users=users,
            kms_data=kms_data,
            aggregate_data=self.compute_aggregate_data(kms_data),
            export_xls_url=self.request.route_path(
                "management_kms_export",
                extension="xls",
                _query=self.request.GET,
            ),
            export_ods_url=self.request.route_path(
                "management_kms_export",
                extension="ods",
                _query=self.request.GET,
            ),
        )


class KmsManagementXlsView(KmsManagementView):
    """
    Export du tableau de suivi des kms au format XLSX
    """

    _factory = XlsExporter

    @property
    def filename(self):
        return "suivi_kms_{}.{}".format(
            self.get_year(),
            self.request.matchdict["extension"],
        )

    def _build_return_value(self, schema, appstruct, query):
        writer = self._factory()
        writer._datas = []
        # Récupération des données
        year = self.get_year()
        users = query
        kms_data = self.compute_kms_data(users, year)
        aggregate_data = self.compute_aggregate_data(kms_data)
        # En-têtes
        headers = []
        headers.append("")
        for year, month in self.get_months(year):
            headers.append(f"{short_month_name(month)} {str(year)[2:]}")
            headers.append("")
        headers.append("TOTAL")
        headers.append("")
        writer.add_headers(headers)
        headers = []
        headers.append("Salarié")
        for year, month in self.get_months(year):
            headers.append("Nb kms")
            headers.append("Taux")
        headers.append("Total kms")
        headers.append("Total remboursé")
        writer.add_headers(headers)
        # Données des kms
        for user in users:
            row_data = []
            row_data.append(user.label)
            total_kms = 0
            total_amount = 0
            for nb_kms, amount, rate in kms_data[user.id]:
                row_data.append(nb_kms / 100)
                row_data.append(rate)
                total_kms += nb_kms
                total_amount += amount
            row_data.append(total_kms / 100)
            row_data.append(total_amount / 100)
            writer.add_row(row_data)
        # Total
        row_total = []
        row_total.append("TOTAL")
        total_kms = 0
        total_amount = 0
        for month_kms, month_amount in aggregate_data:
            row_total.append(month_kms / 100)
            row_total.append("")
            total_kms += month_kms
            total_amount += month_amount
        row_total.append(total_kms / 100)
        row_total.append(total_amount / 100)
        writer.add_row(row_total, options={"highlighted": True})
        # Génération du fichier d'export
        write_file_to_request(self.request, self.filename, writer.render())
        return self.request.response


class KmsManagementOdsView(KmsManagementXlsView):
    """
    Export du tableau de suivi des kms au format ODS
    """

    _factory = OdsExporter


def includeme(config):
    config.add_route("management_kms", "management/kms")
    config.add_route("management_kms_export", "management/kms.{extension}")
    config.add_view(
        KmsManagementView,
        route_name="management_kms",
        renderer="management/kms.mako",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        KmsManagementXlsView,
        route_name="management_kms_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        KmsManagementOdsView,
        route_name="management_kms_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_admin_menu(
        parent="management",
        order=0,
        label="Kilomètres",
        href="/management/kms",
    )
