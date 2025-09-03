import os
from caerp.views import API_ROUTE


CATALOG_ROUTE = "/companies/{id}/sale_products"

COMPANY_API_ROUTE = os.path.join(API_ROUTE, "companies/{id}/")

CATEGORY_API_ROUTE = os.path.join(COMPANY_API_ROUTE, "sale_product_categories")
CATEGORY_ITEM_API_ROUTE = os.path.join(CATEGORY_API_ROUTE, "{cid}")

CATALOG_API_ROUTE = os.path.join(COMPANY_API_ROUTE, "sale_products_catalog")
PRODUCT_API_ROUTE = os.path.join(COMPANY_API_ROUTE, "sale_products")
PRODUCT_ITEM_API_ROUTE = os.path.join(PRODUCT_API_ROUTE, "{pid}")

WORK_ITEMS_API_ROUTE = os.path.join(PRODUCT_ITEM_API_ROUTE, "work_items")
WORK_ITEMS_ITEM_API_ROUTE = os.path.join(WORK_ITEMS_API_ROUTE, "{wid}")

STOCK_OPERATIONS_API_ROUTE = os.path.join(PRODUCT_ITEM_API_ROUTE, "stock_operations")
STOCK_OPERATIONS_ITEM_API_ROUTE = os.path.join(STOCK_OPERATIONS_API_ROUTE, "{soid}")


def includeme(config):
    config.add_route(CATEGORY_API_ROUTE, CATEGORY_API_ROUTE, traverse="/companies/{id}")
    config.add_route(
        CATEGORY_ITEM_API_ROUTE,
        CATEGORY_ITEM_API_ROUTE,
        traverse="/sale_categories/{cid}",
    )

    config.add_route(CATALOG_ROUTE, CATALOG_ROUTE, traverse="/companies/{id}")
    config.add_route(CATALOG_API_ROUTE, CATALOG_API_ROUTE, traverse="/companies/{id}")
    config.add_route(PRODUCT_API_ROUTE, PRODUCT_API_ROUTE, traverse="/companies/{id}")
    config.add_route(
        PRODUCT_ITEM_API_ROUTE,
        PRODUCT_ITEM_API_ROUTE,
        traverse="/base_sale_products/{pid}",
    )
    config.add_route(
        WORK_ITEMS_API_ROUTE,
        WORK_ITEMS_API_ROUTE,
        traverse="/base_sale_products/{pid}",
    )
    config.add_route(
        WORK_ITEMS_ITEM_API_ROUTE,
        WORK_ITEMS_ITEM_API_ROUTE,
        traverse="/work_items/{wid}",
    )
    config.add_route(
        STOCK_OPERATIONS_API_ROUTE,
        STOCK_OPERATIONS_API_ROUTE,
        traverse="/base_sale_products/{pid}",
    )
    config.add_route(
        STOCK_OPERATIONS_ITEM_API_ROUTE,
        STOCK_OPERATIONS_ITEM_API_ROUTE,
        traverse="/stock_operations/{soid}",
    )
