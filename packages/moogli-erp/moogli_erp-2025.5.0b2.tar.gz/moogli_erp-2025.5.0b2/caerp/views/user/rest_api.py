"""
Users rest api

Used to get active users list from externals tools
"""
import os
import logging

from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import HTTPBadRequest
from caerp_base.models.base import DBSESSION

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.user.user import get_list_schema
from caerp.utils.rest.apiv1 import Apiv1Resp
from caerp.views import (
    BaseRestView,
    RestListMixinClass,
)
from caerp.views.user.lists import UserFilterTools
from caerp.models.user.login import (
    UserConnections,
    Login,
)
from caerp.models.user.user import User


API_ROOT = "/api/v1"
USERS_API_ROUTE = os.path.join(API_ROOT, "users")
USERS_LIST_ROUTE = os.path.join(USERS_API_ROUTE, "list")
USERS_PUBLIC_ROUTE = os.path.join(USERS_API_ROUTE, "public")


def authentification_check_view(context, request):
    """
    Allows to chek if the accounting authentication is valid without firing any
    additionnal action
    """
    return Apiv1Resp(request)


class UsersListRestView(BaseRestView):
    """
    Handle requests for active users list
    expect json body with {'period': [{"year": "YYYY", "month": "MM"}]}

    Respond to a Http GET request

    Setting caerp.users_api_key=06dda91136f6ad4688cdf6c8fd991696 in the development.ini


    >>> def list_active_users(params=None):
    ...     import time
    ...     import requests
    ...     from hashlib import md5
    ...     timestamp = str(time.time())
    ...     api_key = "06dda91136f6ad4688cdf6c8fd991696"
    ...     secret = "%s-%s" % (timestamp, api_key)
    ...     encoded = md5(secret.encode('utf-8')).hexdigest()
    ...     url = "http://127.0.0.1:8080/api/v1/users/list"
    ...     headers = {
    ...         "Authorization" : "HMAC-MD5 %s" % encoded,
    ...         "Timestamp": timestamp
    ...     }
    ...     resp = requests.get(url, json=params, headers=headers)
    ...     return resp
    >>> resp = list_active_users({'period': [{"year": "2019", "month": "6"}]})
    >>> print resp.json()


    :returns: List of MoOGLi's active users group by month
    """

    def __init__(self, *args, **kwargs):
        BaseRestView.__init__(self, *args, **kwargs)
        self.logger.setLevel(logging.INFO)

    def get_active_users(self):
        self.logger.info("Getting active users list")
        # query = UserConnections.query()
        query = DBSESSION().query(UserConnections)
        query = query.join(User)
        query = query.filter(User.special == 0)
        try:
            period = self.request.json_body["period"]
            self.logger.info("    Period : %s" % period)
            query = query.filter(UserConnections.year == period[0]["year"])
            query = query.filter(UserConnections.month == period[0]["month"])
        except Exception:
            self.logger.exception("Missing parameters")
            raise HTTPBadRequest()
        return query.all()


class GeneralAccountRestList(
    UserFilterTools,
    RestListMixinClass,
    BaseRestView,
):
    list_schema = get_list_schema()

    def filter_login_filter(self, query, appstruct):
        """
        Filter the list on accounts with login only
        """
        query = query.join(User.login)
        login_filter = appstruct.get("login_filter", "active_login")
        if login_filter == "active_login":
            query = query.filter(Login.active == True)  # NOQA : E712
        elif login_filter == "unactive_login":
            query = query.filter(Login.active == False)  # NOQA : E712
        return query

    def _jsonify(self, user):
        json = user.__json__(None)
        json["companies"] = user.active_company_ids
        return json

    def format_collection(self, query):
        return [self._jsonify(user) for (user_id, user) in query]


def includeme(config):
    config.add_route(USERS_API_ROUTE, USERS_API_ROUTE)
    config.add_view(
        authentification_check_view,
        route_name=USERS_API_ROUTE,
        request_method="GET",
        request_param="action=check",
        renderer="json",
        permission=NO_PERMISSION_REQUIRED,
        api_key_authentication="caerp.users_api_key",
    )
    config.add_route(USERS_LIST_ROUTE, USERS_LIST_ROUTE)
    config.add_view(
        UsersListRestView,
        route_name=USERS_LIST_ROUTE,
        attr="get_active_users",
        request_method="GET",
        renderer="json",
        permission=NO_PERMISSION_REQUIRED,
        api_key_authentication="caerp.users_api_key",
    )

    config.add_route(USERS_PUBLIC_ROUTE, USERS_PUBLIC_ROUTE)
    config.add_rest_service(
        factory=GeneralAccountRestList,
        collection_route_name=USERS_PUBLIC_ROUTE,
        collection_view_rights=PERMISSIONS["global.authenticated"],
    )
