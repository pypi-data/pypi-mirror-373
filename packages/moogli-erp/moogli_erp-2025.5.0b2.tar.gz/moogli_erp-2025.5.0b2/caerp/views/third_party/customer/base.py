import logging

from caerp.utils.widgets import (
    ButtonLink,
    ViewLink,
)

from .routes import COMPANY_CUSTOMERS_ROUTE, CUSTOMER_ITEM_ROUTE

logger = logging.getLogger(__name__)


def populate_actionmenu(request, context=None):
    """
    populate the actionmenu for the different views (list/add/edit ...)
    """
    company_id = request.context.get_company_id()
    request.actionmenu.add(get_list_view_btn(company_id))
    if context is not None and context.__name__ == "customer":
        request.actionmenu.add(get_view_btn(context.id))


def get_list_view_btn(id_):
    return ButtonLink("Liste des clients", path=COMPANY_CUSTOMERS_ROUTE, id=id_)


def get_view_btn(customer_id):
    return ViewLink(
        "Revenir au client", "company.view", path=CUSTOMER_ITEM_ROUTE, id=customer_id
    )


def get_edit_btn(customer_id):
    return ViewLink(
        "Modifier",
        "context.edit_customer",
        path=CUSTOMER_ITEM_ROUTE,
        id=customer_id,
        _query=dict(action="edit"),
    )


def get_customer_url(
    request,
    customer=None,
    _query={},
    suffix="",
    api=False,
    _anchor=None,
    absolute=False,
):
    if customer is None:
        customer = request.context

    # La route pour le client est toujours nommée "customer" et non
    #  "/customers/{id}"
    if not suffix and not api:
        route = CUSTOMER_ITEM_ROUTE
    else:
        # On est donc obligé de traiter le cas où on veut construire d'autres route
        # dynamiquement à part
        route = CUSTOMER_ITEM_ROUTE

    if suffix:
        route += suffix

    if api:
        route = "/api/v1%s" % route

    params = dict(id=customer.id, _query=_query)
    if _anchor is not None:
        params["_anchor"] = _anchor

    if absolute:
        method = request.route_url
    else:
        method = request.route_path
    return method(route, **params)
