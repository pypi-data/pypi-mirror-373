import logging

from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm import (
    Load,
    joinedload,
)


from caerp.models import career_path
from caerp.models.user.user import User
from caerp.utils.widgets import Link, POSTButton
from caerp.views import (
    BaseFormView,
    BaseView,
    DeleteView,
)
from caerp.utils.strings import format_account
from caerp.models.files import File
from caerp.models.career_path import CareerPath, CareerPathFileRel
from caerp.models.user import Login, UserDatas
from caerp.utils.notification.career_path import notify_career_path_end_date
from caerp.forms.user.career_path import (
    get_add_stage_schema,
    get_edit_stage_schema,
)
from caerp.views.user.routes import USER_LOGIN_ADD_URL
from caerp.views.user.tools import UserFormConfigState
from caerp.views.userdatas.routes import (
    CAREER_PATH_URL,
    USER_USERDATAS_CAREER_PATH_URL,
)

logger = logging.getLogger(__name__)


class CareerPathList(BaseView):
    """
    List of career path stages
    """

    @property
    def current_userdatas(self):
        return self.context

    def stream_actions(self, item):
        if self.request.has_permission(PERMISSIONS["global.edit_userdata_career"]):
            yield Link(
                url=self.request.route_url(
                    CAREER_PATH_URL, id=item.id, _query=dict(action="edit")
                ),
                label="Modifier",
                title="Modifier cette étape",
                icon="pen",
                css="btn icon only",
            )

            yield POSTButton(
                url=self.request.route_url(
                    CAREER_PATH_URL, id=item.id, _query=dict(action="delete")
                ),
                label="Supprimer",
                title="Supprimer cette étapes",
                icon="trash-alt",
                css="negative icon only",
            )

    def add_button(self):
        if self.request.has_permission(PERMISSIONS["global.edit_userdata_career"]):
            return Link(
                url=self.request.route_url(
                    USER_USERDATAS_CAREER_PATH_URL,
                    id=self.context.id,
                    _query=dict(action="new"),
                ),
                label="Ajouter une étape",
                title="Ajouter une nouvelle étape de parcours",
                icon="plus",
                css="btn icon only",
            )
        return None

    def get_js_onclick(self, item):
        if self.request.has_permission(PERMISSIONS["global.edit_userdata_career"]):
            return "document.location='{}'".format(
                self.request.route_url(
                    CAREER_PATH_URL, id=item.id, _query=dict(action="edit")
                )
            )
        return "return false;"

    def __call__(self):
        path_query = CareerPath.query(self.current_userdatas.id)
        path_query = path_query.options(
            Load(CareerPath).load_only("start_date", "id"),
            joinedload("career_stage").load_only("name"),
        )
        return dict(
            career_path=path_query.all(),
            user=self.current_userdatas.user,
            title="Parcours de {0}".format(
                format_account(self.current_userdatas.user, False)
            ),
            add_button=self.add_button(),
            stream_actions=self.stream_actions,
            get_js_onclick=self.get_js_onclick,
        )


class UserCareerPathList(CareerPathList):
    @property
    def current_userdatas(self):
        return self.context.userdatas


class CareerPathAddStage(BaseFormView):
    """
    Career path add stage view
    """

    title = "Ajout d'une nouvelle étape"
    schema = get_add_stage_schema()

    @property
    def current_userdatas(self) -> UserDatas:
        return self.context

    def submit_success(self, appstruct):
        model = self.schema.objectify(appstruct)
        model.userdatas_id = self.current_userdatas.id
        self.dbsession.add(model)
        self.dbsession.flush()

        # Update CareerPath with chosen CareerStage's data
        model.cae_situation_id = model.career_stage.cae_situation_id
        model.stage_type = model.career_stage.stage_type
        model = self.dbsession.merge(model)
        self.dbsession.flush()

        # Redirect to login or stage's edition if needed
        dest_route = self.request.current_route_path(_query="")
        msg = "L'étape de parcours a bien été ajoutée"
        if model.career_stage.cae_situation is not None:
            if model.career_stage.cae_situation.is_integration:
                login = (
                    Login.query()
                    .filter(Login.user_id == self.context.userdatas.user_id)
                    .first()
                )
                if login is None:
                    config = UserFormConfigState(self.request.session)
                    config.set_defaults({"account_type": "entrepreneur"})
                    dest_route = self.request.route_path(
                        USER_LOGIN_ADD_URL, id=self.context.userdatas.user_id
                    )
                    msg = "L'étape de parcours a bien été ajoutée, \
vous devez maintenant créer les identifiants de l'utilisateur"

        if model.stage_type is not None:
            if model.stage_type in ("contract", "amendment", "exit"):
                dest_route = self.request.route_path(
                    CAREER_PATH_URL, id=model.id, _query=""
                )
        if model.stage_type in ("contract", "amendment", "entry"):
            notify_career_path_end_date(
                self.request, self.current_userdatas.user, career_path=model
            )

        self.session.flash(msg)
        return HTTPFound(dest_route)


class UserCareerPathAddStage(CareerPathAddStage):
    @property
    def current_userdatas(self):
        return self.context.userdatas


class CareerPathEditStage(BaseFormView):
    """
    Career path edit stage view
    """

    title = "Modification d'une étape de parcours"
    _schema = None
    files = None
    add_template_vars = ("files",)

    @property
    def current_userdatas(self):
        return self.context.userdatas

    # Schema is here a property since we need to build it dynamically
    # regarding the current request
    @property
    def schema(self):
        """
        The getter for our schema property
        """
        if self._schema is None:
            self._schema = get_edit_stage_schema(self.context.stage_type)

            if self.context.career_stage:
                self._schema.title = self.context.career_stage.name
                if self.context.cae_situation is not None:
                    self._schema.title += " ( => {})".format(
                        self.context.cae_situation.label
                    )
            else:
                if self.context.cae_situation is not None:
                    self._schema.title = "Changement de situation : {}".format(
                        self.context.cae_situation.label
                    )
        return self._schema

    @schema.setter
    def schema(self, value):
        """
        A setter for the schema property
        The BaseClass in pyramid_deform gets and sets the schema attribute
        that is here transformed as a property
        """
        self._schema = value

    def before(self, form):
        appstruct = self.request.context.appstruct()
        form.set_appstruct(appstruct)
        query = File.query().join(
            CareerPathFileRel, File.id == CareerPathFileRel.file_id
        )
        query = query.filter_by(career_path_id=self.context.id)
        self.files = query.all()

    def submit_success(self, appstruct):
        model = self.schema.objectify(appstruct)
        model.userdatas_id = self.current_userdatas.id
        model = self.dbsession.merge(model)
        self.dbsession.flush()
        self.session.flash("L'étape de parcours a bien été enregistrée")
        dest = USER_USERDATAS_CAREER_PATH_URL

        # Redirect to login management if new CAE situation is integration and
        # no active login
        if self.context.cae_situation is not None:
            if self.context.cae_situation.is_integration:
                login = (
                    Login.query()
                    .filter(Login.user_id == self.context.userdatas.user_id)
                    .first()
                )
                if login is None:
                    dest = USER_LOGIN_ADD_URL

        if model.stage_type in ("contract", "amendment", "entry"):
            notify_career_path_end_date(
                self.request,
                self.current_userdatas.user,
                career_path=model,
                update=True,
            )
        return HTTPFound(
            self.request.route_path(dest, id=self.context.userdatas.user_id)
        )


class UserCareerPathEditStage(CareerPathEditStage):
    @property
    def current_userdatas(self):
        return self.context.userdatas


class CareerPathDeleteStage(DeleteView):
    """
    Career path delete stage view
    """

    delete_msg = "L'étape a bien été supprimée"

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                USER_USERDATAS_CAREER_PATH_URL, id=self.context.userdatas.user_id
            )
        )


def add_views(config):
    """
    Add career path related views
    """
    config.add_view(
        UserCareerPathList,
        route_name=USER_USERDATAS_CAREER_PATH_URL,
        renderer="/userdatas/career_path.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["context.view_userdata"],
    )

    config.add_view(
        UserCareerPathAddStage,
        route_name=USER_USERDATAS_CAREER_PATH_URL,
        request_param="action=add_stage",
        renderer="/userdatas/career_path_form.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["global.edit_userdata_career"],
    )
    config.add_view(
        CareerPathEditStage,
        route_name=CAREER_PATH_URL,
        renderer="/userdatas/career_path_form.mako",
        layout="user",
        context=CareerPath,
        permission=PERMISSIONS["global.edit_userdata_career"],
    )
    config.add_view(
        CareerPathDeleteStage,
        route_name=CAREER_PATH_URL,
        request_param="action=delete",
        renderer="/userdatas/career_path.mako",
        layout="user",
        context=CareerPath,
        permission=PERMISSIONS["global.edit_userdata_career"],
    )


def includeme(config):
    add_views(config)
