import os
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.models.config import (
    ConfigFiles,
    Config,
)
from caerp.plugins.sap.forms.admin.sap import SAPConfigSchema
from caerp.views.admin.main.digital_signatures import DIGITAL_SIGNATURES_ROUTE
from caerp.views.admin.tools import BaseAdminFormView
from caerp.views.files.routes import PUBLIC_ITEM
from . import (
    SAPIndexView,
    SAP_URL,
)

SAP_PDF_URL = os.path.join(SAP_URL, "pdf")


HELP_MSG = f"""La signature scannée se paramètre (optionellement) dans
<a href="{DIGITAL_SIGNATURES_ROUTE}">
  Configuration générale → Signatures numérisées
</a>.
"""


class SAPPdfView(BaseAdminFormView):
    title = "Attestation fiscale"
    description = "Configurer le contenu du PDF d'attestation fiscale SAP"
    schema = SAPConfigSchema()
    route_name = SAP_PDF_URL
    info_message = HELP_MSG
    validation_msg = "L'attestation fiscale SAP a bien été configurée"

    text_config_keys = [
        "sap_attestation_document_help",
        "sap_attestation_footer",
        "sap_attestation_signee",
    ]

    def _add_pdf_img_to_appstruct(self, data_type, appstruct):
        for file_type in ("header_img", "footer_img"):
            file_name = "%s_%s.png" % (data_type, file_type)
            file_model = ConfigFiles.get(file_name)
            if file_model is not None:
                appstruct[file_type] = {
                    "uid": file_model.id,
                    "filename": file_model.name,
                    "preview_url": self.request.route_url(
                        PUBLIC_ITEM,
                        name=file_name,
                    ),
                }

    def store_pdf_conf(self, appstruct, data_type):
        pdf_appstruct = appstruct
        for file_type in ("header_img", "footer_img"):
            file_datas = pdf_appstruct.get(file_type)
            if file_datas:
                file_name = "%s_%s.png" % (data_type, file_type)
                ConfigFiles.set(file_name, file_datas)

        for key in self.text_config_keys:
            Config.set(key, pdf_appstruct.get(key, ""))

    def before(self, form):
        """
        Add appstruct to the current form object
        """

        sap_pdf_appstruct = {
            key: self.request.config.get(key, "") for key in self.text_config_keys
        }
        self._add_pdf_img_to_appstruct("sap_attestation", sap_pdf_appstruct)
        form.set_appstruct(sap_pdf_appstruct)

    def submit_success(self, sap_pdf_appstruct):
        """
        Handle successfull SAP PDF configuration
        """
        self.store_pdf_conf(sap_pdf_appstruct, "sap_attestation")
        self.dbsession.flush()

        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.parent_view.route_name))


def includeme(config):
    config.add_route(SAP_PDF_URL, SAP_PDF_URL)
    config.add_admin_view(
        SAPPdfView, parent=SAPIndexView, permission=PERMISSIONS["global.config_sap"]
    )
