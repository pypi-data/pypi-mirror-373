"""
    Before Render Subscribers

        + Add tools used in templating

        + Require the main_js js ressource

"""
import logging

from pyramid.events import BeforeRender
from pyramid.threadlocal import get_current_request

from caerp.views.render_api import Api

logger = logging.getLogger(__name__)


def add_translation(event):
    """
    Add a translation func to the templating context
    """
    request = event.get("req")
    if not request:
        request = get_current_request()
    if hasattr(request, "translate"):
        event["_"] = request.translate


def add_api(event):
    """
    Add an api to the templating context
    """
    if event.get("renderer_name", "") != "json":
        request = event["request"]
        api = getattr(request, "api", None)
        if api is None and request is not None:
            api = Api(event["context"], event["request"])
        event["api"] = api


def includeme(config):
    """
    Bind the subscribers to the pyramid events
    """
    for before in (add_translation, add_api):
        config.add_subscriber(before, BeforeRender)
