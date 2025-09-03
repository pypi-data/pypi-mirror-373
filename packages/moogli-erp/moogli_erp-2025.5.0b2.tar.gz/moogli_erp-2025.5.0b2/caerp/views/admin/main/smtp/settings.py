import os
from caerp.consts.permissions import PERMISSIONS
from caerp.services.smtp.smtp import get_cae_smtp
from caerp.views.smtp.views import CompanySmtpSettingsView
from . import SMTP_INDEX_URL, SmtpIndexView
from caerp.views.smtp.routes import (
    API_BASE_ROUTE as API_SMTP,
)

SMTP_SETTINGS_URL = os.path.join(SMTP_INDEX_URL, "settings")


class AdminSmtpView(CompanySmtpSettingsView):
    route_name = SMTP_SETTINGS_URL
    permission = PERMISSIONS["global.config_cae"]
    description = (
        "Configurer le serveur SMTP du service d’envoi d’e-mails utilisable par "
        "les entrepreneurs de la CAE pour envoyer leurs devis et factures aux clients"
    )

    def get_company_id(self):
        return None

    def context_url(self, _query):
        return self.request.route_path(SMTP_SETTINGS_URL)

    def get_current_smtp_settings(self):
        return get_cae_smtp(self.request)

    def get_api_url(self):
        return self.request.route_url(API_SMTP)


def includeme(config):
    config.add_route(SMTP_SETTINGS_URL, SMTP_SETTINGS_URL)
    config.add_admin_view(
        AdminSmtpView,
        parent=SmtpIndexView,
        renderer="base/vue_app.mako",
    )
