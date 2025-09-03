import logging
import os

from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm.query import Query

from caerp.consts.permissions import PERMISSIONS
from caerp.models.config import Config
from caerp.forms import flatten_appstruct
from caerp.forms.admin import (
    get_sequence_model_admin,
    build_config_appstruct,
)
from caerp.utils.ascii import (
    camel_case_to_name,
)
from caerp.views import (
    BaseFormView,
    BaseView,
    BaseAddView,
    BaseEditView,
    DisableView,
    DeleteView,
    TreeMixin,
    submit_btn,
    cancel_btn,
)
from caerp.views.render_api import build_icon_str

logger = logging.getLogger(__name__)


class BaseAdminFormView(BaseFormView, TreeMixin):
    add_template_vars = ("message",)
    redirect_route_name = "admin_index"
    info_message = ""

    def get_icon(self, icon_name):
        icon = build_icon_str(self.request, icon_name)
        return "<span class='icon'>{}</span>".format(icon)

    @property
    def message(self):
        return self.info_message

    def __call__(self):
        self.populate_navigation()
        return BaseFormView.__call__(self)


class BaseConfigView(BaseAdminFormView):
    """
    Base view for configuring elements in the config key-value table
    """

    keys = ()
    validation_msg = "Vos modifications ont été enregistrées"
    schema = None
    redirect_route_name = None
    buttons = (submit_btn, cancel_btn)

    def before(self, form):
        appstruct = build_config_appstruct(self.request, self.keys)
        form.set_appstruct(appstruct)

    def _get_redirect(self):
        result = None
        if self.redirect_route_name is not None:
            result = HTTPFound(self.request.route_path(self.redirect_route_name))
        else:
            back_link = self.back_link
            if back_link is not None:
                result = HTTPFound(self.back_link)
            else:
                logger.error(
                    "This view %s is not able to provide a back_link "
                    "after validation" % self
                )
        return result

    def submit_success(self, appstruct):
        """
        Handle successfull configuration
        """
        appstruct = flatten_appstruct(appstruct)
        for key in self.keys:
            value = appstruct.pop(key, None)
            if value is None:
                continue

            cfg_obj = Config.get(key) or Config(name=key)
            cfg_obj.value = value

            self.dbsession.add(cfg_obj)

            logger.debug(" # Setting configuration")
            logger.debug("{0} : {1}".format(key, value))
        self.request.session.flash(self.validation_msg)
        return self._get_redirect()

    def cancel_success(self, appstruct):
        return self._get_redirect()


class AdminOption(BaseAdminFormView):
    """
    Main view for option configuration
    It allows to configure a sequence of models

        factory

            The model we are manipulating.

        disable

            True : If the model has an "active" column, it can be used to
            enable/disable elements  (default)
            False : Elements are deleted

        validation_msg

            The message shown to the end user on successfull validation

        redirect_route_name

            The route we're redirecting to after successfull validation

        js_resources

            specific fanstatic javascript resources we want to add to the page

        widget_options

            Options passed to the sequence widget used here

        customize_schema

            Method taking schema as parameter that allows to customize the
            given schema by, for example, adding a global validator
    """

    title = ""
    validation_msg = ""
    factory = None
    disable = True
    show_active_only = False
    js_resources = []
    widget_options = {}
    buttons = (submit_btn, cancel_btn)

    def __init__(self, *args, **kwargs):
        BaseAdminFormView.__init__(self, *args, **kwargs)
        if not hasattr(self, "_schema"):
            self._schema = None

    def customize_schema(self, schema):
        return schema

    def get_schema(self):
        return None

    @property
    def schema(self):
        if self._schema is None:
            self._schema = self.get_schema()
            if self._schema is None:
                self._schema = get_sequence_model_admin(
                    self.factory,
                    "",
                    widget_options=self.widget_options,
                )
            self._schema.title = self.title
            self.customize_schema(self._schema)
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    @property
    def message(self):
        """
        Return an optionnal message to help to configure datas
        """
        help_msg = getattr(self, "help_msg", None)
        if help_msg is None:
            calchemy_dict = getattr(self.factory, "__colanderalchemy_config__", {})
            help_msg = calchemy_dict.get("help_msg", "")
        return help_msg

    def before(self, form):
        """
        Populate the form with existing elements
        """
        if not hasattr(self.js_resources, "__iter__"):
            self.js_resources = (self.js_resources,)

        for js_resource in self.js_resources:
            js_resource.need()

        form.set_appstruct(self.get_appstruct())

    def query_items(self):
        """
        the query used to retrieve items in the database.
        when show_acive_only is True, filters on active items.
        :results: a list of element we want to display as default in the form
        :rtype: list
        """
        query = self.factory.query()

        # Only select active items when show_active_only
        if (
            self.disable is True
            and self.show_active_only
            and hasattr(self.factory, "active")
        ):
            query = query.filter(self.factory.active == True)

        return query.all()

    def get_appstruct(self):
        """
        Return the appstruct used to generate default form entries
        :results: A data structure (list or dict) representing the existing
        datas
        :rtype: dict or list
        """
        return self.schema.dictify(self.query_items())

    def _get_edited_elements(self, appstruct):
        """
        Return the elements that are edited (already have an id)
        """
        return dict(
            (data["id"], data) for data in appstruct.get("datas", {}) if "id" in data
        )

    def _disable_or_remove_elements(self, appstruct):
        """
        Disable or delete existing elements that are no more in the results

        :param appstruct: The validated form datas
        """
        edited = self._get_edited_elements(appstruct)

        for element in self.query_items():
            if element.id not in list(edited.keys()):
                if self.disable:
                    element.active = False
                    self.dbsession.merge(element)
                else:
                    self.dbsession.delete(element)

    def _add_or_edit(self, index, datas):
        """
        Add or edit an element of the given factory
        """
        node_schema = self.schema.children[0].children[0]
        element = node_schema.objectify(datas)
        element.order = index
        if element.id is not None:
            element = self.dbsession.merge(element)
        else:
            self.dbsession.add(element)
        return element

    def submit_success(self, appstruct):
        """
        Handle successfull submission
        """
        self._disable_or_remove_elements(appstruct)

        for index, datas in enumerate(appstruct.get("datas", [])):
            self._add_or_edit(index, datas)

        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.redirect_route_name))

    def cancel_success(self, appstruct):
        return HTTPFound(self.request.route_path(self.redirect_route_name))


def get_model_admin_view(
    model,
    js_requirements=[],
    r_path="admin_userdatas",
    only_active=False,
    can_disable=True,
    permission=None,
):
    """
    Return a view object and a route_name for administrating a sequence of
    models instances (like options)
    """
    infos = model.__colanderalchemy_config__
    view_title = infos.get("title", "Titre inconnu")

    subroute_name = camel_case_to_name(model.__name__)
    view_route_name = os.path.join(r_path, subroute_name)
    # On ajoute une variable intermédiaire pour éviter une erreur "undefined"
    perm = permission

    class MyView(AdminOption):
        title = view_title
        description = infos.get("description", "")
        route_name = view_route_name

        validation_msg = infos.get("validation_msg", "")
        factory = model
        redirect_route_name = r_path
        js_resources = js_requirements
        show_active_only = only_active
        disable = can_disable
        permission = perm

    return MyView


def make_enter_point_view(parent_route, views_to_link_to, title=""):
    """
    Builds a view with links to the views passed as argument

        views_to_link_to

            list of 2-uples (view_obj, route_name) we'd like to link to

        parent_route

            route of the parent page
    """

    def myview(request):
        """
        The dinamycally built view
        """
        menus = []
        menus.append(dict(label="Retour", route_name=parent_route, icon="arrow-left"))
        for view, route_name, tmpl in views_to_link_to:
            menus.append(
                dict(
                    label=view.title,
                    route_name=route_name,
                )
            )
        return dict(title=title, menus=menus)

    return myview


class AdminCrudListView(BaseView, TreeMixin):
    title = "Missing title"
    columns = []

    def _get_item_url(self, item, action=None):
        """
        Build an url to an item's action

        Usefull from inside the stream_actions method

        :param obj item: An instance with an id
        :param str action: The name of the action
        (duplicate/disable/edit...)

        :returns: An url
        :rtype: str
        """
        if not hasattr(self, "item_route_name"):
            raise NotImplementedError("Un attribut item_route_name doit être défini")

        query = dict(self.request.GET)
        if action is not None:
            query["action"] = action

        return self.request.route_path(
            self.item_route_name, id=item.id, _query=query, **self.request.matchdict
        )

    def get_actions(self, items):
        """
        Return additionnal list related actions (other than add)

        :returns: An iterator providing caerp.utils.widgets.Link instances

        :rtype: iterator
        """
        return []

    def get_icon(self, name):
        """
        Build a <span> tag rendering the icon with given name
        """
        icon = build_icon_str(self.request, name)
        return "<span class='icon'>{}</span>".format(icon)

    def get_addurl(self):
        """
        Build the url to the add form
        Override and return None if you don't want an add button

        :returns: An url string
        :rtype: str
        """
        return self.request.route_path(self.route_name, _query={"action": "add"})

    def stream_columns(self, item):
        """
        Each item is a row in a table, here we stream the different columns for
        the given row except the actions column

        :param obj item: A SQLAlchemy model instance
        :returns: an iterator (can be used in a for loop) of column contents
        :rtype: iterator
        """
        raise NotImplementedError()

    def stream_actions(self, item):
        """
        For each column, we stream an action corresponding to it

        :param item: the SQLAlchemy model we wish to have action for
        :returns: List of 4uples (url, label, title, icon)
        """
        raise NotImplementedError()

    def load_items(self):
        """
        Perform the listing query and return the result

        :returns: List of SQLAlchemy object to present in the UI
        :rtype: obj
        """
        raise NotImplementedError()

    def more_template_vars(self, result):
        """
        Add template vars to the result

        :param dict result: The currently built dict that will be returned as
        templating context
        :returns: The templating context for the given view
        :rtype: dict
        """
        return result

    def __call__(self):
        items = self.load_items()
        # We ensure we return a list
        if isinstance(items, Query):
            items = items.all()

        self.populate_navigation()

        result = dict(
            title=self.title,
            addurl=self.get_addurl(),
            columns=self.columns,
            items=items,
            stream_columns=self.stream_columns,
            stream_actions=self.stream_actions,
        )
        result["actions"] = self.get_actions(items)

        if hasattr(self, "more_template_vars"):
            self.more_template_vars(result)

        return result


class BaseAdminIndexView(BaseView, TreeMixin):
    """
    Base admin view

    Used to manage Admin view hierachies


    add_template_vars

        property or attribute names to add to the templating context dict

    """

    add_template_vars = ()
    permission = PERMISSIONS["global.access_admin"]

    def more_template_vars(self, result):
        for propname in self.add_template_vars:
            result[propname] = getattr(self, propname)
        return result

    def __call__(self):
        self.populate_navigation()
        result = dict(
            title=self.title,
            navigation=self.navigation,
        )
        result = self.more_template_vars(result)
        return result


class BaseAdminAddView(BaseAddView, TreeMixin):
    title = "Ajoutez"
    add_template_vars = ("help_msg",)

    buttons = (submit_btn, cancel_btn)

    def __call__(self):
        self.populate_navigation()
        return BaseAddView.__call__(self)

    def redirect(self, appstruct, model=None):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(
                "This view %s is not able to provide a back_link "
                "after validation" % self
            )
            result = None
        return result

    def cancel_success(self, appstruct):
        return self.redirect(appstruct)


class BaseAdminEditView(BaseEditView, TreeMixin):
    add_template_vars = ("help_msg",)

    buttons = (submit_btn, cancel_btn)

    def __call__(self):
        self.populate_navigation()
        return BaseEditView.__call__(self)

    def redirect(self, appstruct):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(
                "This view %s is not able to provide a back_link "
                "after validation" % self
            )
            result = None
        return result

    def cancel_success(self, appstruct):
        return self.redirect(appstruct)


class BaseAdminDisableView(DisableView, TreeMixin):
    def redirect(self):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(
                "This view %s is not able to provide a back_link "
                "after validation" % self
            )
            result = None
        return result


class BaseAdminDeleteView(DeleteView, TreeMixin):
    def redirect(self):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(
                "This view %s is not able to provide a back_link "
                "after validation" % self
            )
            result = None
        return result
