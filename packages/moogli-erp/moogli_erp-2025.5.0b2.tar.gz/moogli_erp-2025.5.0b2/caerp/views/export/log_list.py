"""
Export log list view
"""
import logging
from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import Date

from caerp.forms.export import get_accounting_export_log_schema
from caerp.views import BaseListView
from caerp.views.export.routes import (
    EXPORT_LOG_LIST_ROUTE,
)
from caerp.models.export.accounting_export_log import AccountingExportLogEntry

logger = logging.getLogger(__name__)


class BaseExportLogListView(BaseListView):
    """
    Export log listing view
    """

    title = "Historique des exports comptables"
    schema = get_accounting_export_log_schema()
    sort_columns = {
        "id": AccountingExportLogEntry.id,
        "datetime": AccountingExportLogEntry.datetime,
        "user_id": AccountingExportLogEntry.user_id,
        "export_type": AccountingExportLogEntry.export_type,
    }
    default_sort = "datetime"
    default_direction = "desc"

    def query(self):
        return AccountingExportLogEntry.query()

    def filter_user_id(self, query, appstruct):
        user_id = appstruct.get("user_id")
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query

    def filter_export_type(self, query, appstruct):
        export_type = appstruct.get("export_type")
        if export_type:
            query = query.filter_by(export_type=export_type)
        return query

    def filter_date(self, query, appstruct):
        start = appstruct.get("start_date")
        end = appstruct.get("end_date")
        date_col = AccountingExportLogEntry.datetime.cast(Date)
        if start:
            query = query.filter(date_col >= start)
        if end:
            query = query.filter(date_col <= end)
        return query


def includeme(config):
    config.add_view(
        BaseExportLogListView,
        route_name=EXPORT_LOG_LIST_ROUTE,
        renderer="/export/log_list.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )
