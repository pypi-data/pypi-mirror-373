"""
    Translation tools
"""
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request


def translate(term):
    """
    String translator
    Allows string translation without having a request object available
    from deform rendering for example
    """
    tsf = TranslationStringFactory("deform")
    localizer = get_localizer(get_current_request())
    if not hasattr(term, "interpolate"):
        term = tsf(term)
    return localizer.translate(term)
