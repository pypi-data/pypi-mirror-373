import venusian

from pyramid.config import Configurator
from pyramid.request import Request
from typing import List

from caerp.interfaces import IDataQueriesRegistry


def register_dataquery(config: Configurator, dataquery_class: object):
    """
    Register a dataquery into the "dataqueries" registry

    :param obj config: The pyramid config object
    :param obj dataquery_class: The class object of the dataquery to register
    """
    config.registry.getUtility(IDataQueriesRegistry).append(dataquery_class)


def _find_dataqueries_by_name(request: Request, name: str) -> list:
    """
    Return registered dataqueries with given name

    :param obj request: The current pyramid request
    :param str name: Name of the dataqueries to find in registry
    """
    return [
        dataquery
        for dataquery in request.registry.getUtility(IDataQueriesRegistry)
        if dataquery.name == name
    ]


def get_dataquery(request: Request, dataquery_name: str) -> object or None:
    """
    Return the dataquery object from its name

    :param obj request: The current pyramid request
    :param str dataquery_name: The name of the dataquery to get
    """
    matched_dataqueries = _find_dataqueries_by_name(request, dataquery_name)
    return matched_dataqueries[0](request) if matched_dataqueries else None


def has_dataquery(request: Request, dataquery_name: str) -> bool:
    """
    Check if a dataquery has been registred by its name

    :param obj request: The current pyramid request
    :param str dataquery_name: The name of the dataquery to check
    """
    return len(_find_dataqueries_by_name(request, dataquery_name)) > 0


def get_dataqueries(request: Request) -> List[str]:
    """
    Return the list of all registered dataqueries

    :param obj request: The current pyramid request
    """
    return request.registry.getUtility(IDataQueriesRegistry)


class dataquery_class(object):
    """
    A class decorator for automatic dataqueries registration

    Eg:
    @dataquery_class()
    class MyDataQuery(BaseDataQuery):
        ...
    """

    def __call__(self, wrapped):
        def callback(context, name, dataquery_class):
            config = context.config.with_package(info.module)
            # Attache la requête au registre
            config.register_dataquery(dataquery_class)

        info = venusian.attach(wrapped, callback, category="dataqueries")
        return wrapped


def includeme(config: Configurator):
    config.registry.registerUtility([], IDataQueriesRegistry)
    config.add_directive("register_dataquery", register_dataquery)
    config.add_request_method(has_dataquery)
    config.add_request_method(get_dataqueries)
    config.add_request_method(get_dataquery)
