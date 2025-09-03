from caerp.utils.compat import Iterable
from typing import Tuple

from .models.sap import SAPAttestation
from caerp.models.config import (
    ConfigFiles,
    Config,
)


def pdf_header_panel(context: SAPAttestation, request):
    """
    The panel used to render the header of the pdf content
    """
    header_key = "sap_attestation_header_img.png"

    has_header = ConfigFiles.query().filter_by(key=header_key).count() > 0
    return dict(
        attestation=context, has_header=has_header, url="/public/{}".format(header_key)
    )


def pdf_content_panel(context: SAPAttestation, request, lines: Iterable[Tuple]):
    signature_key = "cae_manager_digital_signature.png"
    signature = ConfigFiles.get(signature_key)
    signature_url = request.route_path("/public/{name}", name=signature_key)
    return dict(
        customer_name=context.customer.label,
        document_help=Config.get_value("sap_attestation_document_help"),
        signee=Config.get_value("sap_attestation_signee"),
        attestation=context,
        lines=lines,
        has_signature=bool(signature),
        signature_url=signature_url,
    )


# TODO pdf_footer.mako uses workshop_footer css class, should we create a
# sap_attestation_footer class ?
def pdf_footer_panel(context: SAPAttestation, request, **kwargs):
    """
    The panel used to render the SAP attestation pdf footer
    :param obj context: The current SAP attestation
    """
    img_key = "sap_attestation_footer_img.png"
    has_img = ConfigFiles.query().filter_by(key=img_key).count() > 0
    text = request.config.get("sap_attestation_footer")
    return dict(
        img_url="/public/{}".format(img_key),
        has_img=has_img,
        text=text,
        has_text=bool(text),
        **kwargs,
    )


def includeme(config):
    config.add_panel(
        pdf_header_panel,
        "sap_attestation_pdf_header",
        renderer="caerp.plugins.sap:/templates/panels/sap/pdf_header.mako",
    )
    config.add_panel(
        pdf_content_panel,
        "sap_attestation_pdf_content",
        renderer="caerp.plugins.sap:/templates/panels/sap/pdf_content.mako",
    )
    config.add_panel(
        pdf_footer_panel,
        "sap_attestation_pdf_footer",
        renderer="caerp.plugins.sap:/templates/panels/sap/pdf_footer.mako",
    )
