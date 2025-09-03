from caerp.views import caerp_add_route

INDICATOR_ROUTE = "/indicators/{id}"
INDICATOR_NODE_COLLECTION_API_ROUTE = "/api/v1/nodes/{id}/indicators"
INDICATOR_ITEM_API_ROUTE = "/api/v1/indicators/{id}"


def includeme(config):
    for route in INDICATOR_ROUTE, INDICATOR_ITEM_API_ROUTE:
        caerp_add_route(config, route, traverse="/indicators/{id}")

    for route in (INDICATOR_NODE_COLLECTION_API_ROUTE,):
        caerp_add_route(
            config,
            route,
            traverse="/nodes/{id}",
        )
