"""
    Rest related utilities
"""

from pyramid.httpexceptions import HTTPError, HTTPOk, HTTPTemporaryRedirect
from pyramid.renderers import render
from pyramid.response import Response


# Not used : but kept in case of it's sure
def allowed_methods(*allowed):
    """
    Custom predict checking if the HTTP method in the allowed set.
    It also changes the request.method according to "_method" form parameter
    and "X-HTTP-Method-Override" header
    """

    def predicate(info, request):
        if request.method == "POST":
            request.method = (
                request.POST.get("_method", "").upper()
                or request.headers.get("X-HTTP-Method-Override", "").upper()
                or request.method
            )

        return request.method in allowed

    return predicate


class RestError(HTTPError):
    """
    Rest error, allows to raise errors from rest apis like we would do with
    common http exceptions
    """

    def __init__(self, errors, code=400, status="error"):
        self.code = code
        if not hasattr(errors, "__iter__"):
            errors = [errors]
        body = {"status": status, "errors": errors}
        Response.__init__(self, status=code, body=render("json", body))
        self.detail = str(errors)
        self.content_type = "application/json"

    def __str__(self):
        return "<RestError status=%s body=%s>" % (self.status, self.body)


class RestResponse(HTTPOk):
    def __init__(self, data, status="success", code=200):
        body = {"status": status, "data": data}
        Response.__init__(self, status=code, body=render("json", body))
        self.detail = str(data)
        self.content_type = "application/json"

    def __str__(self):
        return "<RestResponse status=%s body=%s>" % (self.status, self.body)


class Apiv1Resp(dict):
    """
    v1 api Response object

    Returns a dict that should be sent as a json object

        request

            The pyramid request object

        datas

            The datas to be sent in the data key of the result

        status

            The status of the response (one of ['success', 'error'])

    The response contains :

        id
            The id of the request if one is provided by passing the js client
            Check for the '_' key as jquery handles it
            ex:
                $.ajax({..., cache:false, ...});

        api

            The version of the api

        status

            the status of the request

        datas

            The datas sent through the request
            In case of errors, the datas are of the form:
                datas: {'messages': [list of messages]}

    """

    _id_key = "_"
    _version = "1.0"

    def __init__(self, request, datas={}, status="success"):
        dict.__init__(
            self,
            status=status,
            datas=datas,
            id=request.GET.get(self._id_key, ""),
            api=self._version,
        )


class Apiv1Error(Apiv1Resp):
    """
    Error response
    """

    def __init__(self, request, datas=None, messages=None):
        if datas is None:
            datas = {}

        if messages is not None:
            if not hasattr(messages, "__iter__"):
                messages = [messages]
            datas["messages"] = messages

        Apiv1Resp.__init__(self, request, datas=datas, status="error")


class RestJsonRepr:
    """
    :WARNING: Deprecated (only used in holidays)


    BaseJson model wrapper
    Allows to enhance the __json__ method of an sqlalchemy model by
    formatting its output with a colander schema for UI representation
    purpose.
    Takes the json dict and update it with the output of the serialize
    method of the given schema

    :attr schema: colander schema used to preformat datas for ui rendering
    :param model: the model instance we have to format

    :param bind_params: parameters used to bind the schema.
    By default the json renderer passes the request when calling the
    __json__ method of our object, so we use request as default bind_param
    """

    schema = None

    def __init__(self, model, bind_params=None):
        self.model = model
        self.bind_params = bind_params

    def get_schema(self, request):
        """
        Return the binded schema
        """
        if self.bind_params is None:
            bind_params = dict(request=request)
        else:
            bind_params = self.bind_params
        return self.schema.bind(**bind_params)

    def preformat(self, appstruct, request):
        """
        Pass the values through the form schema to preformat some datas for
        ui representation
        (e.g: amounts are represented as floats while they are integers in
        the db)
        """
        if self.schema is not None:
            schema = self.get_schema(request)
            appstruct = schema.serialize(appstruct)
        return appstruct

    def appstruct(self, request):
        """
        Return the appstruct associated to the current schema
        Should be overriden if the model has some relationships
        """
        if hasattr(self.model, "__json__"):
            return self.model.__json__(request)
        else:
            return self.model.appstruct()

    def postformat(self, appstruct):
        """
        allows to postformat the data we want to provide as json
        """
        return appstruct

    def __json__(self, request):
        appstruct = self.appstruct(request)
        result = self.preformat(appstruct, request)
        # We update the appstruct with the value we had expected from the json
        # repr
        for key, value in list(appstruct.items()):
            if key not in result:
                result[key] = value
        result = self.postformat(result)
        return result


def add_rest_service(
    config,
    factory,
    route_name=None,
    edit_rights=None,
    add_rights=None,
    view_rights=None,
    delete_rights=None,
    collection_route_name=None,
    collection_view_rights=None,
    context=None,
    collection_context=None,
    **add_view_kwargs,
):
    """
    Add a rest service

    :param str route_name: The single item route name
    :param cls factory: Class View grouping the methods for Rest views
    :param str edit_rights: The permission needed to execute the edit actions
    :param str add_rights: The permission needed to execute the add actions
    :param str view_rights: The permission needed to get datas
    :param str delete_rights: The permission needed to execute the delete
    actions
    :param str collection_route_name: Specific route name for collection
    related views (default is route_name +'s')
    :param str collection_view_rights: Specific rights for collection view
    :param context: context param passed to the item add_view
    :param collection_context: context param passed to the collection add_view
    :param **add_view_kwargs: passed as-is to all config.add_view() calls

    Add a rest iface associating the factory's methods to the different
    request methods of the routes based on route_name :
        route_name : route name of a single item (items/{id})
        route_name + "s" : route name of the items model (items)
    del - > route_name, DELETE
    put - > route_name, PUT
    get - > route_name, GET
    post - > route_name+"s", POST
    """
    if collection_view_rights is None:
        collection_view_rights = view_rights

    if hasattr(factory, "get") and route_name is not None and view_rights is not None:
        config.add_view(
            factory,
            attr="get",
            route_name=route_name,
            renderer="json",
            request_method="GET",
            permission=view_rights,
            context=context,
            **add_view_kwargs,
        )
    if (
        hasattr(factory, "collection_get")
        and collection_route_name is not None
        and collection_view_rights is not None
    ):
        config.add_view(
            factory,
            attr="collection_get",
            route_name=collection_route_name,
            renderer="json",
            request_method="GET",
            permission=collection_view_rights,
            context=collection_context,
            **add_view_kwargs,
        )
    if (
        hasattr(factory, "post")
        and collection_route_name is not None
        and add_rights is not None
    ):
        config.add_view(
            factory,
            attr="post",
            route_name=collection_route_name,
            renderer="json",
            request_method="POST",
            permission=add_rights,
            context=collection_context,
            **add_view_kwargs,
        )
    if hasattr(factory, "put") and route_name is not None and edit_rights is not None:
        config.add_view(
            factory,
            attr="put",
            route_name=route_name,
            renderer="json",
            request_method="PUT",
            permission=edit_rights,
            context=context,
            **add_view_kwargs,
        )
        config.add_view(
            factory,
            attr="put",
            route_name=route_name,
            renderer="json",
            request_method="PATCH",
            permission=edit_rights,
            context=context,
            **add_view_kwargs,
        )
    if (
        hasattr(factory, "delete")
        and route_name is not None
        and delete_rights is not None
    ):
        config.add_view(
            factory,
            attr="delete",
            route_name=route_name,
            renderer="json",
            request_method="DELETE",
            permission=delete_rights,
            context=context,
            **add_view_kwargs,
        )


def make_redirect_view(route_name, with_id=True):
    """
    Returns a redirect function that redirects to route_name
    :@param with_id: the route expects and id
    """

    def view(request):
        if with_id:
            id_ = request.context.id
            url = request.route_path(route_name, id=id_)
        else:
            url = request.route_path(route_name)
        return HTTPTemporaryRedirect(url)

    return view
