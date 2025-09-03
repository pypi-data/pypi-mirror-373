"""
Panel displaying CustomBusinessIndicators

- bpf
- facturation
"""
import logging

from caerp.views.indicators.routes import INDICATOR_ROUTE

logger = logging.getLogger(__name__)


def custom_indicator_panel(context, request, indicator):
    """
    Panel displaying an indicator in a generic format
    """
    force_url = request.route_path(
        INDICATOR_ROUTE,
        id=indicator.id,
        _query={"action": "force"},
    )
    return dict(
        indicator=indicator,
        force_url=force_url,
    )


def includeme(config):
    TEMPLATE_PATH = "caerp:templates/panels/indicators/{}"
    config.add_panel(
        custom_indicator_panel,
        "custom_indicator",
        renderer=TEMPLATE_PATH.format("custom_indicator.mako"),
    )
