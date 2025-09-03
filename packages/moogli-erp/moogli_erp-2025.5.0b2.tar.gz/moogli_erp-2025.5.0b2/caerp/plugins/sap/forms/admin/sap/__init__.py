import colander

from caerp import forms
from caerp.forms.files import ImageNode, get_file_upload_preparer
from caerp.utils.image import ImageResizer

IMAGE_RESIZER = ImageResizer(1000, 1000)


class SAPConfigSchema(colander.Schema):
    header_img = ImageNode(
        title="En-tête des sortie PDF",
        missing=colander.drop,
        preparer=get_file_upload_preparer([IMAGE_RESIZER]),
    )
    sap_attestation_document_help = forms.textarea_node(
        title="Texte d'aide",
        description=(
            "Affiché une seule fois en fin de document "
            "mais avant le pied de page et la signature"
        ),
        missing="",
    )
    sap_attestation_signee = forms.textarea_node(
        title="Qui atteste / signe ?",
        missing="",
        description=(
            "souvent le gérant. Viendra s'insérer après " "« je soussigné … »"
        ),
    )
    footer_img = ImageNode(
        title="Image du pied de page des sorties PDF",
        description="Vient se placer au-dessus du texte du pied de page",
        missing=colander.drop,
        preparer=get_file_upload_preparer([IMAGE_RESIZER]),
    )
    sap_attestation_footer = forms.textarea_node(
        title="Texte du pied de page des sorties PDF",
        missing="",
    )
