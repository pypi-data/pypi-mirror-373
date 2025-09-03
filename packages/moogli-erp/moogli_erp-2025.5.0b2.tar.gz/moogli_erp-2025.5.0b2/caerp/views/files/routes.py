import os

from caerp.views import API_ROUTE


FILES = "/files"
FILE_ITEM = os.path.join(FILES, "{id}")
FILE_PNG_ITEM = os.path.join(FILES, "{id}.png")

NODE_FILE_ROUTE = "/nodes/{id}/addfile"

FILE_API = os.path.join(API_ROUTE, "files")
FILE_ITEM_API = os.path.join(FILE_API, "{id}")
NODE_FILE_API = os.path.join(API_ROUTE, "nodes", "{id}", "files")
# Default public route. Access restrictions can be
# added via the object's _acl property.
PUBLIC_ITEM = "/public/{name}"


def includeme(config):
    """
    Add module's related routes
    """
    config.add_route(FILE_API, FILE_API)
    config.add_route(FILE_PNG_ITEM, FILE_PNG_ITEM, traverse="/files/{id}")
    config.add_route(FILE_ITEM, FILE_ITEM, traverse="/files/{id}")
    config.add_route(NODE_FILE_ROUTE, NODE_FILE_ROUTE, traverse="/nodes/{id}")
    config.add_route(PUBLIC_ITEM, PUBLIC_ITEM, traverse="/configfiles/{name}")
    config.add_route(FILE_ITEM_API, FILE_ITEM_API, traverse="/files/{id}")
    config.add_route(NODE_FILE_API, NODE_FILE_API, traverse="/nodes/{id}")
