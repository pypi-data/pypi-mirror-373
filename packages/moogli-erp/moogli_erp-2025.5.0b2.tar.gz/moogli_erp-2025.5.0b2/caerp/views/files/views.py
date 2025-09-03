import io
import logging

from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from typing import Any, List

from caerp.export.utils import write_file_to_request
from caerp.forms.files import get_file_upload_schema
from caerp.models.files import File
from caerp.resources import fileupload_js
from caerp.utils.image import ImageResizer
from caerp.utils.widgets import ViewLink, Link
from caerp.utils.zip import mk_zip
from caerp.views import (
    BaseFormView,
    BaseView,
    DeleteView,
    PopupMixin,
    submit_btn,
    cancel_btn,
)
from caerp.views.files.controller import FileController
from caerp.views.training.routes import USER_TRAINER_FILE_URL
from caerp.views.userdatas.routes import USER_USERDATAS_FILELIST_URL

from .routes import (
    FILE_ITEM,
    FILE_PNG_ITEM,
    NODE_FILE_ROUTE,
    PUBLIC_ITEM,
)


UPLOAD_MISSING_DATAS_MSG = "Des informations sont manquantes pour \
l'adjonction de fichiers"


UPLOAD_OK_MSG = "Le fichier a bien été enregistré"
EDIT_OK_MSG = "Le fichier a bien été enregistré"


logger = log = logging.getLogger(__name__)


def file_dl_view(context, request):
    """
    download view for a given file
    """
    write_file_to_request(
        request,
        context.name,
        context,
        context.mimetype,
    )
    return request.response


def file_stream_view(context, request):
    """
    download view for a given file
    """
    write_file_to_request(
        request,
        context.name,
        context,
        context.mimetype,
        force_download=False,
    )
    return request.response


class FileViewRedirectMixin(PopupMixin):
    """
    Mixin providing tools to handle redirection from within a File related view
    """

    NODE_TYPE_ROUTES = {
        "activity": "activity",
        "business": "/businesses/{id}/files",
        "cancelinvoice": "/cancelinvoices/{id}",
        "estimation": "/estimations/{id}",
        "internalestimation": "/estimations/{id}",
        "expensesheet": "/expenses/{id}",
        "invoice": "/invoices/{id}",
        "internalinvoice": "/invoices/{id}",
        "internalcancelinvoice": "/cancelinvoices/{id}",
        "project": "/projects/{id}/files",
        "userdata": USER_USERDATAS_FILELIST_URL,
        "workshop": "workshop",
        "supplier_order": "/supplier_orders/{id}",
        "internalsupplier_order": "/supplier_orders/{id}",
        "supplier_invoice": "/supplier_invoices/{id}",
        "internalsupplier_invoice": "/supplier_invoices/{id}",
        "trainerdata": USER_TRAINER_FILE_URL,
    }

    NODE_TYPE_LABEL = {
        "activity": "au rendez-vous",
        "business": "à l'affaire",
        "cancelinvoice": "à l'avoir",
        "estimation": "au devis",
        "internalestimation": "au devis interne",
        "expensesheet": "à la note de dépenses",
        "invoice": "à la facture",
        "internalinvoice": "à la facture interne",
        "internalcancelinvoice": "à l'avoir interne",
        "project": "au dossier",
        "userdata": "à la fiche de gestion sociale",
        "workshop": "à l'atelier",
        "supplier_order": "à la commande fournisseur",
        "internalsupplier_order": "à la commande fournisseur interne",
        "supplier_invoice": "à la facture fournisseur",
        "internalsupplier_invoice": "à la facture fournisseur interne",
    }

    def get_redirect_item(self):
        item = parent = self.context.parent
        if parent.type_ in ["userdata", "trainerdata"]:
            item = parent.user
        return item

    def back_url(self):
        if "come_from" in self.request.params:
            return self.request.params["come_from"]
        parent = self.context.parent
        if parent is None:
            return self.request.referer

        route_name = self.NODE_TYPE_ROUTES.get(parent.type_)
        if route_name is None:
            raise Exception(
                "You should set the route name of the file's parent type ({}) "
                "in views.files.FileView.NODE_TYPE_ROUTES attribute".format(
                    parent.type_
                )
            )
        return self.request.route_path(route_name, id=self.get_redirect_item().id)

    def get_label(self):
        parent = self.context.parent
        if parent is None:
            return ""
        type_label = self.NODE_TYPE_LABEL.get(parent.type_, "au précédent")
        label = "Revenir {0}".format(type_label)
        return label


class FileView(BaseView, FileViewRedirectMixin):
    """
    A base file view allowing to tune the way datas is shown
    """

    def populate_actionmenu(self):
        back_url = self.back_url()
        if back_url:
            return Link(self.back_url(), self.get_label())
        else:
            return None

    def get_file_path(self, action):
        params = self.request.GET
        params["action"] = action
        return self.request.current_route_path(_query=params)

    def edit_url(self):
        return self.get_file_path("edit")

    def delete_url(self):
        return self.get_file_path("delete")

    def download_url(self):
        return self.get_file_path("download")

    def __call__(self):
        return dict(
            title="Fichier {0}".format(self.context.name),
            file=self.context,
            edit_url=self.edit_url(),
            delete_url=self.delete_url(),
            download_url=self.download_url(),
            navigation=self.populate_actionmenu(),
        )


class FileUploadView(BaseFormView):
    """
    Form view for file upload

    Current context for this view is the document the file should be attached
    to (Invoice, Estimation...)

    By getting the referrer url from the request object, we provide the
    redirection to the original page when the file is added

    a `class:caerp.events.files.FileAdded` is fired on file modification
    """

    factory = File

    title = "Téléverser un fichier"
    edit = False
    valid_msg = None
    buttons = (
        submit_btn,
        cancel_btn,
    )

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller = FileController(self.request, edit=self.edit)

    def get_schema(self):
        return get_file_upload_schema([ImageResizer(1200, 1200, "PDF")])

    def before(self, form):
        fileupload_js.need()

        come_from = self.request.referrer
        appstruct = {
            "come_from": come_from,
        }
        form.set_appstruct(appstruct)

    def redirect(self, come_from):
        """
        Build the redirection url

        Can be overriden to specify a redirection
        """
        return HTTPFound(come_from)

    def save(self, appstruct):
        return self.controller.save(appstruct)

    def submit_success(self, appstruct):
        """
        Insert data in the database
        """
        log.debug("A file has been uploaded (add or edit)")
        come_from = appstruct.pop("come_from", None)
        self.save(appstruct)
        # Clear all informations stored in session by the tempstore used for
        # the file upload widget
        self.request.session.pop("substanced.tempstore")
        self.request.session.changed()
        if self.valid_msg:
            self.request.session.flash(self.valid_msg)
        return self.redirect(come_from)

    def cancel_success(self, appstruct):
        """
        Handle successfull cancellation of the form
        """
        come_from = appstruct.pop("come_from", None)
        # Si come_from est None, dans 99% des cas on sera dans une PopUp
        # Et la popupview mixin se chargera de fermer simplement la popup
        return self.redirect(come_from)

    cancel_failure = cancel_success


class FileEditView(FileUploadView):
    """
    View for file object modification

    Current context is the file itself

    a `class:caerp.events.files.FileUpdated` is fired on file modification
    """

    valid_msg = EDIT_OK_MSG
    edit = True

    @property
    def title(self):
        """
        The form title
        """
        return "Modifier le fichier {0}".format(self.context.name)

    def get_context(self):
        """Allow to override the context we attach the file to"""
        return self.context

    def _get_form_initial_data(self):
        come_from = self.request.referrer
        appstruct = {"come_from": come_from}
        appstruct.update(self.controller.file_to_appstruct(self.context))
        return appstruct

    def before(self, form):
        fileupload_js.need()
        appstruct = self._get_form_initial_data()
        form.set_appstruct(appstruct)


def get_add_file_link(
    request,
    label="Attacher un fichier",
    perm=PERMISSIONS["context.add_file"],
    route=None,
):
    """
    Add a button for file attachment
    """
    context = request.context
    route = route or context.type_
    return ViewLink(
        label, perm, path=route, id=context.id, _query=dict(action="attach_file")
    )


class FileDeleteView(DeleteView, FileViewRedirectMixin):
    """
    a `class:caerp.events.files.FileDeleted` is fired on file deletion
    """

    delete_msg = None

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller = FileController(self.request, edit=True)

    def delete(self):
        self.controller.delete()

    def redirect(self):
        if self.request.is_popup:
            self.add_popup_response()
            return self.request.response
        else:
            back_url = self.back_url()
            if back_url:
                return HTTPFound(back_url)


class BaseZipFileView(BaseView):
    """
    Base Zip File View, allows to produce an archive with multiple files

    E.g :


    """

    def filename(self) -> str:
        return "archive.zip"

    def collect_files(self) -> List[File]:
        """Collect the File objects to include in the archive"""
        raise NotImplementedError()

    def produce_archive(self, files: List[File]) -> io.BytesIO:
        result = mk_zip(files)
        return result

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        files = self.collect_files()
        zipcontent_buffer = self.produce_archive(files)
        write_file_to_request(
            self.request, self.filename(), zipcontent_buffer, "application/zip"
        )
        return self.request.response


def includeme(config):
    """
    Configure views
    """
    config.add_view(
        FileUploadView,
        route_name=NODE_FILE_ROUTE,
        permission=PERMISSIONS["context.add_file"],
        renderer="base/formpage.mako",
    )
    config.add_view(
        FileView,
        route_name=FILE_ITEM,
        permission=PERMISSIONS["context.view_file"],
        renderer="file.mako",
    )
    config.add_view(
        file_dl_view,
        route_name=FILE_PNG_ITEM,
        permission=PERMISSIONS["context.view_file"],
    )
    config.add_view(
        file_dl_view,
        route_name=FILE_ITEM,
        permission=PERMISSIONS["context.view_file"],
        request_param="action=download",
    )
    config.add_view(
        file_stream_view,
        route_name=FILE_ITEM,
        permission=PERMISSIONS["context.view_file"],
        request_param="action=stream",
    )
    config.add_view(
        file_dl_view,
        route_name=PUBLIC_ITEM,
        permission=PERMISSIONS["context.view_file"],
    )
    config.add_view(
        FileEditView,
        route_name=FILE_ITEM,
        permission=PERMISSIONS["context.edit_file"],
        renderer="base/formpage.mako",
        request_param="action=edit",
    )
    config.add_view(
        FileDeleteView,
        route_name=FILE_ITEM,
        permission=PERMISSIONS["context.delete_file"],
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )
