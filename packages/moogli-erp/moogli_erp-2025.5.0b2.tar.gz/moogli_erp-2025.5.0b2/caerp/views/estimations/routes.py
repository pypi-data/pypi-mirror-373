import os


API_COMPANY_COLLECTION_ROUTE = "/api/v1/companies/{id}/estimations"
API_ADD_ROUTE = os.path.join(API_COMPANY_COLLECTION_ROUTE, "add")
API_COLLECTION_ROUTE = "/api/v1/estimations"
API_ITEM_ROUTE = os.path.join(API_COLLECTION_ROUTE, "{id}")
API_FILE_ROUTE = os.path.join(API_ITEM_ROUTE, "files")

ESTIMATION_COLLECTION_ROUTE = "/estimations"
ESTIMATION_ITEM_ROUTE = "/estimations/{id}"
ESTIMATION_ITEM_GENERAL_ROUTE = "/estimations/{id}/general"
ESTIMATION_ITEM_PREVIEW_ROUTE = "/estimations/{id}/preview"
ESTIMATION_ITEM_FILES_ROUTE = "/estimations/{id}/files"


def includeme(config):
    config.add_route(API_COLLECTION_ROUTE, API_COLLECTION_ROUTE)
    config.add_route(ESTIMATION_COLLECTION_ROUTE, ESTIMATION_COLLECTION_ROUTE)

    for route in API_COMPANY_COLLECTION_ROUTE, API_ADD_ROUTE:
        config.add_route(route, route, traverse="/companies/{id}")

    for route in (
        API_ITEM_ROUTE,
        ESTIMATION_ITEM_ROUTE,
        API_FILE_ROUTE,
        ESTIMATION_ITEM_GENERAL_ROUTE,
        ESTIMATION_ITEM_PREVIEW_ROUTE,
        ESTIMATION_ITEM_FILES_ROUTE,
    ):
        # On assure qu'on matche la route qui finit par un id et pas id.html par exemple
        pattern = r"{}".format(route.replace("id", r"id:\d+"))
        config.add_route(route, pattern, traverse="/tasks/{id}")

    # export routes
    config.add_route("estimations_export", "/estimations.{extension}")
    config.add_route("estimations_details_export", "/estimations_details.{extension}")
    config.add_route(
        "company_estimations_export",
        r"/company/{id:\d+}/estimations.{extension}",
        traverse="/companies/{id}",
    )
    config.add_route(
        "company_estimations_details_export",
        r"/company/{id:\d+}/estimations_details.{extension}",
        traverse="/companies/{id}",
    )
    config.add_route("/estimations/export/pdf", "/estimations/export/pdf")
