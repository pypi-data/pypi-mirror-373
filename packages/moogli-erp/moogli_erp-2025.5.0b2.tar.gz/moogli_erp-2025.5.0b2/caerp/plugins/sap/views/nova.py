from caerp.consts.permissions import PERMISSIONS
from caerp.models.tva import Product
from caerp.plugins.sap.forms.nova import NovaStatsSchema
from caerp.plugins.sap.models.services.nova import NovaStatsService
from caerp.utils.strings import (
    format_amount,
    format_quantity,
)
from caerp.views import (
    TreeMixin,
    BaseListView,
)


def query_to_index(query, index_key: str) -> dict:
    """
    Iters a query and builds an index  based on one of the columns

    :type query: sqla query
    """
    return {getattr(row, index_key): row for row in query.all()}


class NovaStatsView(TreeMixin, BaseListView):
    """
    Helper to fill Nova stats

    This is a quite unconventional use of BaseListView (agregating table)
    """

    schema = NovaStatsSchema()
    title = "Statistiques Nova (SAP)"
    use_paginate = False

    def query(self):
        # The queries and filtering are done without all of BaseListView tooling
        return None

    def _build_return_value(self, schema, appstruct, query):
        template_ctx = super()._build_return_value(schema, appstruct, query)
        year = appstruct["year"]
        year_stats = query_to_index(
            NovaStatsService.query_for_year(year),
            "product_id",
        )
        months_summary = {
            row.month: row for row in NovaStatsService.query_for_monthly_summary(year)
        }
        year_summary = NovaStatsService.query_for_yearly_summary(year).first()

        product_ids = list(year_stats.keys())
        products = Product.query().filter(Product.id.in_(product_ids))

        products_index = {row.id: row.name for row in products.all()}

        products_stats = {
            product.id: query_to_index(
                NovaStatsService.query_for_product(year, product.id),
                "month",
            )
            for product in products
        }

        # Maps to col labels of the sqla query
        metrics = [
            (
                "company_count",
                "Intervenants (1)",
                lambda x: str(x or 0),
            ),
            (
                "invoiced_hours",
                "Heures facturées",
                lambda x: "{} h".format(format_quantity(x or 0)),
            ),
            (
                "customers_count",
                "Clients (3)",
                lambda x: str(x),
            ),
            (
                "reported_total_ht",
                "CA hors taxes (4)",
                lambda x: "{} €".format(format_amount(x or 0, precision=5)),
            ),
        ]
        # template_ctx = self._embed_form(schema, appstruct)
        template_ctx.update(
            {
                "year_stats": year_stats,
                "year_summary": year_summary,
                "months_summary": months_summary,
                "products_stats": products_stats,
                "products_index": products_index,
                "products": products,
                "metrics": metrics,
                "help_message": "",
                "title": self.title,
            }
        )
        return template_ctx


def add_routes(config):
    config.add_route(
        "/sap/nova",
        "/sap/nova",
    )


def includeme(config):
    add_routes(config)
    config.add_tree_view(
        NovaStatsView,
        route_name="/sap/nova",
        permission=PERMISSIONS["global.view_sap"],
        renderer="caerp.plugins.sap:/templates/sap/nova.mako",
    )
