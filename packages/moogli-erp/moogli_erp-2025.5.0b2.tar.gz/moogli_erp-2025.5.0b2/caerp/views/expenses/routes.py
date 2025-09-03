import os

from caerp.views import caerp_add_route


# NB : ici on n'a que les routes pour l'api rest
# NB : les autres routes (views/lists) ont des noms customs

EXPENSES_API_ROUTE = "/api/v1/expenses"
EXPENSE_ITEM_API_ROUTE = os.path.join(EXPENSES_API_ROUTE, "{id}")
EXPENSE_LINES_API_ROUTE = os.path.join(EXPENSE_ITEM_API_ROUTE, "lines")
EXPENSE_KMLINE_API_ROUTE = os.path.join(EXPENSE_ITEM_API_ROUTE, "kmlines")
EXPENSE_LINE_ITEM_API_ROUTE = os.path.join(EXPENSE_LINES_API_ROUTE, "{lid}")
EXPENSE_KMLINE_ITEM_API_ROUTE = os.path.join(EXPENSE_KMLINE_API_ROUTE, "{kid}")
EXPENSE_BOOKMARK_API_ROUTE = "/api/v1/bookmarks"
EXPENSE_BOOKMARK_ITEM_API_ROUTE = os.path.join(EXPENSE_BOOKMARK_API_ROUTE, "{id}")

EXPENSE_STATUS_LOG_ROUTE = os.path.join(EXPENSE_ITEM_API_ROUTE, "statuslogentries")
EXPENSE_STATUS_LOG_ITEM_ROUTE = os.path.join(EXPENSE_STATUS_LOG_ROUTE, "{sid}")


def includeme(config):
    caerp_add_route(config, EXPENSES_API_ROUTE)
    for route in (
        EXPENSE_ITEM_API_ROUTE,
        EXPENSE_LINES_API_ROUTE,
        EXPENSE_KMLINE_API_ROUTE,
        EXPENSE_STATUS_LOG_ROUTE,
    ):
        caerp_add_route(config, route, traverse="/expenses/{id}")

    for route in (
        EXPENSE_LINE_ITEM_API_ROUTE,
        EXPENSE_KMLINE_ITEM_API_ROUTE,
    ):
        caerp_add_route(config, route, traverse="/expenselines/{lid}")

    caerp_add_route(
        config, EXPENSE_STATUS_LOG_ITEM_ROUTE, traverse="/statuslogentries/{sid}"
    )

    caerp_add_route(config, EXPENSE_BOOKMARK_API_ROUTE)
    caerp_add_route(config, EXPENSE_BOOKMARK_ITEM_API_ROUTE)
