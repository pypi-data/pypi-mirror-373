import os
import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.main.smtp import SmtpIndexView, SMTP_INDEX_URL

EMAIL_ESTIMATION_ROUTE = os.path.join(SMTP_INDEX_URL, "estimation_email")
EMAIL_INVOICE_ROUTE = os.path.join(SMTP_INDEX_URL, "invoice_email")

logger = logging.getLogger(__name__)


class AdminEstimationEmailView(BaseConfigView):
    title = "Gabarits d’e-mails pour envoyer les devis"
    description = "Configurer le contenu des e-mails d’envoi de devis aux clients dans l’application."
    info_message = (
        "<p>MoOGLi permet l’envoi des devis "
        "et factures aux clients directement depuis l’application.</p>"
        "<p>Les gabarits des e-mails de devis envoyés aux clients par MoOGLi "
        "sont configurables ici.</p>"
        "<br />"
        "<h4>Variables disponibles :</h4>"
        "<ul>"
        "<li><code>{task.customer.label}</code> : nom du client</li>"
        "<li><code>{task.company.name}</code> : nom de l’enseigne</li>"
        "<li><code>{task.internal_number}</code> : numéro du document</li>"
        "</ul>"
        "<br />"
        "<p>NB : Le contenu définitif des e-mails peut être modifié par l’entrepreneur "
        "au moment de l’envoi.</p>"
    )
    route_name = EMAIL_ESTIMATION_ROUTE
    keys = (
        "smtp_cae_estimation_subject_template",
        "smtp_cae_estimation_body_template",
    )
    permission = PERMISSIONS["global.config_cae"]

    def get_schema(self):
        return get_config_schema(self.keys)


class AdminInvoiceEmailView(BaseConfigView):
    title = "Gabarits d’e-mails pour envoyer les factures"
    description = "Configurer le contenu des e-mails d’envoi de factures aux clients dans l’application."
    info_message = (
        "<p>MoOGLi permet l’envoi des devis "
        "et factures aux clients directement depuis l’application.</p>"
        "<p>Les gabarits des e-mails de factures envoyés aux clients par MoOGLi "
        "sont configurables ici.</p>"
        "<br />"
        "<h4>Variables disponibles :</h4>"
        "<ul>"
        "<li><code>{task.customer.label}</code> : nom du client</li>"
        "<li><code>{task.company.name}</code> : nom de l’enseigne</li>"
        "<li><code>{task.official_number}</code> : numéro de la facture</li>"
        "</ul>"
        "<br />"
        "<p>NB : Le contenu définitif des e-mails peut être modifié par l’entrepreneur "
        "au moment de l’envoi.</p>"
    )
    route_name = EMAIL_INVOICE_ROUTE
    keys = (
        "smtp_cae_invoice_subject_template",
        "smtp_cae_invoice_body_template",
    )
    permission = PERMISSIONS["global.config_cae"]

    def get_schema(self):
        return get_config_schema(self.keys)


def includeme(config):
    config.add_route(EMAIL_ESTIMATION_ROUTE, EMAIL_ESTIMATION_ROUTE)
    config.add_route(EMAIL_INVOICE_ROUTE, EMAIL_INVOICE_ROUTE)
    config.add_admin_view(
        AdminEstimationEmailView,
        parent=SmtpIndexView,
    )
    config.add_admin_view(
        AdminInvoiceEmailView,
        parent=SmtpIndexView,
    )
