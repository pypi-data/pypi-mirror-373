"""
Configuration de filedepot
"""
import cgi
import logging
from caerp.export.utils import detect_file_mimetype


logger = logging.getLogger(__name__)


def configure_filedepot(settings):
    """
    Setup filedepot storage(s)
    """
    try:
        path = settings["caerp.depot_path"]
    except KeyError as err:
        logger.exception(
            " !!!! You forgot to configure filedepot with an \
'caerp.depot_path' setting"
        )
        raise err

    from depot.manager import DepotManager

    name = "local"
    if name not in DepotManager._depots:
        DepotManager.configure(name, {"depot.storage_path": path})


def _to_fieldstorage(fp, filename, size, **_kwds):
    """Build a :class:`cgi.FieldStorage` instance.

    Deform's :class:`FileUploadWidget` returns a dict, but
    :class:`depot.fields.sqlalchemy.UploadedFileField` likes
    :class:`cgi.FieldStorage` objects
    """
    f = cgi.FieldStorage()
    f.file = fp
    f.filename = filename
    mimetype = _kwds.get("mimetype", "")
    if not mimetype:
        mimetype = detect_file_mimetype(filename)
    f.type = mimetype
    f.length = size
    return f
