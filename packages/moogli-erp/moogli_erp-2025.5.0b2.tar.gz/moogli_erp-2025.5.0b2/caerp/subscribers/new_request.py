"""
Log all incoming requests
"""
import logging

from pyramid.events import NewRequest

from caerp.utils.widgets import (
    ActionMenu,
    Navigation,
)
from caerp.i18n import translate

logger = logging.getLogger(__name__)


def log_request(event):
    """
    Log each request
    """
    if "/api/v1/notifications" in event.request.url:
        return
    else:
        logger.info("####################  NEW REQUEST COMING #################")
        logger.info("  + The request object")
        result = event.request.as_bytes(skip_body=True).decode("utf-8")
        result += "\n\n# Paramètres GET de la requête #\n"
        for key, value in list(event.request.GET.items()):
            if key == "password":
                value = "*************"
            result += "{} : {}\n".format(key, value)
        result += "# Paramètres POST de la requête #\n"
        for key, value in list(event.request.POST.items()):
            if "password" in key or "pwd_hash" in key:
                value = "*************"
            result += "{} : {}\n".format(key, value)
        logger.info(result)
        logger.info("  + The session object")
        logger.info(event.request.session)
        logger.info("################### END REQUEST METADATA LOG #############")


def add_request_attributes(event):
    """
    Add usefull tools to the request object
    that may be used inside the views
    """
    request = event.request
    request.translate = translate
    # Old stuff will be deprecated with the time
    request.actionmenu = ActionMenu()
    # Use this one instead
    request.navigation = Navigation()
    request.popups = {}
    if request.params.get("popup", "") != "":
        logger.info("Relative window is a popup")
        request.is_popup = True
    else:
        request.is_popup = False

    request.current_company = None


def includeme(config):
    config.add_subscriber(log_request, NewRequest)
    config.add_subscriber(add_request_attributes, NewRequest)
