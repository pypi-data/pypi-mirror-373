import logging
import os

from pyramid.httpexceptions import HTTPFound
from sqlalchemy import asc

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.accounting import (
    get_admin_accounting_measure_type_schema,
    get_admin_accounting_type_category_schema,
)
from caerp.forms.admin import get_config_schema
from caerp.models.accounting.income_statement_measures import (
    IncomeStatementMeasureType,
    IncomeStatementMeasureTypeCategory,
)
from caerp.utils.widgets import Link, POSTButton
from caerp.views import BaseView, TreeMixin
from caerp.views.admin.accounting import ACCOUNTING_URL, AccountingIndexView
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminAddView,
    BaseAdminDeleteView,
    BaseAdminDisableView,
    BaseAdminEditView,
    BaseAdminIndexView,
    BaseConfigView,
)

logger = logging.getLogger(__name__)

BASE_URL = os.path.join(ACCOUNTING_URL, "income_statement_measures")

CATEGORY_URL = BASE_URL + "/categories"
GENERAL_CONFIG_URL = BASE_URL + "/config"
CATEGORY_TYPE_ITEM_URL = CATEGORY_URL + "/{id}"

TYPE_INDEX_URL = BASE_URL + "/types"
TYPE_CATEGORY_URL = TYPE_INDEX_URL + "/{category_id}"
TYPE_ITEM_URL = TYPE_CATEGORY_URL + "/{id}"


class IncomeStatementMeasureIndexView(BaseAdminIndexView):
    title = "Comptes de résultat"
    description = (
        "Paramétrer l'état de gestion « Comptes de résultat »"
        " visible par les entrepreneurs."
    )
    route_name = BASE_URL
    permission = PERMISSIONS["global.config_accounting_measure"]


class IncomeStatementGeneralConfigView(BaseConfigView):
    title = "Affichage des comptes de résultat"
    description = "Paramètres d'affichage par défaut des comptes de résultat."

    route_name = GENERAL_CONFIG_URL

    keys = [
        "income_statement_default_show_decimals",
        "income_statement_default_show_zero_rows",
    ]

    schema = get_config_schema(keys)

    info_message = (
        "Paramètres par défaut pour l'<strong>affichage</strong> et les "
        "<strong>exports tableur</strong>"
        " d'un compte de résultat."
        "<br /> <br />"
        "Ils peuvent être changés par l'utilisateur/utilisatrice."
    )
    permission = PERMISSIONS["global.config_accounting_measure"]


class CategoryListView(AdminCrudListView):
    columns = [
        "Libellé de la catégorie",
    ]
    title = "Catégories d'indicateurs de compte de résultat"
    route_name = CATEGORY_URL
    item_route_name = CATEGORY_TYPE_ITEM_URL
    factory = IncomeStatementMeasureTypeCategory
    item_name = "comptes de résultat"
    permission = PERMISSIONS["global.config_accounting_measure"]

    def __init__(self, *args, **kwargs):
        AdminCrudListView.__init__(self, *args, **kwargs)
        self.max_order = self.factory.get_next_order() - 1

    def stream_columns(self, measure_type):
        """
        Stream a column object (called from within the template)

        :param obj measure_type: The object to display
        :returns: A generator of labels representing the different columns of
        our list
        :rtype: generator
        """
        yield measure_type.label

    def stream_actions(self, category):
        """
        Stream the actions available for the given category object
        :param obj catgegory: IncomeStatementMeasureTypeCategory instance
        :returns: List of 4-uples (url, label, title, icon,)
        """
        if category.active:
            yield Link(
                self._get_item_url(category), "Voir/Modifier", icon="pen", css="icon"
            )
            move_url = self._get_item_url(category, action="move")
            if category.order > 0:
                yield POSTButton(
                    move_url + "&direction=up",
                    "Remonter",
                    title="Remonter dans l’ordre des catégories",
                    icon="arrow-up",
                    css="icon",
                )
            if category.order < self.max_order:
                yield POSTButton(
                    move_url + "&direction=down",
                    "Redescendre",
                    title="Redescendre dans l’ordre des catégories",
                    icon="arrow-down",
                    css="icon",
                )

            yield POSTButton(
                self._get_item_url(category, action="disable"),
                "Désactiver",
                title="Les informations associés aux indicateur de cette "
                "catégorie ne seront plus affichées",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(category, action="disable"),
                "Activer",
                title="Les informations générés depuis les indicateurs de "
                "cette catégorie seront affichées",
                icon="lock-open",
                css="icon",
            )
            yield POSTButton(
                self._get_item_url(category, action="delete"),
                "Supprimer",
                title="Supprimer cet indicateurs et les entrées associées",
                icon="trash-alt",
                confirm="Êtes-vous sûr de vouloir supprimer "
                "cet élément ? Tous les éléments dans les {item_name} "
                "ayant été générés depuis des indicateurs seront  également "
                "supprimés.".format(item_name=self.item_name),
                css="icon negative",
            )

    def load_items(self):
        """
        Return the sqlalchemy models representing current queried elements
        :rtype: SQLAlchemy.Query object
        """
        items = self.factory.query()
        items = items.order_by(asc(self.factory.order))
        return items

    def more_template_vars(self, result):
        """
        Hook allowing to add datas to the templating context
        """
        result[
            "help_msg"
        ] = """Les catégories ci-dessous sont utilisées pour
        regrouper des éléments dans la configuration des {item_name}
        des entrepreneurs. Elles permettent la configuration de totaux.
        """.format(
            item_name=self.item_name
        )
        return result


class CategoryAddView(BaseAdminAddView):
    title = "Ajouter"
    route_name = CATEGORY_URL

    factory = IncomeStatementMeasureTypeCategory
    schema = get_admin_accounting_type_category_schema(
        IncomeStatementMeasureTypeCategory, is_edit=False
    )
    permission = PERMISSIONS["global.config_accounting_measure"]

    def before(self, form):
        pre_filled = {"order": self.factory.get_next_order()}
        form.set_appstruct(pre_filled)


class CategoryEditView(BaseAdminEditView):
    factory = IncomeStatementMeasureTypeCategory
    route_name = CATEGORY_TYPE_ITEM_URL
    schema = get_admin_accounting_type_category_schema(
        IncomeStatementMeasureTypeCategory, is_edit=True
    )
    permission = PERMISSIONS["global.config_accounting_measure"]

    @property
    def title(self):
        return "Modifier la catégorie '{0}'".format(self.context.label)


class CategoryDisableView(BaseAdminDisableView):
    """
    View for measure disable/enable
    """

    route_name = CATEGORY_TYPE_ITEM_URL
    factory = IncomeStatementMeasureTypeCategory
    permission = PERMISSIONS["global.config_accounting_measure"]

    def on_disable(self):
        """
        On disable we set order to -1
        """
        self.context.order = -1
        self.request.dbsession.merge(self.context)

    def on_enable(self):
        """
        on enable we set order to 1
        """
        order = self.factory.get_next_order()
        self.context.order = order
        self.request.dbsession.merge(self.context)


class CategoryDeleteView(BaseAdminDeleteView):
    """
    Category deletion view
    """

    route_name = CATEGORY_TYPE_ITEM_URL
    factory = IncomeStatementMeasureTypeCategory
    permission = PERMISSIONS["global.config_accounting_measure"]

    def on_delete(self):
        """
        On disable we reset the order
        """
        self.factory.reorder()


class TypeListIndexView(BaseView, TreeMixin):
    title = "Indicateurs de Compte de résultat"
    route_name = TYPE_INDEX_URL
    category_route_name = TYPE_CATEGORY_URL
    category_class = IncomeStatementMeasureTypeCategory
    help_message = """Les indicateurs de comptes de résultat permettent de
    regrouper les écritures comptables derrière un même libellé afin de les
    regrouper au sein d'un tableau annuel présentant le compte de résultat
    de chaque enseigne.<br />
    Les indicateurs sont divisés en plusieurs catégories. <br />
    Depuis cette interface, vous pouvez configurer, par
    catégorie, l'ensemble des indicateurs qui composeront les comptes de
    résultat de vos entrepreneurs."""
    permission = PERMISSIONS["global.config_accounting_measure"]

    def __call__(self):
        self.populate_navigation()
        navigation = []
        for category in self.category_class.get_categories():
            label = "Catégorie %s" % category.label
            url = self.request.route_path(
                self.category_route_name,
                category_id=category.id,
            )
            navigation.append(Link(label=label, url=url, icon="project-diagram"))

        return dict(
            title=self.title,
            help_message=self.help_message,
            navigation=navigation,
        )


class MeasureTypeListView(AdminCrudListView):
    columns = [
        "Libellé de l'indicateur",
        "Regroupe",
        "Correspond à un total",
        "Convention de signe",
    ]
    factory = IncomeStatementMeasureType
    # category_class can be None for MeasureType having no categories
    category_class = IncomeStatementMeasureTypeCategory
    route_name = TYPE_CATEGORY_URL
    item_route_name = TYPE_ITEM_URL
    item_label = "de compte de résultat"
    permission = PERMISSIONS["global.config_accounting_measure"]

    def __init__(self, *args, **kwargs):
        AdminCrudListView.__init__(self, *args, **kwargs)
        if self.category_class:
            self.max_order = (
                self.factory.get_next_order_by_category(self.context.id) - 1
            )
        else:
            self.max_order = self.factory.get_next_order() - 1

    def _get_current_category(self):
        if not self.category_class:
            return None

        if isinstance(self.context, self.category_class):
            result = self.context
        else:
            result = self.context.category
        return result

    @property
    def title(self):
        return "Indicateurs {} (catégorie {})".format(
            self.item_label,
            self._get_current_category().label,
        )

    @property
    def tree_url(self):
        if self.category_class:
            return self.request.route_path(
                self.route_name, category_id=self._get_current_category().id
            )
        else:
            return self.request.route_path(self.route_name)

    def stream_columns(self, measure_type):
        """
        Stream a column object (called from within the template)

        :param obj measure_type: The object to display
        :returns: A generator of labels representing the different columns of
        our list
        :rtype: generator
        """
        yield measure_type.label
        if measure_type.is_computed_total:
            if measure_type.total_type == "categories":
                yield "La somme des indicateurs des catégories %s" % (
                    measure_type.account_prefix,
                )
            elif measure_type.total_type == "complex_total":
                yield "Le résultat de l'opération : '%s'" % (
                    measure_type.account_prefix,
                )
        else:
            yield "Les comptes : %s" % measure_type.account_prefix
        if measure_type.is_total:
            yield "<span class='icon'><svg><use href='{}#check'></use></svg></span>".format(
                self.request.static_url("caerp:static/icons/icones.svg")
            )
        else:
            yield "<span class='icon'><svg><use href='{}#times'></use></svg></span>".format(
                self.request.static_url("caerp:static/icons/icones.svg")
            )

        if measure_type.is_total:
            if measure_type.total_type != "account_prefix":
                if measure_type.sign() == -1:
                    yield "Inversé"
                else:
                    yield "Non inversé"
            else:
                if measure_type.sign() == -1:
                    yield "Non inversé"
                else:
                    yield "Inversé"
        else:
            if measure_type.sign() == -1:
                yield "Crédit - débit"
            else:
                yield "Débit - crédit"

    def _get_item_url(self, measure_type, action=None):
        """
        shortcut for route_path calls
        """
        query = dict(self.request.GET)
        if action is not None:
            query["action"] = action

        return self.request.route_path(
            self.item_route_name,
            id=measure_type.id,
            category_id=measure_type.category_id,
            _query=query,
        )

    def stream_actions(self, measure_type):
        """
        Stream the actions available for the given measure_type object
        :param obj measure_type: TreasuryMeasureType instance
        :returns: List of 4-uples (url, label, title, icon,)
        """
        if measure_type.active:
            yield POSTButton(
                self._get_item_url(measure_type),
                "Voir/Modifier",
                icon="pen",
                css="icon",
            )
            move_url = self._get_item_url(measure_type, action="move")
            if measure_type.order > 0:
                yield POSTButton(
                    move_url + "&direction=up",
                    "Monter",
                    title="Monter dans l’ordre des indicateurs",
                    icon="arrow-up",
                    css="icon",
                )
            if measure_type.order < self.max_order:
                yield POSTButton(
                    move_url + "&direction=down",
                    "Redescendre",
                    title="Redescendre dans l'ordre des indicateurs",
                    icon="arrow-down",
                    css="icon",
                )

            yield POSTButton(
                self._get_item_url(measure_type, action="disable"),
                "Désactiver",
                title="Les informations associés à cet indicateur ne seront "
                "plus affichées",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(measure_type, action="disable"),
                "Activer",
                title="Les informations générés depuis cet indicateur seront "
                "affichées",
                icon="lock-open",
                css="icon",
            )
            yield POSTButton(
                self._get_item_url(measure_type, action="delete"),
                "Supprimer",
                title="Supprimer cet indicateurs et les entrées associées",
                icon="trash-alt",
                confirm="Êtes-vous sûr de vouloir supprimer "
                "cet élément ? Tous les éléments dans les comptes de résultat "
                "ayant été générés depuis cet indicateur seront  également "
                "supprimés.",
                css="icon negative",
            )

    def load_items(self, year=None):
        """
        Return the sqlalchemy models representing current queried elements
        :rtype: SQLAlchemy.Query object
        """
        if self.category_class:
            items = self.factory.query().filter_by(category_id=self.context.id)
        else:
            items = self.factory.query()
        items = items.order_by(asc(self.factory.order))
        return items

    def more_template_vars(self, result):
        """
        Hook allowing to add datas to the templating context
        """
        result[
            "help_msg"
        ] = """Les définitions ci-dessous indiquent quelles
        écritures sont utilisées pour le calcul des indicateurs de la section
        %s des comptes de résultat des entrepreneurs.<br />
        Les indicateurs seront présentés dans l'ordre.<br />
        Certains indicateurs sont des totaux, ils seront alors mis en évidence
        dans l'interface""" % (
            self.context.label,
        )
        return result

    def get_actions(self, items):
        """
        Return the description of additionnal main actions buttons

        :rtype: list
        """
        yield Link(
            self.get_addurl() + "?is_total=1",
            "Ajouter un total",
            title="Ajouter un indicateur de type total qui sera mis en "
            "évidence dans l'interface",
            icon="plus-circle",
            css="btn",
        )

    def get_addurl(self):
        if self.category_class:
            return self.request.route_path(
                self.route_name + "/add",
                category_id=self.context.id,
            )
        else:
            return self.request.route_path(self.route_name + "/add")


class MeasureTypeAddView(BaseAdminAddView):
    title = "Ajouter"
    route_name = TYPE_CATEGORY_URL + "/add"
    _schema = None
    factory = IncomeStatementMeasureType
    has_category = True
    permission = PERMISSIONS["global.config_accounting_measure"]

    def is_total_form(self):
        return "is_total" in self.request.GET

    @property
    def schema(self):
        if self._schema is None:
            if self.is_total_form():
                self._schema = get_admin_accounting_measure_type_schema(
                    self.factory,
                    is_edit=False,
                    total=True,
                )
            else:
                self._schema = get_admin_accounting_measure_type_schema(
                    self.factory, is_edit=False
                )
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    def before(self, form):
        """
        Launched before the form is used

        :param obj form: The form object
        """
        if self.has_category:
            pre_filled = {
                "category_id": self.context.id,
                "order": self.factory.get_next_order_by_category(self.context.id),
            }
            if "is_total" in self.request.GET:
                pre_filled["is_total"] = True
                pre_filled["label"] = "Total %s" % (self.context.label,)
                pre_filled["categories"] = "%s" % self.context.label
                pre_filled["total_type"] = "categories"
        else:
            pre_filled = {
                "category_id": None,
                "order": self.factory.get_next_order(),
            }

            if "is_total" in self.request.GET:
                from caerp.views.admin.accounting.balance_sheet_measures import (
                    ActiveMeasureTypeAddView,
                    PassiveMeasureTypeAddView,
                )

                if isinstance(self, ActiveMeasureTypeAddView) or isinstance(
                    self, PassiveMeasureTypeAddView
                ):
                    active = True
                    label = "Actif"
                else:
                    active = False
                    label = "Passif"

                pre_filled["is_total"] = True
                pre_filled["label"] = "Total %s" % label
                pre_filled["categories"] = "%s" % label
                pre_filled["total_type"] = "categories"

        form.set_appstruct(pre_filled)

    def merge_appstruct(self, appstruct, model):
        """
        Handle specific form keys when setting the new model's datas

        Regarding the type of total we manage (category total or operation
        specific total), we want to set some attributes
        """
        model = BaseAdminAddView.merge_appstruct(self, appstruct, model)
        if "total_type" in appstruct:
            total_type = appstruct["total_type"]
            model.account_prefix = appstruct[total_type]

        return model


class MeasureTypeEditView(BaseAdminEditView):
    route_name = TYPE_ITEM_URL
    _schema = None
    factory = IncomeStatementMeasureType
    permission = PERMISSIONS["global.config_accounting_measure"]

    @property
    def title(self):
        return "Modifier la définition de l'indicateur '{0}'".format(self.context.label)

    def is_total_form(self):
        return self.context.is_total

    @property
    def schema(self):
        if self._schema is None:
            if self.is_total_form():
                self._schema = get_admin_accounting_measure_type_schema(
                    self.factory,
                    is_edit=True,
                    total=True,
                )
            else:
                self._schema = get_admin_accounting_measure_type_schema(
                    self.factory, is_edit=True
                )
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    def get_default_appstruct(self):
        result = BaseAdminEditView.get_default_appstruct(self)
        if self.is_total_form():
            result["total_type"] = self.context.total_type
            result["account_prefix"] = ""
            result[self.context.total_type] = self.context.account_prefix
        return result

    def merge_appstruct(self, appstruct, model):
        """
        Handle specific form keys when setting the new model's datas

        Regarding the type of total we manage (category total or operation
        specific total), we want to set some attributes
        """
        if "account_prefix" in appstruct:
            appstruct["account_prefix"] = appstruct["account_prefix"].replace(" ", "")
        model = BaseAdminEditView.merge_appstruct(self, appstruct, model)
        if "total_type" in appstruct:
            total_type = appstruct["total_type"]
            model.account_prefix = appstruct[total_type]

        return model


class MeasureDisableView(CategoryDisableView):
    route_name = TYPE_ITEM_URL
    factory = IncomeStatementMeasureType
    permission = PERMISSIONS["global.config_accounting_measure"]

    def on_enable(self):
        """
        on enable we set order to 1
        """
        order = self.factory.get_next_order_by_category(self.context.category_id)
        self.context.order = order
        self.request.dbsession.merge(self.context)


class MeasureDeleteView(CategoryDeleteView):
    """
    View for measure disable/enable
    """

    route_name = TYPE_ITEM_URL
    factory = IncomeStatementMeasureType
    permission = PERMISSIONS["global.config_accounting_measure"]

    def on_delete(self):
        """
        On disable we reset the order
        """
        self.factory.reorder(self.context.category_id)


def move_view(context, request):
    """
    Reorder the current context moving it up in the category's hierarchy

    :param obj context: The given IncomeStatementMeasureType instance
    """
    action = request.params["direction"]
    if action == "up":
        context.move_up()
    else:
        context.move_down()
    return HTTPFound(request.referer)


def add_routes(config):
    """
    Add routes related to this module
    """
    config.add_route(BASE_URL, BASE_URL)
    config.add_route(CATEGORY_URL, CATEGORY_URL)
    config.add_route(GENERAL_CONFIG_URL, GENERAL_CONFIG_URL)
    config.add_route(
        CATEGORY_TYPE_ITEM_URL,
        CATEGORY_TYPE_ITEM_URL,
        traverse="/income_statement_measure_type_categories/{id}",
    )

    config.add_route(TYPE_INDEX_URL, TYPE_INDEX_URL)
    config.add_route(
        TYPE_CATEGORY_URL,
        TYPE_CATEGORY_URL,
        traverse="/income_statement_measure_type_categories/{category_id}",
    )
    config.add_route(
        TYPE_CATEGORY_URL + "/add",
        TYPE_CATEGORY_URL + "/add",
        traverse="/income_statement_measure_type_categories/{category_id}",
    )
    config.add_route(
        TYPE_ITEM_URL,
        TYPE_ITEM_URL,
        traverse="income_statement_measure_types/{id}",
    )


def add_views(config):
    """
    Add views defined in this module
    """
    config.add_admin_view(
        IncomeStatementGeneralConfigView,
        parent=IncomeStatementMeasureIndexView,
    )
    config.add_admin_view(
        IncomeStatementMeasureIndexView,
        parent=AccountingIndexView,
    )
    config.add_admin_view(
        CategoryListView,
        parent=IncomeStatementMeasureIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        CategoryAddView,
        parent=CategoryListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        CategoryEditView,
        parent=CategoryListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        CategoryDisableView,
        parent=CategoryListView,
        request_param="action=disable",
        require_csrf=True,
        request_method="POST",
    )
    config.add_admin_view(
        CategoryDeleteView,
        parent=CategoryListView,
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
    )
    config.add_admin_view(
        move_view,
        route_name=CATEGORY_TYPE_ITEM_URL,
        request_param="action=move",
        require_csrf=True,
        request_method="POST",
    )
    config.add_admin_view(
        TypeListIndexView,
        parent=IncomeStatementMeasureIndexView,
    )
    config.add_admin_view(
        MeasureTypeListView,
        parent=TypeListIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        MeasureTypeAddView,
        parent=MeasureTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        MeasureTypeEditView,
        parent=MeasureTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        MeasureDisableView,
        parent=MeasureTypeListView,
        request_param="action=disable",
        require_csrf=True,
        request_method="POST",
    )
    config.add_admin_view(
        MeasureDeleteView,
        parent=MeasureTypeListView,
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
    )
    config.add_admin_view(
        move_view,
        route_name=TYPE_ITEM_URL,
        request_param="action=move",
        require_csrf=True,
        request_method="POST",
    )


def includeme(config):
    add_routes(config)
    add_views(config)
