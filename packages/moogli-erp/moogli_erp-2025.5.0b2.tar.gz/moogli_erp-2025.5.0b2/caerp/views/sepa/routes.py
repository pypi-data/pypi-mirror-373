import os

from caerp.views import caerp_add_route

SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE = "/sepa_credit_transfers"
SEPA_CREDIT_TRANSFER_ITEM_ROUTE = os.path.join(
    SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE, "{id}"
)
SEPA_CREDIT_TRANSFER_CANCEL_ROUTE = os.path.join(
    SEPA_CREDIT_TRANSFER_ITEM_ROUTE, "cancel"
)
SEPA_WAITING_PAYMENT_ITEM_ROUTE = "/sepa_waiting_payments/{id}"
API_SEPA_COLLECTION_ROUTE = "/api/v2/sepa_credit_transfers"
API_SEPA_ITEM_ROUTE = os.path.join(API_SEPA_COLLECTION_ROUTE, "{id}")

API_SEPA_WAITING_PAYMENTS_COLLECTION_ROUTE = "/api/v2/sepa_waiting_payments"
API_SEPA_WAITING_PAYMENT_ITEM_ROUTE = os.path.join(
    API_SEPA_WAITING_PAYMENTS_COLLECTION_ROUTE, "{id}"
)


def includeme(config):
    caerp_add_route(config, SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE)
    caerp_add_route(config, API_SEPA_COLLECTION_ROUTE)
    caerp_add_route(
        config, SEPA_CREDIT_TRANSFER_ITEM_ROUTE, traverse="/sepa_credit_transfers/{id}"
    )
    caerp_add_route(
        config,
        SEPA_CREDIT_TRANSFER_CANCEL_ROUTE,
        traverse="/sepa_credit_transfers/{id}",
    )
    caerp_add_route(config, API_SEPA_ITEM_ROUTE, traverse="/sepa_credit_transfers/{id}")
    caerp_add_route(
        config,
        API_SEPA_WAITING_PAYMENTS_COLLECTION_ROUTE,
    )
    caerp_add_route(
        config,
        API_SEPA_WAITING_PAYMENT_ITEM_ROUTE,
        traverse="/sepa_waiting_payments/{id}",
    )
    caerp_add_route(
        config, SEPA_WAITING_PAYMENT_ITEM_ROUTE, traverse="/sepa_waiting_payments/{id}"
    )
