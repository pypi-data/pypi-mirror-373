import logging
import colander

from caerp.consts.permissions import PERMISSIONS
from caerp_base.models.base import DBSESSION
from caerp.forms.validation.supplier_invoices import get_list_schema
from caerp.models.company import Company
from caerp.models.supply import SupplierInvoice
from caerp.models.third_party.supplier import Supplier
from caerp.views import BaseListView


logger = logging.getLogger(__name__)


class SuppliersInvoicesValidationView(BaseListView):
    title = "Factures fournisseurs en attente de validation"
    sort_columns = dict(
        status_date=SupplierInvoice.status_date,
        company=Company.name,
        date=SupplierInvoice.date,
        remote_invoice_number=SupplierInvoice.remote_invoice_number,
        supplier=Supplier.name,
        cae_percentage=SupplierInvoice.cae_percentage,
    )
    add_template_vars = ("title",)
    default_sort = "status_date"
    default_direction = "desc"

    def get_schema(self):
        return get_list_schema(self.request)

    def query(self):
        query = DBSESSION().query(SupplierInvoice)
        query = query.outerjoin(SupplierInvoice.company)
        query = query.outerjoin(SupplierInvoice.supplier)
        query = query.filter(SupplierInvoice.status == "wait")
        return query

    def filter_company(self, query, appstruct):
        company_id = appstruct.get("company_id")
        if company_id and company_id not in ("", -1, colander.null):
            query = query.filter(
                SupplierInvoice.company_id == company_id,
            )
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            query = query.filter(Company.antenne_id == antenne_id)
        return query

    def filter_follower(self, query, appstruct):
        follower_id = appstruct.get("follower_id")
        if follower_id not in (None, colander.null):
            query = query.filter(Company.follower_id == follower_id)
        return query

    def filter_supplier(self, query, appstruct):
        supplier_id = appstruct.get("supplier_id")
        if supplier_id and supplier_id not in ("", -1, colander.null):
            query = query.filter(
                SupplierInvoice.supplier_id == supplier_id,
            )
        return query

    def filter_doctype(self, query, appstruct):
        type_ = appstruct.get("doctype")
        if type_ in (
            "supplier_invoice",
            "internalsupplier_invoice",
        ):
            query = query.filter(SupplierInvoice.type_ == type_)
        return query


def includeme(config):
    config.add_route("validation_supplier_invoices", "validation/supplier_invoices")
    config.add_view(
        SuppliersInvoicesValidationView,
        route_name="validation_supplier_invoices",
        renderer="validation/supplier_invoices.mako",
        permission=PERMISSIONS["global.validate_supplier_invoice"],
    )
    config.add_admin_menu(
        parent="validation",
        order=4,
        label="Factures fournisseurs",
        href="/validation/supplier_invoices",
        permission=PERMISSIONS["global.validate_supplier_invoice"],
    )
