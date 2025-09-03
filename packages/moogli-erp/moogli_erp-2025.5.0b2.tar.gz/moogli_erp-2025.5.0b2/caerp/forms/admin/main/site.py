import colander
from caerp.forms import files
from caerp import forms
from deform.widget import SequenceWidget, HiddenWidget
from caerp.utils.image import ImageResizer

LOGIN_IMAGE_RESIZER = ImageResizer(1200, 1200)
SITE_LOG_RESIZER = ImageResizer(400, 400)


class SiteConfigPhoto(colander.Schema):
    index = colander.SchemaNode(
        colander.Integer(),
        widget=HiddenWidget(),
        validator=colander.Range(0, 10),
        missing=colander.drop,
    )

    photo = files.ImageNode(
        title="Choisir une photo",
        missing=colander.drop,
        preparer=files.get_file_upload_preparer([LOGIN_IMAGE_RESIZER]),
    )

    title = colander.SchemaNode(
        colander.String(),
        title="Titre de la photo",
    )

    subtitle = colander.SchemaNode(
        colander.String(),
        title="Sous-titre de la photo",
        missing="",
    )

    author = colander.SchemaNode(
        colander.String(),
        title="Photographe ou attribution",
        missing="",
    )


class SiteConfigPhotos(colander.SequenceSchema):
    photo = SiteConfigPhoto()
    validator = colander.Length(max=10, max_err="Limité à ${max} photos")
    widget = SequenceWidget(add_subitem_text_template="Ajouter une photo")


class SiteConfigSchema(colander.MappingSchema):
    """
    Site configuration
    logos ...
    """

    logo = files.ImageNode(
        title="Choisir un logo",
        missing=colander.drop,
        preparer=files.get_file_upload_preparer([SITE_LOG_RESIZER]),
    )

    welcome = forms.textarea_node(
        title="Texte d’accueil",
        richwidget=True,
        missing="",
        admin=True,
    )

    login_backgrounds = SiteConfigPhotos(
        title="Photos de la page de connexion",
    )
