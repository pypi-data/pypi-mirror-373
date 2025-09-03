"""
    MultiRenderer tools to allow multiple renderers to be used with deform
"""
import datetime
import json
import logging

import colander
import deform
import sqlalchemy
from _decimal import Decimal
from deform.template import ZPTRendererFactory
from deform.widget import default_resources
from js.deform import resource_mapping
from pyramid.renderers import JSON, render
from pyramid.threadlocal import get_current_request
from sqla_inspect.export import FORMATTERS_REGISTRY
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric

from caerp.resources import select2_fr, tinymce
from caerp.utils.sys_environment import resource_filename

from .datetimes import format_date, format_datetime
from .export import format_boolean
from .strings import format_quantity
from .sys_environment import package_name

logger = logging.getLogger(__name__)


class CustomRenderer(ZPTRendererFactory):
    """
    Custom renderer needed to ensure our buttons (see utils/widgets.py) can be
    added in the form actions list
    It adds the current request object to the rendering context
    """

    def __call__(self, template_name, **kw):
        if "request" not in kw:
            kw["request"] = get_current_request()
        kw["NAME"] = package_name
        return ZPTRendererFactory.__call__(self, template_name, **kw)


def get_search_path():
    """
    Add MoOGLi's deform custom templates to the loader
    """
    path = resource_filename("templates/deform")
    default_paths = deform.form.Form.default_renderer.loader.search_path
    if path not in default_paths:
        result = (path,) + default_paths
    else:
        result = default_paths
    return result


def set_custom_form_renderer(config):
    """
    Uses an extended renderer that ensures the request object is on our form
    rendering context
    Code largely inspired from pyramid_deform/__init__.py
    """
    # Add translation directories
    config.add_translation_dirs("colander:locale", "deform:locale")
    config.add_static_view("static-deform", "deform:static", cache_max_age=3600)
    # Initialize the Renderer
    from pyramid_deform import translator

    renderer = CustomRenderer(get_search_path(), translator=translator)

    deform.form.Form.default_renderer = renderer


def configure_export():
    """
    Customize sqla_inspect tools
    """
    set_export_formatters()
    set_export_blacklist()
    set_xls_formats()
    customize_tinymce()


def customize_tinymce():

    default_resources["tinymce_js"] = "caerp:static/js/vendors/tinymce/tinymce.min.js"
    resource_mapping["tinymce"] = [
        tinymce,
    ]
    default_resources["select2"] = "caerp:static/js/vendors/select2.min.js"
    resource_mapping["select2"] = select2_fr


def set_export_formatters():
    """
    Globally set export formatters in the sqla_inspect registry
    """
    FORMATTERS_REGISTRY.add_formatter(Date, format_date, "py3o")
    FORMATTERS_REGISTRY.add_formatter(DateTime, format_datetime, "py3o")
    FORMATTERS_REGISTRY.add_formatter(Date, format_date, "csv")
    FORMATTERS_REGISTRY.add_formatter(DateTime, format_date, "csv")
    FORMATTERS_REGISTRY.add_formatter(Boolean, format_boolean)
    FORMATTERS_REGISTRY.add_formatter(Float, format_quantity, "py3o")
    FORMATTERS_REGISTRY.add_formatter(Integer, format_quantity, "py3o")
    FORMATTERS_REGISTRY.add_formatter(Numeric, format_quantity, "py3o")


def set_export_blacklist():
    """
    Globally set an export blacklist
    """
    from sqla_inspect.export import BLACKLISTED_KEYS

    BLACKLISTED_KEYS.extend(
        [
            "_acl",
            "password",
            "parent_id",
            "parent",
            "type_",
            "children",
        ]
    )


def set_xls_formats():
    """
    Globally set the xls formats by datatype
    """
    from sqla_inspect.excel import FORMAT_REGISTRY

    FORMAT_REGISTRY.add_item(Date, "dd/mm/yyyy")
    FORMAT_REGISTRY.add_item(DateTime, "dd/mm/yyyy hh:mm")


def set_json_renderer(config):
    """
    Customize json renderer to allow datetime rendering
    """
    json_renderer = JSON()

    def toisoformat(obj, request):
        return obj.isoformat()

    json_renderer.add_adapter(datetime.datetime, toisoformat)
    json_renderer.add_adapter(datetime.date, toisoformat)
    json_renderer.add_adapter(colander._null, lambda _, r: "null")

    def decimal_to_num(obj, request):
        return float(obj)

    json_renderer.add_adapter(Decimal, decimal_to_num)
    json_renderer.add_adapter(
        sqlalchemy.engine.row.Row, lambda row, request: json.dumps(tuple(row))
    )

    config.add_renderer("json", json_renderer)
    return config


def customize_renderers(config):
    """
    Customize the different renderers
    """
    logger.debug("Setting renderers related hacks")
    # Json
    set_json_renderer(config)
    # deform
    set_custom_form_renderer(config)
    # Exporters
    configure_export()


def set_close_popup_response(
    request, message=None, error=None, refresh=True, force_reload=False
):
    """
    Write directly js code inside the request reponse's body to call popup close

    :param obj request: The Pyramid request object
    :param str message: The information message we want to return
    :param str error: The optionnal error messahe to send
    :param bool refresh: Should a refresh link be included
    :param bool force_reload: Shoud we reload the parent window automatically ?
    """
    options = {"refresh": refresh}

    if message is not None:
        options["message"] = message
    if error is not None:
        options["error"] = error
    if force_reload:
        options["force_reload"] = True

    request.response.text = """<!DOCTYPE html>
    <html><head><title></title></head><body>
    <script type="text/javascript">
    opener.dismissPopup(window, %s);
    </script></body></html>""" % (
        json.dumps(options)
    )
    return request


def get_json_dict_repr(obj, request):
    """
    Call the json renderer on the object and convert it back to a dict to
    simulate the rest_api workflow
    """
    dict_repr = render("json", obj, request=request)
    return json.loads(dict_repr)


def render_template(template: str, data: dict, request) -> str:
    """Render a template including the api tools in the template context"""
    from caerp.views.render_api import Api

    data["api"] = Api(request.context, request)
    return render(template, data, request=request)
