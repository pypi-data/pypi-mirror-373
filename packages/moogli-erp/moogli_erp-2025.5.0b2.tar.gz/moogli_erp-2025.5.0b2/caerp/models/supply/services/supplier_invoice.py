from sqlalchemy import func

from caerp_base.models.base import DBSESSION
from caerp.models.services.mixins import BusinessLinkedServiceMixin


class SupplierInvoiceService:
    @staticmethod
    def import_lines(dest_line_factory, src_obj, dest_obj, source_id_attr=None):
        """
        Copies SupplierOrder lines into SupplierInvoice.

        Use DuplicableMixin data. Lines are add-edto DB by function.

        :param src_obj SupplierOrder or SupplierInvoice:
        :param dest_obj SupplierInvoice:
        :param dest_line_factory:  target's line factory
        :param source_id_attr: optional name of the attribute of dest_obj that
          holds src_obj id

        :param src_instance SupplierOrder:
        """
        for src_line in src_obj.lines:
            dest_line = src_line.duplicate(
                factory=dest_line_factory,
                supplier_invoice_id=dest_obj.id,
            )
            if source_id_attr is not None:
                setattr(dest_line, source_id_attr, src_line.id)
            DBSESSION().add(dest_line)

    @staticmethod
    def filter_by_year(cls, query, year):
        return query.filter(func.year(cls.date) == year)


class SupplierInvoiceLineService(BusinessLinkedServiceMixin):
    def total_expense(
        cls,
        query_filters=[],
        column_name="total_ht",
        tva_on_margin: bool = None,
    ) -> int:
        from caerp.models.expense.types import ExpenseType

        query = cls.query()

        if tva_on_margin is not None:
            query = query.join(cls.expense_type)
            # include or exclude
            query = query.filter(ExpenseType.tva_on_margin == tva_on_margin)

        if query_filters:
            query = query.filter(*query_filters)
        return sum(getattr(e, column_name) for e in query.all())
