import os
from caerp.views.admin.main import (
    MAIN_ROUTE,
    MainIndexView,
)
from caerp.views.admin.tools import BaseAdminIndexView


SMTP_INDEX_URL = os.path.join(MAIN_ROUTE, "smtp")


class SmtpIndexView(BaseAdminIndexView):
    title = "Service d’envoi d’e-mails"
    description = (
        "Configurer l’envoi d’e-mails aux clients directement depuis l’application."
    )
    route_name = SMTP_INDEX_URL


def includeme(config):
    config.add_route(SMTP_INDEX_URL, SMTP_INDEX_URL)
    config.add_admin_view(SmtpIndexView, parent=MainIndexView)
    config.include(".settings")
    config.include(".mail")
