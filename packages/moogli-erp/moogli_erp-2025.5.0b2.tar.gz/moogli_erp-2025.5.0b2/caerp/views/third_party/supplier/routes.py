from caerp.views import caerp_add_route


COMPANY_SUPPLIERS_API_ROUTE = "/api/v1/companies/{id}/suppliers"
SUPPLIER_ITEM_API_ROUTE = "/api/v1/suppliers/{id}"
SUPPLIER_ITEM_STATUSLOGENTRY_API_ROUTE = "/api/v1/suppliers/{id}/statuslogentries"
SUPPLIER_STATUSLOGENTRY_ITEM_API_ROUTE = "/api/v1/suppliers/{eid}/statuslogentries/{id}"


def includeme(config):
    config.add_route(
        "supplier",
        "/suppliers/{id}",
        traverse="/suppliers/{id}",
    )
    config.add_route(
        "supplier_running_orders",
        "/suppliers/{id}/running_orders",
        traverse="/suppliers/{id}",
    )

    config.add_route(
        "supplier_invoiced_orders",
        "/suppliers/{id}/invoiced_orders",
        traverse="/suppliers/{id}",
    )
    config.add_route(
        "supplier_invoices",
        "/suppliers/{id}/invoices",
        traverse="/suppliers/{id}",
    )

    config.add_route(
        "supplier_expenselines",
        "/suppliers/{id}/expenselines",
        traverse="/suppliers/{id}",
    )

    caerp_add_route(
        config,
        COMPANY_SUPPLIERS_API_ROUTE,
        traverse="/companies/{id}",
    )
    caerp_add_route(
        config,
        SUPPLIER_ITEM_API_ROUTE,
        traverse="/suppliers/{id}",
    )
    caerp_add_route(
        config,
        SUPPLIER_ITEM_STATUSLOGENTRY_API_ROUTE,
        traverse="/suppliers/{id}",
    )
    caerp_add_route(
        config,
        SUPPLIER_STATUSLOGENTRY_ITEM_API_ROUTE,
        traverse="/statuslogentries/{id}",
    )

    config.add_route(
        "company_suppliers",
        r"/company/{id:\d+}/suppliers",
        traverse="/companies/{id}",
    )

    config.add_route(
        "suppliers.csv", r"/company/{id:\d+}/suppliers.csv", traverse="/companies/{id}"
    )
    for i in range(2):
        index = i + 1
        route_name = "company_suppliers_import_step%d" % index
        path = r"/company/{id:\d+}/suppliers/import/%d" % index
        config.add_route(route_name, path, traverse="/companies/{id}")
