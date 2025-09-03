import os


COLLECTION_ROUTE = "/api/v1/notifications"
ITEM_ROUTE = os.path.join(COLLECTION_ROUTE, "{id}")
ACTION_ROUTE = os.path.join(ITEM_ROUTE, "{action_name}")


def includeme(config):
    config.add_route(COLLECTION_ROUTE, COLLECTION_ROUTE)
    for route in (ITEM_ROUTE, ACTION_ROUTE):
        config.add_route(route, route, traverse="/notifications/{id}")
