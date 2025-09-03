from functools import lru_cache

from caerp_base.models import DBSESSION
from caerp_base.models.utils import non_null_sum
from pyramid.decorator import reify
from caerp.models.task import (
    Payment,
    CancelInvoice,
    TaskLineGroup,
    TaskLine,
    Invoice,
)
from caerp.sql_compute.task.task import TaskLineSqlCompute


class InvoiceSubQueries:
    """
    Group subqueries for lazy loading

    They cannot be defined before sqla mappings are configured.

    We use @reify / @lru_cache to ensure same instance is returned
    """

    @lru_cache(maxsize=None)  # memoize
    def payments_summary(self, year):
        return (
            DBSESSION.query(
                Payment.task_id,
                non_null_sum(Payment.amount).label("ttc"),
            )
            .filter(Payment.year == year)
            .group_by(Payment.task_id)
            .subquery()
        )

    @reify
    def cancelinvoices_summary(self):
        return (
            DBSESSION.query(
                CancelInvoice.invoice_id,
                non_null_sum(CancelInvoice.ttc).label("ttc"),
            )
            .group_by(CancelInvoice.invoice_id)
            .subquery()
        )

    @reify
    def discount_ratio(self):
        # this is not the discount ratio, but it is helping to compute it.
        return (
            DBSESSION.query(
                Invoice.id,
                non_null_sum(TaskLineSqlCompute.total_ht).label("positive_lines_sum"),
            )
            .join(
                TaskLineGroup,
                TaskLineGroup.task_id == Invoice.id,
            )
            .join(
                TaskLine,
                TaskLineGroup.id == TaskLine.group_id,
            )
            .filter(
                TaskLine.cost > 0,
                Invoice.status == "valid",
            )
            .group_by(Invoice.id)
            .subquery()
        )


_subqueries = InvoiceSubQueries()
