import os
from caerp.views import caerp_add_route

API_COMPANY_COLLECTION_ROUTE = "/api/v1/companies/{id}/invoices"
API_INVOICE_ADD_ROUTE = os.path.join(API_COMPANY_COLLECTION_ROUTE, "add")

API_INVOICE_COLLECTION_ROUTE = "/api/v1/invoices"
API_INVOICE_ITEM_ROUTE = os.path.join(API_INVOICE_COLLECTION_ROUTE, "{id}")
API_INVOICE_FILES_ROUTE = os.path.join(API_INVOICE_ITEM_ROUTE, "files")
API_CINV_COLLECTION_ROUTE = "/api/v1/cancelinvoices"
API_CINV_ITEM_ROUTE = os.path.join(API_CINV_COLLECTION_ROUTE, "{id}")
API_CINV_FILES_ROUTE = os.path.join(API_CINV_ITEM_ROUTE, "files")


INVOICE_COLLECTION_ROUTE = "/invoices"
INVOICE_ITEM_ROUTE = "/invoices/{id}"
INVOICE_ITEM_GENERAL_ROUTE = "/invoices/{id}/general"
INVOICE_ITEM_PREVIEW_ROUTE = "/invoices/{id}/preview"
INVOICE_ITEM_ACCOUNTING_ROUTE = "/invoices/{id}/accounting"
INVOICE_ITEM_PAYMENT_ROUTE = "/invoices/{id}/payment"
INVOICE_ITEM_FILES_ROUTE = "/invoices/{id}/files"


CINV_ITEM_ROUTE = "/cancelinvoices/{id}"
CINV_ITEM_GENERAL_ROUTE = "/cancelinvoices/{id}/general"
CINV_ITEM_PREVIEW_ROUTE = "/cancelinvoices/{id}/preview"
CINV_ITEM_ACCOUNTING_ROUTE = "/cancelinvoices/{id}/accounting"
CINV_ITEM_FILES_ROUTE = "/cancelinvoices/{id}/files"


def includeme(config):
    for route in API_COMPANY_COLLECTION_ROUTE, API_INVOICE_ADD_ROUTE:
        caerp_add_route(config, route, traverse="/companies/{id}")

    for route in (
        API_CINV_COLLECTION_ROUTE,
        API_INVOICE_COLLECTION_ROUTE,
        INVOICE_COLLECTION_ROUTE,
    ):
        config.add_route(route, route)

    for route in (
        API_INVOICE_ITEM_ROUTE,
        API_INVOICE_FILES_ROUTE,
        API_CINV_FILES_ROUTE,
        API_CINV_ITEM_ROUTE,
        INVOICE_ITEM_ROUTE,
        INVOICE_ITEM_GENERAL_ROUTE,
        INVOICE_ITEM_PREVIEW_ROUTE,
        INVOICE_ITEM_ACCOUNTING_ROUTE,
        INVOICE_ITEM_PAYMENT_ROUTE,
        INVOICE_ITEM_FILES_ROUTE,
        CINV_ITEM_ROUTE,
        CINV_ITEM_GENERAL_ROUTE,
        CINV_ITEM_PREVIEW_ROUTE,
        CINV_ITEM_ACCOUNTING_ROUTE,
        CINV_ITEM_FILES_ROUTE,
    ):
        caerp_add_route(config, route, traverse="/tasks/{id}")
