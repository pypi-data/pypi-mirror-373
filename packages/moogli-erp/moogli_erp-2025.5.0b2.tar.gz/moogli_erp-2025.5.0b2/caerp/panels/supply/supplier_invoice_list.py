import functools


from caerp.views.supply.invoices.views import stream_supplier_invoice_actions


class SupplierInvoiceListPanel:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(
        self,
        records,
        stream_actions=None,
        is_admin_view=False,
        is_supplier_view=False,
    ):
        stream_actions = functools.partial(
            stream_supplier_invoice_actions,
            self.request,
        )

        return dict(
            records=records,
            is_admin_view=is_admin_view,
            is_supplier_view=is_supplier_view,
            stream_actions=stream_actions,
            totalht=sum(r.total_ht for r in records),
            totaltva=sum(r.total_tva for r in records),
            totalttc=sum(r.total for r in records),
        )


def includeme(config):
    config.add_panel(
        SupplierInvoiceListPanel,
        "supplier_invoice_list",
        renderer="panels/supply/supplier_invoice_list.mako",
    )
