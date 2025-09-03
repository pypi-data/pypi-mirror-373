from pyramid.request import Request
from pyramid.session import ISession
from caerp_base.models.base import DBSESSION


class BaseController:
    def __init__(self, context, request=None):
        if request is None:
            # Needed for manually called views
            self.request: Request = context
            self.context = self.request.context
        else:
            self.request: Request = request
            self.context = context
        self.session: ISession = self.request.session
        self.dbsession: DBSESSION = self.request.dbsession
