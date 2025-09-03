import logging
from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from caerp.models.project import Phase
from caerp.forms import merge_session_with_post
from caerp.forms.project import PhaseSchema
from caerp.models.project.project import Project
from caerp.views import BaseFormView
from caerp.views.project.routes import (
    PROJECT_ITEM_ROUTE,
    PHASE_ITEM_ROUTE,
    PROJECT_ITEM_PHASE_ROUTE,
)


log = logger = logging.getLogger(__name__)


class PhaseAddFormView(BaseFormView):
    title = "Ajouter un sous-dossier au dossier"
    schema = PhaseSchema()

    def submit_success(self, appstruct):
        model = Phase()
        model.project_id = self.context.id
        merge_session_with_post(model, appstruct)
        self.dbsession.add(model)
        self.dbsession.flush()
        redirect = self.request.route_path(
            PROJECT_ITEM_PHASE_ROUTE, id=model.project_id, _query={"phase": model.id}
        )
        return HTTPFound(redirect)


class PhaseEditFormView(BaseFormView):
    title = "Modification du sous-dossier"
    schema = PhaseSchema()

    def before(self, form):
        form.set_appstruct(self.context.appstruct())

    def submit_success(self, appstruct):
        merge_session_with_post(self.context, appstruct)
        self.dbsession.merge(self.context)
        redirect = self.request.route_path(
            PROJECT_ITEM_PHASE_ROUTE,
            id=self.context.project_id,
        )
        return HTTPFound(redirect)


def phase_delete_view(context, request):
    redirect = request.route_path(
        PROJECT_ITEM_PHASE_ROUTE,
        id=context.project_id,
    )
    if len(context.tasks) == 0:
        msg = "Le sous-dossier {0} a été supprimé".format(context.name)
        request.dbsession.delete(context)
        request.session.flash(msg)
    else:
        msg = "Impossible de supprimer le sous-dossier {0}, il contient \
des documents".format(
            context.name
        )
        request.session.flash(msg, "error")
    return HTTPFound(redirect)


def includeme(config):
    config.add_view(
        PhaseAddFormView,
        route_name=PROJECT_ITEM_ROUTE,
        request_param="action=addphase",
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.add_phase"],
        layout="default",
        context=Project,
    )
    config.add_view(
        PhaseEditFormView,
        route_name=PHASE_ITEM_ROUTE,
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.edit_phase"],
        context=Phase,
    )
    config.add_view(
        phase_delete_view,
        route_name=PHASE_ITEM_ROUTE,
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.delete_phase"],
        request_param="action=delete",
        context=Phase,
    )
