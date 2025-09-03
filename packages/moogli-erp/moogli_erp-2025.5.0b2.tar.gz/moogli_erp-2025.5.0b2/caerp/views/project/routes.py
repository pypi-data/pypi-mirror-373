import os
from caerp.views import caerp_add_route


COMPANY_PROJECTS_ROUTE = "/companies/{id}/projects"
PROJECT_ROUTE = "/projects"
PROJECT_ITEM_ROUTE = os.path.join(PROJECT_ROUTE, "{id}")
PROJECT_ITEM_ESTIMATION_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "estimations")
PROJECT_ITEM_PHASE_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "phases")
PROJECT_ITEM_GENERAL_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "general")
PROJECT_ITEM_INVOICE_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "invoices")
PROJECT_ITEM_INVOICE_EXPORT_ROUTE = PROJECT_ITEM_INVOICE_ROUTE + ".{extension}"
PROJECT_ITEM_BUSINESS_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "businesses")
PROJECT_ITEM_FILE_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "files")
PROJECT_ITEM_FILE_ZIP_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "files.zip")
PROJECT_ITEM_ADD_FILE_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "addfile")
PROJECT_ITEM_EXPENSES_ROUTE = os.path.join(PROJECT_ITEM_ROUTE, "expenses")
PHASE_ROUTE = "/phases"
PHASE_ITEM_ROUTE = os.path.join(PHASE_ROUTE, "{id}")

PROJECT_ITEM_API = "/api/v1/projects/{id}"
API_COMPANY_PROJECTS = "/api/v1/companies/{id}/projects"
PROJECT_TYPE_ITEM_API = "/api/v1/project_types/{id}"
PROJECT_TYPE_COMPANY_COLLECTION_API = "/api/v1/companies/{id}/project_types"
BUSINESS_TYPE_ITEM_API = "/api/v1/business_types/{id}"
BUSINESS_TYPE_COMPANY_COLLECTION_API = "/api/v1/companies/{id}/business_types"
PHASE_COLLECTION_API = "/api/v1/projects/{id}/phases"
PROJECT_TREE_API = "/api/v1/projects/{id}/tree"


def includeme(config):
    caerp_add_route(
        config,
        COMPANY_PROJECTS_ROUTE,
        traverse="/companies/{id}",
    )
    for route in (
        PROJECT_ITEM_ROUTE,
        PROJECT_ITEM_PHASE_ROUTE,
        PROJECT_ITEM_GENERAL_ROUTE,
        PROJECT_ITEM_ESTIMATION_ROUTE,
        PROJECT_ITEM_INVOICE_ROUTE,
        PROJECT_ITEM_INVOICE_EXPORT_ROUTE,
        PROJECT_ITEM_BUSINESS_ROUTE,
        PROJECT_ITEM_FILE_ROUTE,
        PROJECT_ITEM_FILE_ZIP_ROUTE,
        PROJECT_ITEM_ADD_FILE_ROUTE,
        PROJECT_ITEM_EXPENSES_ROUTE,
        PROJECT_ITEM_API,
        PHASE_COLLECTION_API,
        PROJECT_TREE_API,
    ):
        caerp_add_route(config, route, traverse="/projects/{id}")

    caerp_add_route(
        config,
        PHASE_ITEM_ROUTE,
        traverse="/phases/{id}",
    )
    for route in (
        API_COMPANY_PROJECTS,
        PROJECT_TYPE_COMPANY_COLLECTION_API,
        BUSINESS_TYPE_COMPANY_COLLECTION_API,
    ):
        caerp_add_route(
            config,
            route,
            traverse="/companies/{id}",
        )
    caerp_add_route(
        config,
        PROJECT_TYPE_ITEM_API,
        traverse="/project_types/{id}",
    )
    caerp_add_route(
        config,
        BUSINESS_TYPE_ITEM_API,
        traverse="/business_types/{id}",
    )
