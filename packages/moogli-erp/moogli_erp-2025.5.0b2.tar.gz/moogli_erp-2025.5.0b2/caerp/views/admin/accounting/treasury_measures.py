import logging
import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.accounting import get_admin_accounting_type_category_schema
from caerp.forms.admin import get_config_schema
from caerp.models.accounting.treasury_measures import (
    TreasuryMeasureType,
    TreasuryMeasureTypeCategory,
)
from caerp.views.admin.accounting import ACCOUNTING_URL, AccountingIndexView
from caerp.views.admin.accounting.income_statement_measures import (
    CategoryAddView as IncomeStatementCategoryAddView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    CategoryDeleteView as IncomeStatementCategoryDeleteView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    CategoryDisableView as IncomeStatementCategoryDisableView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    CategoryEditView as IncomeStatementCategoryEditView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    CategoryListView as IncomeStatementCategoryListView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    MeasureDeleteView as IncomeStatementMeasureDeleteView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    MeasureDisableView as IncomeStatementMeasureDisableView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    MeasureTypeAddView as IncomeStatementMeasureTypeAddView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    MeasureTypeEditView as IncomeStatementMeasureTypeEditView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    MeasureTypeListView as IncomeStatementMeasureTypeListView,
)
from caerp.views.admin.accounting.income_statement_measures import (
    TypeListIndexView as IncomeStatementTypeListIndexView,
)
from caerp.views.admin.accounting.income_statement_measures import move_view
from caerp.views.admin.tools import BaseAdminIndexView, BaseConfigView

logger = logging.getLogger(__name__)

BASE_URL = os.path.join(ACCOUNTING_URL, "treasury_measures")
UI_URL = os.path.join(BASE_URL, "ui")

CATEGORY_URL = BASE_URL + "/categories"
CATEGORY_TYPE_ITEM_URL = CATEGORY_URL + "/{id}"

TYPE_INDEX_URL = BASE_URL + "/types"
TYPE_CATEGORY_URL = TYPE_INDEX_URL + "/{category_id}"
TYPE_ITEM_URL = TYPE_CATEGORY_URL + "/{id}"


class TreasuryMeasureIndexView(BaseAdminIndexView):
    title = "État de trésorerie"
    description = (
        "Paramétrer l'état de gestion « État de trésorerie »"
        " visible par les entrepreneurs."
    )
    route_name = BASE_URL
    permission = PERMISSIONS["global.config_accounting_measure"]


class TreasuryMeasureUiView(BaseConfigView):
    title = "Interface entrepreneur"
    description = (
        "Configuration des priorités d’affichage dans l’interface de l’entrepreneur"
    )
    route_name = UI_URL

    redirect_route_name = BASE_URL
    validation_msg = "Les informations ont bien été enregistrées"
    keys = ("treasury_measure_ui",)
    schema = get_config_schema(keys)
    info_message = """Configurer l'indicateur de trésorerie qui sera mis en \
        avant dans l'interface de l'entrepreneur"""
    permission = PERMISSIONS["global.config_accounting_measure"]


class CategoryListView(IncomeStatementCategoryListView):
    columns = [
        "Libellé de la catégorie",
    ]
    title = "Catégories d'indicateurs d'état de trésorerie"
    route_name = CATEGORY_URL
    item_route_name = CATEGORY_TYPE_ITEM_URL
    factory = TreasuryMeasureTypeCategory
    item_name = "états de trésorerie"
    permission = PERMISSIONS["global.config_accounting_measure"]


class CategoryAddView(IncomeStatementCategoryAddView):
    route_name = CATEGORY_URL

    factory = TreasuryMeasureTypeCategory
    schema = get_admin_accounting_type_category_schema(
        TreasuryMeasureTypeCategory, is_edit=False
    )
    permission = PERMISSIONS["global.config_accounting_measure"]


class CategoryEditView(IncomeStatementCategoryEditView):
    factory = TreasuryMeasureTypeCategory
    route_name = CATEGORY_TYPE_ITEM_URL
    schema = get_admin_accounting_type_category_schema(
        TreasuryMeasureTypeCategory, is_edit=True
    )
    permission = PERMISSIONS["global.config_accounting_measure"]

    @property
    def title(self):
        return "Modifier la catégorie '{0}'".format(self.context.label)


class CategoryDisableView(IncomeStatementCategoryDisableView):
    """
    View for measure disable/enable
    """

    route_name = CATEGORY_TYPE_ITEM_URL
    factory = TreasuryMeasureTypeCategory
    permission = PERMISSIONS["global.config_accounting_measure"]


class CategoryDeleteView(IncomeStatementCategoryDeleteView):
    """
    Category deletion view
    """

    route_name = CATEGORY_TYPE_ITEM_URL
    factory = TreasuryMeasureTypeCategory
    permission = PERMISSIONS["global.config_accounting_measure"]


class TypeListIndexView(IncomeStatementTypeListIndexView):
    title = "Indicateurs d'état de trésorerie"
    route_name = TYPE_INDEX_URL
    category_route_name = TYPE_CATEGORY_URL
    category_class = TreasuryMeasureTypeCategory
    help_message = """Les indicateurs de états de trésorerie permettent de
    regrouper les écritures comptables derrière un même libellé afin de les
    regrouper au sein des états de trésorerie de chaque enseigne.<br />
    Les indicateurs sont divisés en plusieurs catégories.<br />
    Depuis cette interface, vous pouvez configurer, par
    catégorie, l'ensemble des indicateurs qui composeront les états de
    trésorerie de vos entrepreneurs."""
    permission = PERMISSIONS["global.config_accounting_measure"]


class MeasureTypeListView(IncomeStatementMeasureTypeListView):
    factory = TreasuryMeasureType
    category_class = TreasuryMeasureTypeCategory
    route_name = TYPE_CATEGORY_URL
    item_route_name = TYPE_ITEM_URL
    item_label = "d'état de trésorerie"
    permission = PERMISSIONS["global.config_accounting_measure"]

    def more_template_vars(self, result):
        """
        Hook allowing to add datas to the templating context
        """
        result[
            "help_msg"
        ] = """Les définitions ci-dessous indiquent quelles
        écritures sont utilisées pour le calcul des indicateurs de la section
        %s des états de trésorerie des entrepreneurs.<br />
        Les indicateurs seront présentés dans l'ordre.<br />
        Certains indicateurs sont des totaux, ils seront alors mis en évidence
        dans l'interface""" % (
            self.context.label,
        )
        return result


class MeasureTypeAddView(IncomeStatementMeasureTypeAddView):
    title = "Ajouter"
    route_name = TYPE_CATEGORY_URL + "/add"
    _schema = None
    factory = TreasuryMeasureType
    permission = PERMISSIONS["global.config_accounting_measure"]


class MeasureTypeEditView(IncomeStatementMeasureTypeEditView):
    route_name = TYPE_ITEM_URL
    _schema = None
    factory = TreasuryMeasureType
    permission = PERMISSIONS["global.config_accounting_measure"]


class MeasureDisableView(IncomeStatementMeasureDisableView):
    route_name = TYPE_ITEM_URL
    factory = TreasuryMeasureType
    permission = PERMISSIONS["global.config_accounting_measure"]


class MeasureDeleteView(IncomeStatementMeasureDeleteView):
    """
    View for measure disable/enable
    """

    route_name = TYPE_ITEM_URL
    factory = TreasuryMeasureType
    permission = PERMISSIONS["global.config_accounting_measure"]


def add_routes(config):
    """
    Add routes related to this module
    """
    config.add_route(BASE_URL, BASE_URL)
    config.add_route(CATEGORY_URL, CATEGORY_URL)
    config.add_route(
        CATEGORY_TYPE_ITEM_URL,
        CATEGORY_TYPE_ITEM_URL,
        traverse="/treasury_measure_type_categories/{id}",
    )

    config.add_route(TYPE_INDEX_URL, TYPE_INDEX_URL)
    config.add_route(
        TYPE_CATEGORY_URL,
        TYPE_CATEGORY_URL,
        traverse="/treasury_measure_type_categories/{category_id}",
    )
    config.add_route(
        TYPE_CATEGORY_URL + "/add",
        TYPE_CATEGORY_URL + "/add",
        traverse="/treasury_measure_type_categories/{category_id}",
    )
    config.add_route(
        TYPE_ITEM_URL,
        TYPE_ITEM_URL,
        traverse="/treasury_measure_types/{id}",
    )
    config.add_route(UI_URL, UI_URL)


def add_views(config):
    """
    Add views defined in this module
    """
    config.add_admin_view(
        TreasuryMeasureIndexView,
        parent=AccountingIndexView,
    )
    config.add_admin_view(
        TreasuryMeasureUiView,
        parent=TreasuryMeasureIndexView,
    )
    config.add_admin_view(
        CategoryListView,
        parent=TreasuryMeasureIndexView,
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
    )
    config.add_admin_view(
        CategoryDeleteView,
        parent=CategoryListView,
        request_param="action=delete",
    )
    config.add_admin_view(
        move_view,
        route_name=CATEGORY_TYPE_ITEM_URL,
        request_param="action=move",
    )
    config.add_admin_view(
        TypeListIndexView,
        parent=TreasuryMeasureIndexView,
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
    )
    config.add_admin_view(
        MeasureDeleteView,
        parent=MeasureTypeListView,
        request_param="action=delete",
    )
    config.add_admin_view(
        move_view,
        route_name=TYPE_ITEM_URL,
        request_param="action=move",
    )


def includeme(config):
    add_routes(config)
    add_views(config)
