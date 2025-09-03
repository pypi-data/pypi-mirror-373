import logging
import datetime
import colander

from caerp.consts.permissions import PERMISSIONS
from dateutil.relativedelta import relativedelta
from caerp.export.utils import write_file_to_request
from caerp.export.excel import XlsExporter
from caerp.export.ods import OdsExporter
from caerp.forms.management.payments import get_list_schema
from caerp.models.task import Payment
from caerp.views import BaseListView


logger = logging.getLogger(__name__)


class PaymentsManagementView(BaseListView):
    """
    Tableau de suivi des encaissements
    """

    schema = get_list_schema()
    use_paginate = False
    default_sort = "date"
    sort_columns = {"date": "date"}
    filter_button_label = "Changer"
    filter_button_icon = False
    filter_button_css = "btn btn-primary"

    title = "Suivi des encaissements"

    def query(self):
        return Payment.query().order_by(Payment.date)

    def filter_period(self, query, appstruct):
        year = appstruct.get("year")
        if year not in (None, colander.null):
            self.year = year
        else:
            self.year = datetime.date.today().year
        month = appstruct.get("month")
        if month not in (None, colander.null):
            self.month = month
        else:
            self.month = datetime.date.today().month
        period_start = datetime.date(int(year), int(month), 1)
        period_end = period_start + relativedelta(months=1)
        period_end = period_end - relativedelta(days=1)
        query = query.filter(Payment.date.between(period_start, period_end))
        return query

    def filter_year(self, query, appstruct):
        return self.filter_period(query, appstruct)

    def filter_month(self, query, appstruct):
        return self.filter_period(query, appstruct)

    def more_template_vars(self, response_dict):
        response_dict["export_xls_url"] = self.request.route_path(
            "management_payments_export",
            extension="xls",
            _query=self.request.GET,
        )
        response_dict["export_ods_url"] = self.request.route_path(
            "management_payments_export",
            extension="ods",
            _query=self.request.GET,
        )
        return response_dict


class PaymentsManagementXlsView(PaymentsManagementView):
    """
    Export du tableau de suivi des encaissements au format XLSX
    """

    _factory = XlsExporter

    @property
    def filename(self):
        return "suivi_encaissements_{}_{}.{}".format(
            self.year,
            self.month,
            self.request.matchdict["extension"],
        )

    def _init_writer(self):
        writer = self._factory()
        headers = [
            "Date",
            "Enseigne",
            "Facture",
            "Client",
            "Mode",
            "Montant",
            "Taux TVA",
            "Montant TVA",
        ]
        writer.add_headers(headers)
        return writer

    def _build_return_value(self, schema, appstruct, query):
        writer = self._init_writer()
        writer._datas = []
        total_amount = 0
        total_tva_amount = 0
        for data in query.all():
            row_data = [
                data.date.date().strftime("%d/%m/%Y"),
                data.invoice.company.full_label,
                data.invoice.official_number,
                data.invoice.customer.label,
                data.mode,
                data.amount / 100000,
                data.tva.ratio,
                round(data.get_tva_amount() / 100000, 2),
            ]
            writer.add_row(row_data)
            total_amount += data.amount
            total_tva_amount += data.get_tva_amount()
        row_total = [
            "TOTAL",
            "",
            "",
            "",
            "",
            total_amount / 100000,
            "",
            round(total_tva_amount / 100000, 2),
        ]
        writer.add_row(row_total, options={"highlighted": True})
        write_file_to_request(self.request, self.filename, writer.render())
        return self.request.response


class PaymentsManagementOdsView(PaymentsManagementXlsView):
    """
    Export du tableau de suivi des kms au format ODS
    """

    _factory = OdsExporter


def includeme(config):
    config.add_route("management_payments", "management/payments")
    config.add_route("management_payments_export", "management/payments.{extension}")
    config.add_view(
        PaymentsManagementView,
        route_name="management_payments",
        renderer="management/payments.mako",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        PaymentsManagementXlsView,
        route_name="management_payments_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        PaymentsManagementOdsView,
        route_name="management_payments_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_admin_menu(
        parent="management",
        order=0,
        label="Encaissements",
        href="/management/payments",
    )
