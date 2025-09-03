import logging

from deform_extensions import AccordionFormWidget
from js.deform import auto_need
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm import load_only

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.files import get_userdata_file_upload_schema
from caerp.forms.training.trainer import (
    get_add_edit_trainerdatas_schema,
    FORM_GRID,
)
from caerp.models import files
from caerp.models.training.trainer import TrainerDatas
from caerp.models.user.user import User
from caerp.resources import fileupload_js
from caerp.utils.menu import AttrMenuDropdown
from caerp.utils.strings import format_account
from caerp.views import (
    BaseView,
    BaseEditView,
    DeleteView,
    submit_btn,
    cancel_btn,
)
from caerp.views.files.views import FileUploadView
from caerp.views.user.routes import USER_ITEM_URL
from caerp.views.userdatas.filelist import UserDatasFileEditView
from caerp.views.training.routes import (
    USER_TRAINER_FILE_EDIT_URL,
    USER_TRAINER_URL,
    USER_TRAINER_EDIT_URL,
    USER_TRAINER_DELETE_URL,
    USER_TRAINER_FILE_URL,
    USER_TRAINER_ADD_URL,
)


logger = logging.getLogger(__name__)


def trainerdatas_add_entry_view(context, request):
    """
    Trainer datas add view

    :param obj context: The pyramid context (User instance)
    :param obj request: The pyramid request
    """
    logger.debug("Adding Trainer datas for the user %s" % context.id)
    trainerdatas = TrainerDatas(user_id=context.id)
    request.dbsession.add(trainerdatas)
    request.dbsession.flush()
    if context.login is not None:
        context.login.groups.append("trainer")
        request.dbsession.merge(context.login)
    return HTTPFound(
        request.route_path(
            USER_TRAINER_EDIT_URL,
            id=context.id,
        )
    )


class UserTrainerDatasEditView(BaseEditView):
    """
    Trainer datas edition view
    """

    schema = get_add_edit_trainerdatas_schema()
    buttons = (
        submit_btn,
        cancel_btn,
    )
    add_template_vars = ("delete_url", "current_trainerdatas")

    @property
    def delete_url(self):
        return self.request.route_path(
            USER_TRAINER_DELETE_URL,
            id=self.context.id,
        )

    @property
    def current_trainerdatas(self):
        return self.get_context_model()

    @property
    def title(self):
        return "Fiche formateur de {0}".format(format_account(self.context))

    def before(self, form):
        BaseEditView.before(self, form)
        auto_need(form)
        form.widget = AccordionFormWidget(named_grids=FORM_GRID)

    def get_context_model(self):
        return self.context.trainerdatas

    def redirect(self, appstruct):
        return HTTPFound(self.request.current_route_path())


class UserTrainerDatasDeleteView(DeleteView):
    """
    TrainerDatas deletion view
    """

    delete_msg = "La fiche formateur a bien été supprimée"

    def on_delete(self):
        login = self.context.login
        if login is not None:
            if "trainer" in login.groups:
                login.groups.remove("trainer")
                self.request.dbsession.merge(login)

    def delete(self):
        self.dbsession.delete(self.context.trainerdatas)

    def redirect(self):
        return HTTPFound(self.request.route_path(USER_ITEM_URL, id=self.context.id))


class UserTrainerDatasFileAddView(FileUploadView):
    factory = files.File
    title = "Attacher un fichier à la fiche formateur de l’entrepreneur"

    def get_schema(self):
        schema = super().get_schema()
        # Ici on supprime le champ parent_id qui n'est pas utilisé ici
        # En effet, dans le save plus bas on passe le trainerdatas pour
        # l'attachement du fichier
        if "parent_id" in schema:
            del schema["parent_id"]
        return schema

    def before(self, form):
        fileupload_js.need()
        appstruct = {
            "come_from": self.request.referrer,
        }
        form.set_appstruct(appstruct)

    def save(self, appstruct):
        return self.controller.save(appstruct, self.context.trainerdatas)


class UserTrainerDatasFileEditView(UserDatasFileEditView):
    def get_schema(self):
        return get_userdata_file_upload_schema(
            self.request, excludes=("career_path_id",)
        )


class UserTrainerDatasFileList(BaseView):
    @property
    def current_trainerdatas(self):
        return self.context.trainerdatas

    def _get_add_url(self):
        """
        Build the url to the file add view
        """
        return self.request.route_path(
            USER_TRAINER_FILE_URL,
            id=self.context.id,
            _query=dict(action="attach_file"),
        )

    def __call__(self):
        query = files.File.query().options(
            load_only(
                "description",
                "name",
                "updated_at",
                "id",
            )
        )
        query = query.filter_by(parent_id=self.current_trainerdatas.id)

        visited_user = self.current_trainerdatas.user

        if visited_user.id == self.request.identity.id:
            help_msg = (
                "Liste des documents liés à mon statut de formateur."
                " Ces documents sont visibles, déposables et modifiables par moi comme "
                "par l'équipe d'appui."
            )
        else:
            help_msg = (
                "Liste des documents liés au statut de formateur "
                "de l’entrepreneur. Ces documents sont visibles, déposables et "
                "modifiables par l’entrepreneur."
            )
        return dict(
            title="Documents formateur",
            files=query,
            current_trainerdatas=self.current_trainerdatas,
            add_url=self._get_add_url(),
            help_message=help_msg,
        )


def add_views(config):
    config.add_view(
        trainerdatas_add_entry_view,
        route_name=USER_TRAINER_ADD_URL,
        request_method="POST",
        require_csrf=True,
        context=User,
        permission=PERMISSIONS["global.view_training"],
    )
    config.add_view(
        UserTrainerDatasEditView,
        route_name=USER_TRAINER_EDIT_URL,
        renderer="caerp:templates/training/trainerdatas_edit.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["context.edit_trainerdata"],
    )
    config.add_view(
        UserTrainerDatasFileList,
        route_name=USER_TRAINER_FILE_URL,
        renderer="caerp:templates/training/filelist.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["context.edit_trainerdata"],
    )
    config.add_view(
        UserTrainerDatasFileAddView,
        route_name=USER_TRAINER_FILE_URL,
        request_param="action=attach_file",
        layout="default",
        renderer="caerp:templates/base/formpage.mako",
        context=User,
        permission=PERMISSIONS["context.edit_trainerdata"],
    )
    config.add_view(
        UserTrainerDatasFileEditView,
        route_name=USER_TRAINER_FILE_EDIT_URL,
        layout="default",
        renderer="caerp:templates/base/formpage.mako",
        context=files.File,
        permission=PERMISSIONS["context.edit_file"],
    )

    config.add_view(
        UserTrainerDatasDeleteView,
        route_name=USER_TRAINER_DELETE_URL,
        layout="default",
        request_method="POST",
        require_csrf=True,
        context=User,
        permission=PERMISSIONS["global.view_training"],
    )


TRAINER_MENU = AttrMenuDropdown(
    name="trainerdatas",
    label="Formation",
    default_route=USER_TRAINER_URL,
    icon="chalkboard-teacher",
    hidden_attribute="trainerdatas",
    perm=[
        PERMISSIONS["context.view_trainerdata"],
    ],
)
TRAINER_MENU.add_item(
    name="trainerdatas_view",
    label="Fiche formateur",
    route_name=USER_TRAINER_EDIT_URL,
    icon="user-circle",
    perm=PERMISSIONS["context.edit_trainerdata"],
)
TRAINER_MENU.add_item(
    name="trainerdatas_filelist",
    label="Fichiers liés au formateur",
    route_name=USER_TRAINER_FILE_URL,
    icon="folder",
    perm=PERMISSIONS["context.view_trainerdata"],
)


def register_menus():
    from caerp.views.user.layout import UserMenu

    UserMenu.add(TRAINER_MENU)


def includeme(config):
    """
    Pyramid main entry point

    :param obj config: The current application config object
    """
    add_views(config)
    register_menus()
    config.add_admin_menu(
        parent="training",
        order=2,
        href="/trainers",
        label="Annuaire des formateurs",
        permission=PERMISSIONS["global.view_training"],
    )
