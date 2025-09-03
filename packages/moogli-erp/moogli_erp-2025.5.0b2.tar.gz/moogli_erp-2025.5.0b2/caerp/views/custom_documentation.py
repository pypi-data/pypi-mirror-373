import logging

from pyramid.httpexceptions import HTTPFound
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.consts.permissions import PERMISSIONS
from caerp.views import (
    BaseListView,
    BaseAddView,
    BaseEditView,
    DeleteView,
    submit_btn,
    cancel_btn,
)
from caerp.models.custom_documentation import CustomDocumentation
from caerp.forms.custom_documentation import CustomDocumentationSchema

logger = logging.getLogger(__name__)

edit_perm = PERMISSIONS["global.config_cae"]


class CustomDocumentationList(BaseListView):
    title = "Documents de la CAE"
    use_paginate = False
    default_sort = "updated_at"
    sort_columns = {"updated_at": "updated_at"}
    default_direction = "desc"
    add_template_vars = ("stream_actions",)
    item_route_name = "custom_documentation"

    schema = None

    def query(self):
        query = CustomDocumentation.query()
        return query

    def stream_actions(self, item):
        if not self.request.has_permission(edit_perm):
            return
        yield Link(
            self._get_item_url(item, action="edit"),
            "Voir/Modifier",
            icon="pen",
            css="icon",
        )
        yield POSTButton(
            self._get_item_url(item, action="delete"),
            "Supprimer",
            icon="trash-alt",
            css="icon negative",
            confirm="Êtes vous sûr de vouloir supprimer ?",
        )


class CustomDocumentationAdd(BaseAddView):
    title = "Ajouter une documentation"
    schema = CustomDocumentationSchema
    model = CustomDocumentation
    redirect_route = "custom_documentations"

    def create_instance(self):
        return CustomDocumentation()


class CustomDocumentationEdit(BaseEditView):
    title = "Modifier une documentation"
    schema = CustomDocumentationSchema
    buttons = (submit_btn, cancel_btn)
    add_template_vars = ("title", "help_msg")
    redirect_route = "custom_documentations"
    cancel_failure = BaseEditView.cancel_success  # why !?

    def submit_success(self, appstruct):
        model = self.get_context_model()
        previous_document = model.document
        model = self.merge_appstruct(appstruct, model)

        if model.document is None:
            if previous_document:
                logger.info("deleting the document")
                self.dbsession.delete(previous_document)

        self.dbsession.merge(model)

        self.dbsession.flush()
        if self.msg:
            self.request.session.flash(self.msg)

        return HTTPFound(self.request.route_path(self.redirect_route))


class CustomDocumentationDelete(DeleteView):
    redirect_route = "custom_documentations"


def add_routes(config):
    config.add_route(
        "custom_documentations",
        "/custom_documentation/",
    )
    config.add_route("custom_documentation_create", "/custom_documentation/create")
    config.add_route(
        "custom_documentation",
        r"/custom_documentation/{id:\d+}",
        traverse="/custom_documentations/{id}",
    )


def add_views(config):
    config.add_view(
        CustomDocumentationList,
        route_name="custom_documentations",
        renderer="custom_documentation.mako",
    )
    config.add_view(
        CustomDocumentationAdd,
        route_name="custom_documentation_create",
        renderer="base/formpage.mako",
        permission=edit_perm,
    )
    config.add_view(
        CustomDocumentationEdit,
        route_name="custom_documentation",
        renderer="base/formpage.mako",
        permission=edit_perm,
        request_param="action=edit",
    )
    config.add_view(
        CustomDocumentationDelete,
        route_name="custom_documentation",
        renderer="base/formpage.mako",
        permission=edit_perm,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )


def add_menu(config):
    config.add_admin_menu(
        parent="help",
        order=1,
        label="Documentation de ma CAE",
        route_name="custom_documentations",
    )
    config.add_company_menu(
        parent="help",
        order=1,
        label="Documentation de ma CAE",
        route_name="custom_documentations",
    )


def includeme(config):
    add_routes(config)
    add_views(config)
    add_menu(config)
