"""
Export utilities:

    * Tools to build file responses (pdf, xls ...)
"""
import os
import re
import colander
import logging
import mimetypes
import unicodedata

from colanderalchemy import SQLAlchemySchemaNode
from pyramid.authorization import Allow
from unidecode import unidecode

from caerp.utils.ascii import force_ascii


logger = logging.getLogger(__name__)


def detect_file_mimetype(filename):
    """
    Return the headers adapted to the given filename
    """
    mimetype = mimetypes.guess_type(filename)[0] or "text/plain"
    return mimetype


def write_headers(request, filename, mimetype, encoding=None, force_download=True):
    """
    Write the given headers to the current request
    """
    # Here enforce ascii chars and string object as content type
    mimetype = force_ascii(mimetype)
    request.response.content_type = str(mimetype)
    request.response.charset = encoding
    if force_download:
        request.response.headerlist.append(
            (
                "Content-Disposition",
                'attachment; filename="{0}"'.format(force_ascii(filename)),
            )
        )
    return request


def get_buffer_value(filebuffer):
    """
    Return the content of the given filebuffer, handles the different
    interfaces between opened files and BytesIO containers
    """
    if hasattr(filebuffer, "getvalue"):
        return filebuffer.getvalue()
    elif hasattr(filebuffer, "read"):
        return filebuffer.read()
    else:
        raise Exception("Unknown file buffer type")


def ensure_encoding_bridge(filedata, encoding):
    """
    Ensure, if the encoding is not utf-8, that the returned data will not raise
    an encoding error (if the filedata is provided as a string)

    :param filedata: The data we return to the end user (str or bytes)
    :param str encoding: The name of the destination encoding

    :rtype: bytes
    """
    if (
        not isinstance(filedata, bytes)
        # and encoding.lower() != "utf-8"
        and hasattr(filedata, "encode")
    ):
        # replace remplace les caractères non traités par des ?
        result = filedata.encode(encoding, "replace")
    else:
        result = filedata
    return result


def write_file_to_request(
    request, filename, filebuffer, mimetype=None, encoding="UTF-8", force_download=True
):
    """
    Write a buffer as request content
    :param request: Pyramid's request object
    :param filename: The destination filename
    :param buf: The file buffer mostly BytesIO object, should provide a
        getvalue method
    :param mimetype: file mimetype, defaults to autodetection
    :param force_download: force file downloading instead of inlining
    """
    # Ref #384 : 'text/plain' is the default stored in the db
    request.response.charset = "UTF-8"
    if mimetype is None or mimetype == "text/plain":
        mimetype = detect_file_mimetype(filename)
    request = write_headers(
        request, filename, mimetype, encoding, force_download=force_download
    )

    value = get_buffer_value(filebuffer)
    value = ensure_encoding_bridge(value, encoding)
    if value:
        request.response.write(value)
    else:
        logger.warn(f"Unable to write file '{filename}' to request : empty buffer")
    return request


def store_export_file(
    context, request, export_file, export_filename, mimetype, encoding="utf-8"
):
    """
    Stores the export file containing accounting operations
    """
    export_file.seek(0)
    data = export_file.getvalue()

    exported_file_acl = [
        [
            Allow,
            "group:admin",
            ["context.view_file", "context.edit_file", "context.delete_file"],
        ],
        [
            Allow,
            request.identity.login.login,
            ["context.view_file", "context.edit_file", "context.delete_file"],
        ],
    ]

    from caerp.models import files

    file_obj = files.File(
        name=export_filename,
        description=export_filename,
        _acl=exported_file_acl,
    )
    file_obj.data = ensure_encoding_bridge(data, encoding)
    file_obj.size = len(data)
    file_obj.mimetype = mimetype
    request.dbsession.add(file_obj)
    return file_obj


def slugify(value, allow_unicode=False):
    """
    Taken from
    https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    value = unicodedata.normalize("NFKC", value)

    if not allow_unicode:
        value = unidecode(value)

    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def format_filename(filename):
    """
    Format filename to avoid illegal characters

    :rtype: str
    """
    basename, ext = os.path.splitext(filename)
    basename = slugify(basename)
    return "{}{}".format(basename, ext)


class JSONExportSQLAlchemySchemaNode(SQLAlchemySchemaNode):
    """
    Patched version of SQLAchemySchemaNode dedicated to import/export of complex objects as JSON

    This is not classical JSON : every scalar is encoded as string (ex: False
    -> "false", 1.2 -> "1.2"). But what matters most here is not interoperability, but the ability to
    import/export from/to MoOGLi and the reliability/maintenaibility of that process with evolving models.

    Contains bugfixes, configurability and design change

    - Unplug from the config set in SQLA models ({"info": {"colanderalchemy": …}})
    - Possible to configure via SchemaNode class attributes rather than imperatively :
      - the SQLA underlying model
      - the overrides / includes / excludes params.
    - fix 1 bug on dictification
    - fix 2 limitations and 1 bug in nested relationship
    - Automatic instantiating of subclasses when using SA polymorphism
    """

    # Just set a key that is never set on existing column definitions
    # Unless we do that, it is impossible to serialize a relation that has an
    # exclude=True in class declaration
    # (colanderalchemy does not allow that level of override)
    # Might be a bug, but the lib seems unmaintained
    # It leaves us « unplugged » for ColanderAlchemy models-based configuration
    sqla_info_key = "colanderalchemy_json_export"

    # Those vars allow declarative overrides
    # May be let to None and passed as-usual as first arg of constructor
    CLASS = None
    # Optionals
    OVERRIDES = None
    INCLUDES = None
    EXCLUDES = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("overrides", self.OVERRIDES)
        kwargs.setdefault("excludes", self.EXCLUDES)
        kwargs.setdefault("includes", self.INCLUDES)
        if self.CLASS is None:  #  FIXME: virer ?
            super().__init__(*args, **kwargs)
        else:
            super().__init__(self.CLASS, *args, **kwargs)

    def dictify(self, obj):
        """
        Overrided to fix a colanderalchemy bug:
        if a child schema is called "items"¹

        Root bug cause is ColanderAlchemy accesses column
        information through column_attrs/relationship_attrs attributes, but this is
        unreliable as namespace own attributes, (eg column_attrs.items()) are polutting
        namespaces.

        Fixing that by accessing column information with the dict-like API
        of column_attrs/relationship_attrs.
        """
        dict_ = {}
        for node in self:
            name = node.name
            try:
                attribute_col = self.inspector.column_attrs.get(name)
                relationship_col = self.inspector.relationships.get(name)
                if not attribute_col and not relationship_col:
                    raise KeyError

            except (AttributeError, KeyError):
                # The given node isn't part of the SQLAlchemy model
                msg = "SQLAlchemySchemaNode.dictify: %s not found on %s"
                # log.debug(msg, name, self)
                continue
            else:
                if attribute_col is not None:
                    value = getattr(obj, name)
                elif relationship_col is not None:
                    if relationship_col.uselist:
                        value = [
                            self[name].children[0].dictify(o)
                            for o in getattr(obj, name)
                        ]
                    else:
                        o = getattr(obj, name)
                        value = None if o is None else self[name].dictify(o)

            # SQLAlchemy mostly converts values into Python types
            #  appropriate for appstructs, but not always.  The biggest
            #  problems are around `None` values so we're dealing with
            #  those here.  All types should accept `colander.null` so
            #  we mostly change `None` into that.

            if value is None:
                if isinstance(node.typ, colander.String):
                    # colander has an issue with `None` on a String type
                    #  where it translates it into "None".  Let's check
                    #  for that specific case and turn it into a
                    #  `colander.null`.
                    dict_[name] = colander.null
                else:
                    # A specific case this helps is with Integer where
                    #  `None` is an invalid value.  We call serialize()
                    #  to test if we have a value that will work later
                    #  for serialization and then allow it if it doesn't
                    #  raise an exception.  Hopefully this also catches
                    #  issues with user defined types and future issues.
                    try:
                        node.serialize(value)
                    except:
                        dict_[name] = colander.null
                    else:
                        dict_[name] = value
            else:
                dict_[name] = value

        return dict_

    def objectify(self, dict_, context=None):
        # Objectify to the right child-class
        if self.inspector.polymorphic_on is not None:
            try:
                polymorphic_col_name = self.inspector.polymorphic_on.name
                polymorphic_key = dict_.get(polymorphic_col_name, None)
                context = self.inspector.polymorphic_map[polymorphic_key].class_()
            except KeyError:
                context = None

        return super().objectify(dict_, context)

    def get_schema_from_relationship(self, prop, overrides):
        """
        Pimps this method so that the child nodes are JSONExportSQLAlchemySchemaNode

        Works around two limitations of two SQLAlchemyNode :
        - child schema (mappings) are SQLAlchemyNode, not our customized clas
        - Sequences schemas items are plain SchemaNode, not even SQLAlchemyNode

        And one bug:
        - default cannot be overrided imperatively
        :param prop:
        :param overrides:
        :return:
        """

        node = super().get_schema_from_relationship(prop, overrides)
        if isinstance(node, SQLAlchemySchemaNode) or (
            isinstance(node.typ, colander.Sequence)
            and isinstance(node.children[0], SQLAlchemySchemaNode)
        ):
            if isinstance(node.typ, colander.Mapping):
                reference_node = node
            else:  # colander.Sequence
                reference_node = node.children[0]

            new_node = JSONExportSQLAlchemySchemaNode(
                reference_node.class_,
                name=reference_node.name,
                includes=reference_node.includes,
                excludes=reference_node.excludes,
                overrides=reference_node.overrides,
                missing=reference_node.missing,
                parents_=reference_node.parents_,
            )

            if isinstance(node, SQLAlchemySchemaNode):
                ret = new_node
            else:
                node.children[0] = new_node
                ret = node

            if "default" in overrides:
                ret.default = overrides["default"]
            return ret
