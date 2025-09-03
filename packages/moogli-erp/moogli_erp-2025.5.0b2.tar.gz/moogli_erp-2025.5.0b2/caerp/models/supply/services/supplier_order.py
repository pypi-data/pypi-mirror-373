from sqlalchemy import func

from caerp_base.models.base import DBSESSION


class SupplierOrderService:
    @staticmethod
    def query_for_select(
        SupplierOrder,
        valid_only=False,
        company_id=None,
        invoiced=None,
        include_internal=False,
    ):
        query = DBSESSION().query(SupplierOrder.id, SupplierOrder.name)
        if not include_internal:
            query = query.filter(SupplierOrder.type_ != "internalsupplier_order")

        if valid_only:
            query = query.filter_by(status="valid")
        if company_id is not None:
            query = query.filter_by(company_id=company_id)
        if invoiced:
            query = query.filter(SupplierOrder.supplier_invoice_id != None)  # noqa
        elif invoiced == False:  # noqa
            query = query.filter(SupplierOrder.supplier_invoice_id == None)  # noqa
        return query

    @staticmethod
    def import_lines(dest_line_factory, src_obj, dest_obj):
        """
        Copies SupplierOrder lines into dest_obj.

        Use DuplicableMixin data. Lines are added to DB by function.

        :param src_obj SupplierOrder or SupplierInvoice:
        :param dest_obj SupplierInvoice:
        :param dest_line_factory:  target's line factory

        :param src_instance SupplierOrder:
        """
        for src_line in src_obj.lines:
            dest_line = src_line.duplicate(
                factory=dest_line_factory,
                supplier_order_id=dest_obj.id,
            )
            DBSESSION().add(dest_line)

    @staticmethod
    def filter_by_year(cls, query, year):
        return query.filter(func.year(cls.created_at) == year)
