from caerp_base.models.base import DBSESSION

from .third_party import ThirdPartyService


class SupplierService(ThirdPartyService):
    @classmethod
    def get_orders(
        cls,
        instance,
        waiting_only=False,
        invoiced_only=False,
        pending_invoice_only=False,
        internal=True,
    ):
        from caerp.models.supply.supplier_order import SupplierOrder

        query = DBSESSION().query(SupplierOrder)
        query = query.filter_by(supplier_id=instance.id)
        if waiting_only or pending_invoice_only:
            query = query.filter(
                SupplierOrder.supplier_invoice_id == None,  # noqa
            )
            if pending_invoice_only:
                query = query.filter_by(status="valid")

        if not internal:
            query = query.filter(SupplierOrder.type_ != "internalsupplier_order")
        if invoiced_only:
            query = query.filter(
                SupplierOrder.supplier_invoice_id != None,  # noqa
            )
        return query

    @classmethod
    def count_orders(cls, instance):
        return cls.get_orders(instance).count()

    @classmethod
    def get_invoices(cls, instance):
        from caerp.models.supply.supplier_invoice import SupplierInvoice

        query = DBSESSION().query(SupplierInvoice)
        query = query.filter_by(supplier_id=instance.id)
        return query

    @classmethod
    def get_expenselines(cls, instance):
        from caerp.models.expense.sheet import ExpenseLine, ExpenseSheet

        query = ExpenseLine.query().join(ExpenseSheet)
        query = query.filter(ExpenseLine.supplier_id == instance.id)
        return query

    @classmethod
    def get_general_account(cls, instance, prefix=""):
        result = instance.compte_cg
        if not result:
            result = instance.company.get_general_supplier_account(prefix)
        return result

    @classmethod
    def get_third_party_account(cls, instance, prefix=""):
        result = instance.compte_tiers
        if not result:
            result = instance.company.get_third_party_supplier_account(prefix)
        return result
