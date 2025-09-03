from typing import Optional, Union
from caerp.models.supply import SupplierInvoice, SupplierOrder


def get_supplier_doc_view_type(document):
    """
    Compute the view/acl label for the given supplier document based on its type_
    """
    type_ = document.type_
    if type_.startswith("internal"):
        type_ = type_.replace("internal", "")
    return type_


def get_supplier_doc_url(
    request,
    doc: Optional[Union[SupplierInvoice, SupplierOrder]] = None,
    _query: Optional[dict] = {},
    suffix: Optional[str] = "",
    api: Optional[bool] = False,
    _anchor: Optional[str] = None,
    absolute: Optional[bool] = False,
):
    """Return the route_name associated to the given document

    :param request: Pyramid request
    :param doc: The given document defaults to None (request.context is used)
    :param _query: url query params, defaults to {}
    :param suffix: Child path to append, defaults to ""
    :param api: Api url ?, defaults to False
    :param _anchor: Anchor (#foo) to add to the url, defaults to None
    :param absolute: Absolute url expected ?, defaults to False
    """
    if doc is None:
        doc = request.context

    type_ = get_supplier_doc_view_type(doc)
    route = "/%ss/{id}" % type_

    if suffix:
        if not suffix.startswith("/"):
            suffix = f"/{suffix}"
        route += suffix

    if api:
        route = "/api/v1%s" % route

    params = dict(id=doc.id, _query=_query)
    if _anchor is not None:
        params["_anchor"] = _anchor

    if absolute:
        method = request.route_url
    else:
        method = request.route_path
    return method(route, **params)
