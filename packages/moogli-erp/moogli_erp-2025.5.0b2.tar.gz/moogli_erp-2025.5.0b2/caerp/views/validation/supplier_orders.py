import logging
import colander

from caerp.consts.permissions import PERMISSIONS
from caerp_base.models.base import DBSESSION
from caerp.forms.validation.supplier_orders import get_list_schema
from caerp.models.company import Company
from caerp.models.supply import SupplierOrder
from caerp.models.third_party.supplier import Supplier
from caerp.views import BaseListView


logger = logging.getLogger(__name__)


class SuppliersOrdersValidationView(BaseListView):
    title = "Commandes fournisseurs en attente de validation"
    sort_columns = dict(
        status_date=SupplierOrder.status_date,
        company=Company.name,
        name=SupplierOrder.name,
        supplier=Supplier.name,
        cae_percentage=SupplierOrder.cae_percentage,
    )
    add_template_vars = ("title",)
    default_sort = "status_date"
    default_direction = "desc"

    def get_schema(self):
        return get_list_schema(self.request)

    def query(self):
        query = DBSESSION().query(SupplierOrder)
        query = query.outerjoin(SupplierOrder.company)
        query = query.outerjoin(SupplierOrder.supplier)
        query = query.filter(SupplierOrder.status == "wait")
        return query

    def filter_company(self, query, appstruct):
        company_id = appstruct.get("company_id")
        if company_id and company_id not in ("", -1, colander.null):
            query = query.filter(
                SupplierOrder.company_id == company_id,
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
                SupplierOrder.supplier_id == supplier_id,
            )
        return query

    def filter_doctype(self, query, appstruct):
        type_ = appstruct.get("doctype")
        if type_ in (
            "supplier_order",
            "internalsupplier_order",
        ):
            query = query.filter(SupplierOrder.type_ == type_)
        return query


def includeme(config):
    config.add_route("validation_supplier_orders", "validation/supplier_orders")
    config.add_view(
        SuppliersOrdersValidationView,
        route_name="validation_supplier_orders",
        renderer="validation/supplier_orders.mako",
        permission=PERMISSIONS["global.validate_supplier_order"],
    )
    config.add_admin_menu(
        parent="validation",
        order=3,
        label="Commandes fournisseurs",
        href="/validation/supplier_orders",
        permission=PERMISSIONS["global.validate_supplier_order"],
    )
