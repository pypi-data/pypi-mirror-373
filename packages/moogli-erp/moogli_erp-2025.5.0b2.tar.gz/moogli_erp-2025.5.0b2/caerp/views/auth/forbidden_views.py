import logging
from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    HTTPUnauthorized,
)
from pyramid.security import NO_PERMISSION_REQUIRED

logger = logging.getLogger(__name__)


def forbidden_view(request):
    """
    The forbidden view :
        * handles the redirection to login form
        * return a json dict in case of xhr requests

    :param obj request: The pyramid request object
    """
    logger.debug("We are in a forbidden view")
    login = request.authenticated_userid

    if login:
        logger.warn("An access has been forbidden to '{0}'".format(login))
        if request.is_xhr:
            return_datas = HTTPForbidden()
        else:
            return_datas = {
                "title": "Accès refusé",
            }

    else:
        logger.debug("An access has been forbidden to an unauthenticated user")
        # redirecting to the login page with the current path as param
        nextpage = request.path

        # If it's an api call, we raise HTTPUnauthorized
        if nextpage.startswith("/api"):
            return_datas = HTTPUnauthorized()
        else:
            loc = request.route_url("login", _query=(("nextpage", nextpage),))
            if request.is_xhr:
                return_datas = dict(redirect=loc)
            else:
                return_datas = HTTPFound(location=loc)

    return return_datas


def includeme(config):
    config.add_view(
        forbidden_view,
        context=HTTPForbidden,
        permission=NO_PERMISSION_REQUIRED,
        xhr=True,
        renderer="json",
    )
    config.add_view(
        forbidden_view,
        context=HTTPForbidden,
        permission=NO_PERMISSION_REQUIRED,
        renderer="forbidden.mako",
    )
