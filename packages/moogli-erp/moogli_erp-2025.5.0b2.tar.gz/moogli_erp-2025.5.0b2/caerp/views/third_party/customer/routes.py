import os

from caerp.views import caerp_add_route

COMPANY_CUSTOMERS_ROUTE = "/companies/{id}/customers"
CUSTOMER_ITEM_ROUTE = "/customers/{id}"
CUSTOMER_ITEM_RGPD_CLEAN_ROUTE = "/customers/{id}/rgpd_clean"
CUSTOMER_ITEM_BUSINESS_ROUTE = "/customers/{id}/businesses"
CUSTOMER_ITEM_ESTIMATION_ROUTE = "/customers/{id}/estimations"
CUSTOMER_ITEM_INVOICE_ROUTE = "/customers/{id}/invoices"
CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE = CUSTOMER_ITEM_INVOICE_ROUTE + ".{extension}"
CUSTOMER_ITEM_EXPENSES_ROUTE = os.path.join(CUSTOMER_ITEM_ROUTE, "expenses")
COMPANY_CUSTOMERS_ADD_ROUTE = os.path.join(COMPANY_CUSTOMERS_ROUTE, "add")

API_COMPANY_CUSTOMERS_ROUTE = "/api/v1/companies/{id}/customers"
CUSTOMER_REST_ROUTE = "/api/v1/customers/{id}"
CUSTOMER_STATUS_LOG_ROUTE = "/api/v1/customers/{id}/statuslogentries"
CUSTOMER_STATUS_LOG_ITEM_ROUTE = "/api/v1/customers/{eid}/statuslogentries/{id}"


def includeme(config):
    caerp_add_route(
        config,
        API_COMPANY_CUSTOMERS_ROUTE,
        traverse="/companies/{id}",
    )
    caerp_add_route(config, CUSTOMER_ITEM_ROUTE, traverse="/customers/{id}")

    for route in (
        CUSTOMER_REST_ROUTE,
        CUSTOMER_ITEM_BUSINESS_ROUTE,
        CUSTOMER_ITEM_ESTIMATION_ROUTE,
        CUSTOMER_ITEM_INVOICE_ROUTE,
        CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        CUSTOMER_ITEM_EXPENSES_ROUTE,
        CUSTOMER_STATUS_LOG_ROUTE,
        CUSTOMER_ITEM_RGPD_CLEAN_ROUTE,
    ):
        caerp_add_route(
            config,
            route,
            traverse="/customers/{id}",
        )

    caerp_add_route(
        config, CUSTOMER_STATUS_LOG_ITEM_ROUTE, traverse="/statuslogentries/{id}"
    )

    for route in (COMPANY_CUSTOMERS_ROUTE, COMPANY_CUSTOMERS_ADD_ROUTE):
        caerp_add_route(config, route, traverse="/companies/{id}")

    config.add_route(
        "customers.csv", r"/company/{id:\d+}/customers.csv", traverse="/companies/{id}"
    )
