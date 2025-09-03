import colander
import deform
import logging

from cgi import FieldStorage
from PIL import UnidentifiedImageError
from pyramid_deform import SessionFileUploadTempStore
from sqlalchemy.orm import load_only
from typing import List, Union
from typing_extensions import Protocol

from caerp.consts.permissions import PERMISSIONS
from caerp import forms
from caerp.compute.math_utils import convert_to_int
from caerp.forms.validators import validate_image_mime
from caerp.models.project.project import Project
from caerp.models.node import Node
from caerp.models.task import Task
from caerp.models.files import (
    File,
    FileType,
)
from caerp.models.career_path import CareerPath
from caerp.models.project.business import Business
from caerp.models.project.file_types import BusinessTypeFileType
from caerp.models.user.user import User
from caerp.utils.datetimes import format_date
from caerp.utils.files import DeformFileDict
from caerp.utils.strings import human_readable_filesize


logger = logging.getLogger(__name__)


class CustomFileUploadWidget(deform.widget.FileUploadWidget):
    """
    File upload widget that handles:
      - filters when deserializing
      - file deletion (via a checkbox)

        filters

            An optionnal list (or simple filter) that will be fired on the datas
            (for example in order to reduce image sizes)

       show_delete_control (default :False)

           Display a checkbox to allow deleting the file from form ("clearing"
           file field).

    """

    template = "fileupload.pt"

    def __init__(self, *args, **kwargs):
        self.show_delete_control = kwargs.pop("show_delete_control", False)
        super(CustomFileUploadWidget, self).__init__(*args, **kwargs)

    @property
    def _pstruct_schema(self):
        # Overrides a private attribute form FileUploadWidget
        pstruct_schema = deform.widget.FileUploadWidget._pstruct_schema.clone()
        delete_field_node = colander.SchemaNode(
            colander.String(allow_empty=True),
            name="delete",
            missing=None,
        )
        pstruct_schema.add(delete_field_node)
        return pstruct_schema

    def deserialize(self, field, pstruct):
        data = deform.widget.FileUploadWidget.deserialize(self, field, pstruct)
        # We're returning the datas in the appstruct dict, we format the file if
        # needed
        uid = self._pstruct_schema.deserialize(pstruct).get("uid")

        if pstruct.get("delete") and uid and self.show_delete_control:
            data = {"delete": True}
            return data
        return data


class FileNode(colander.SchemaNode):
    """
    A main file upload node class

    Can be initialized with any colander attribute (preparer, widget ...)

    Can also be initialized with the show_delete_control named parameter.
    The widget will display a checkbox to allow deleting the file from form ("clearing")


    Use this node in a custom schema.
    Then, on submit :

        >>> class Schema(colander.Schema):
                filenodename = FileNode(title="Fichier")

        # You need to pass the name before merging the appstruct
        >>> f_object = File(
            parent=parent_obj, name=appstruct['filenodename']['name']
        )
        >>> merge_session_with_post(f_object, appstruct)
        >>> dbsession.add(f_object)

    """

    schema_type = deform.FileData
    title = "Choix du fichier"
    default_max_size = 1048576
    _max_allowed_file_size = None

    def validator(self, node, value):
        """
        Build a file size validator
        """
        # Note : syntaxe colander un peu différente de d'habitude
        # Pour les validator sur les Schémas qui sont des class, on peut déclarer le
        # validator comme une méthode avec self.bindings qui contient les arguments
        # utilisés lorsque l'on bind le schéma
        # Dans caerp self.bindings contient essentiellement request
        request = self.bindings["request"]
        max_filesize = self._get_max_allowed_file_size(request)
        if value is not None:
            if isinstance(value, FieldStorage):
                file_obj = value.fp
            else:
                file_obj = value.get("fp")
            if file_obj:
                file_obj.seek(0)
                size = len(file_obj.read())
                file_obj.seek(0)
                if size > max_filesize:
                    message = "Ce fichier est trop volumineux"
                    raise colander.Invalid(node, message)

    def _get_max_allowed_file_size(self, request) -> int:
        """
        Return the max allowed filesize configured in MoOGLi
        """
        if self._max_allowed_file_size is None:
            settings = request.registry.settings
            size = settings.get("caerp.maxfilesize", self.default_max_size)
            self._max_allowed_file_size = convert_to_int(size, self.default_max_size)

        return self._max_allowed_file_size

    @colander.deferred
    def widget(self, kw):
        request = kw["request"]
        tmpstore = SessionFileUploadTempStore(request)
        show_delete_control = getattr(self, "show_delete_control", False)
        return CustomFileUploadWidget(tmpstore, show_delete_control=show_delete_control)

    def after_bind(self, node, kw):
        size = self._get_max_allowed_file_size(kw["request"])
        if not getattr(self, "description", ""):
            self.description = ""

        self.description += " Taille maximale : {0}".format(
            human_readable_filesize(size)
        )


class ImageNode(FileNode):
    def validator(self, node, value):
        FileNode.validator(self, node, value)
        validate_image_mime(node, value)

    def after_bind(self, node, kw):
        FileNode.after_bind(self, node, kw)
        if not getattr(self, "description", ""):
            self.description = ""

        self.description += (
            ". Charger un fichier de type image (*.png, *.jpeg ou *.jpg)"
        )


# Protocol est l'équivalent des interfaces mais compatible avec
# le typing Python.
# Ici on décrit un handler qui permettra de traiter une image ou un
# document déposé dans un formulaire
# Voir utils/image.py pour des exemples d'implémentation
class FileUploadModifier(Protocol):
    def __call__(
        self, value: Union[DeformFileDict, FieldStorage]
    ) -> Union[DeformFileDict, FieldStorage]:
        ...


def get_file_upload_preparer(modifiers: List[FileUploadModifier]):
    """
    Build a preparer handling file transformation on upload
    """

    def preparer(value):
        """
        Apply all the handlers to the provided value
        """
        for modifier in modifiers:
            try:
                value = modifier(value)
            except UnidentifiedImageError:
                logger.debug("Cannot identify image file, probably not an image")
                continue
            except Exception:
                logger.exception("Erreur while processing uploaded")
                continue

        return value

    return preparer


class FileTypeNode(colander.SchemaNode):
    title = "Type de document"
    schema_type = colander.Int

    def __init__(self, *args, **kwargs):
        colander.SchemaNode.__init__(self, *args, **kwargs)
        self.types = []

    @colander.deferred
    def widget(self, kw):
        request = kw["request"]
        context = request.context
        available_types = self._collect_available_types(request, context)
        if available_types:
            choices = [(t.id, t.label) for t in available_types]
            choices.insert(0, ("", ""))
            widget = deform.widget.SelectWidget(values=choices)
        else:
            widget = deform.widget.HiddenWidget()
        return widget

    def _collect_available_types(self, request, context):
        """
        Collect file types that may be loaded for the given context

        :param obj context: The current object we're attaching a file to
        :returns: A list of FileType instances
        """
        result = []
        if isinstance(context, File):
            context = context.parent

        if isinstance(context, Task) or isinstance(context, Business):
            business_type_id = context.business_type_id

            result = BusinessTypeFileType.get_file_type_options(
                business_type_id, context.type_
            )
        elif isinstance(context, Project):
            result = []
            for business_type in context.get_all_business_types(request):
                result.extend(
                    BusinessTypeFileType.get_file_type_options(
                        business_type.id, requirement_type="project_mandatory"
                    )
                )
        else:
            result = (
                FileType.query()
                .options(load_only("id", "label"))
                .order_by(FileType.label.asc())
                .all()
            )
        return result

    def after_bind(self, node, kw):
        get_params = kw["request"].GET
        if "file_type_id" in get_params:
            self.default = int(get_params["file_type_id"])


@colander.deferred
def deferred_parent_id_validator(node, kw):
    request = kw["request"]

    def validate_node(node, value):
        logger.debug("Deferred parent_id_validator")
        logger.debug(value)
        node_object = request.dbsession.query(Node).get(value)
        logger.debug(node_object)
        if node_object is None and not request.has_permission(
            PERMISSIONS["context.add_file"]
        ):
            colander.Invalid(node, "You don't have permission to add standalone files")
        if not request.has_permission(
            PERMISSIONS["context.edit_file"], node_object
        ) and not request.has_permission(PERMISSIONS["context.add_file"], node_object):
            raise colander.Invalid(
                node, f"You don't have permission to edit this node {node_object}"
            )

    return validate_node


@colander.deferred
def deferred_parent_id_missing(node, kw):
    request = kw["request"]
    context = request.context
    if isinstance(context, (Node, File)):
        return colander.drop
    else:
        # Cas où on ajoute un fichier directement sur /api/v1/files
        return colander.required


class FileUploadSchema(colander.Schema):
    come_from = forms.come_from_node()
    popup = forms.popup_node()

    upload = FileNode()

    description = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(
            min=5,
            max=100,
            min_err="La description ne doit pas être inférieure à 5 caractères",
            max_err="La description ne doit pas être supérieure à 100 caractères",
        ),
    )
    file_type_id = FileTypeNode(missing=colander.drop)
    indicator_id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=deform.widget.HiddenWidget(),
    )
    parent_id = colander.SchemaNode(
        colander.Integer(),
        missing=deferred_parent_id_missing,
        widget=deform.widget.HiddenWidget(),
        validator=deferred_parent_id_validator,
    )


def get_file_upload_schema(file_modifiers: List[FileUploadModifier] = []):
    """
    Build a Full File upload schema adding file handlers as preparers for the file node

    .. code-block:: python

        from caerp.utils.image import ImageRatio
        from caerp.forms.files import get_file_upload_schema
        schema = get_file_upload_schema([ImageRatio(100, 100)])
    """
    schema = FileUploadSchema()
    if len(file_modifiers) > 0:
        schema["upload"].preparer = get_file_upload_preparer(file_modifiers)
    return schema


def get_template_upload_schema():
    """
    Return the form schema for template upload
    """
    schema = FileUploadSchema()
    schema["upload"].description += " Le fichier doit être au format ODT"
    del schema["file_type_id"]
    del schema["parent_id"]
    del schema["indicator_id"]

    return schema


def get_businesstype_filetype_template_upload_schema():
    """
    Return the form schema for business type / file type template upload
    """

    def customize_schema(schema):
        schema["upload"].description += " Le fichier doit être au format ODT"
        schema["business_type_id"] = colander.SchemaNode(
            colander.Integer(),
            widget=deform.widget.HiddenWidget(),
        )
        schema["file_type_id"] = colander.SchemaNode(
            colander.Integer(),
            widget=deform.widget.HiddenWidget(),
        )
        del schema["parent_id"]
        del schema["indicator_id"]

    schema = FileUploadSchema().clone()
    customize_schema(schema)
    return schema


def get_userdata_file_upload_schema(request, excludes=()):
    """
    Return the specific form schema for userdata's file upload
    """
    schema = FileUploadSchema().clone()
    if "career_path_id" not in excludes:
        # TODO : convertir ces méthodes en statichmethod ou les sortir d'ici
        # cf le message du type checker
        def filter_by_userdata(node, kw):
            if isinstance(kw["request"].context, File):
                return CareerPath.userdatas_id == kw["request"].context.parent.id
            elif isinstance(kw["request"].context, User):
                return CareerPath.userdatas_id == kw["request"].context.userdatas.id
            else:
                raise KeyError("UserDatas related files should be attached to a User")

        def get_career_path_label(node):
            """
            génère un label pour l'étape de parcours

            :param obj node: L'étape de parcours
            """

            label = "{}".format(format_date(node.start_date))
            if node.career_stage is not None:
                label += " : {}".format(node.career_stage.name)

            if node.cae_situation is not None:
                label += " ({})".format(node.cae_situation.label)
            return label

        schema.add(
            colander.SchemaNode(
                name="career_path_id",
                typ=colander.Integer(),
                title="Attacher à une étape du parcours de l'entrepreneur",
                widget=forms.get_deferred_model_select(
                    CareerPath,
                    multi=False,
                    mandatory=False,
                    keys=("id", get_career_path_label),
                    filters=[filter_by_userdata],
                    empty_filter_msg="Non",
                ),
                missing=colander.drop,
            )
        )
    return schema
