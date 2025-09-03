# * Authors:
#       * TJEBBES Gaston <g.t@majerti.fr>
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
"""
Module providing a custom tween that cleans the scoped_session on each request

The problem :

    pyramid_tm commits/rollback/closes the current sqlalchemy session

But inside a same thread, scoped_session returns the same session object which
keeps some state related informations

See :

    https://groups.google.com/forum/#!topic/pylons-discuss/hm5MuaQD1qo
"""
from caerp_base.models.base import DBSESSION


def tm_cleanup_tween_factory(handler, registry):
    def tween(request):
        try:
            return handler(request)
        finally:
            DBSESSION.remove()

    return tween


def includeme(config):
    config.add_tween(
        __name__ + ".tm_cleanup_tween_factory", over="pyramid_tm.tm_tween_factory"
    )
