import colander

from caerp.utils.image import ImageResizer
from caerp.forms import files


class DigitalSignaturesSchema(colander.MappingSchema):
    """
    Digital signatures form schema
    """

    cae_manager_digital_signature = files.ImageNode(
        show_delete_control=True,
        title="Signature du gérant",
        missing=colander.drop,
        preparer=files.get_file_upload_preparer([ImageResizer(800, 800)]),
        description="Charger un fichier de type image *.png *.jpeg \
 *.jpg…",
    )
