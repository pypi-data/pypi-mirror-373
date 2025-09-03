"""
    colander validators
"""
import logging
import colander
from cgi import FieldStorage

log = logging.getLogger(__name__)


def validate_image_mime(node, value):
    """
    Validate mime types for image files
    """

    mimetype = None

    # Handle FieldStorage Type
    if isinstance(value, FieldStorage):
        mimetype = value.type

    # Handle deform type
    elif value and value.get("mimetype"):
        mimetype = value["mimetype"]

    if mimetype and not mimetype.startswith("image/"):
        message = "Veuillez télécharger un fichier de type jpg, png, bmp ou gif"
        raise colander.Invalid(node, message)


def validate_rncp_rs_code(node, value):
    if value:
        v = value.upper()
        if not v.startswith("RNCP") and not v.startswith("RS"):
            msg = "Doit commencer par « RNCP » ou « RS »"
            raise colander.Invalid(node, msg)
