"""
Tva administration tools
"""
import os
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import select

from caerp.consts.permissions import PERMISSIONS
from caerp.models.tva import Tva
from caerp.views import BaseView
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.admin.sale.tva import get_tva_edit_schema
from caerp.views import render_api
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminEditView,
    BaseAdminAddView,
    BaseAdminDisableView,
)
from . import ACCOUNTING_INDEX_URL, SaleAccountingIndex

TVA_URL = os.path.join(ACCOUNTING_INDEX_URL, "tva")
TVA_ITEM_URL = os.path.join(TVA_URL, "{id}")

VALIDATION_MSG = "Les taux de Tva ont bien été configurés"
HELP_MSG = """Configurez les taux de Tva disponibles utilisés dans
 MoOGLi, ainsi que les produits associés.<br />
Une Tva est composée :<ul><li>D'un libellé (ex : TVA 20%)</li>
<li>D'un montant (ex : 20)</li>
<li>D'un ensemble d'informations comptables</li>
<li>D'un ensemble de produits associés</li>
<li> D'une mention : si elle est renseignée, celle-ci viendra se placer
 en lieu et place du libellé (ex : Tva non applicable en vertu ...)
</ul><br />
<strong>Note : les montants doivent tous être distincts, si
vous utilisez
 plusieurs Tva à 0%, utilisez des montants négatifs pour les
 différencier.</strong>
"""


class TvaListView(AdminCrudListView):
    """
    List of tva entries
    """

    title = "Comptabilité : Produits et TVA collectés"
    description = "Configurer : Taux de TVA, codes produits et codes \
analytiques associés"
    route_name = TVA_URL
    columns = ["Libellé", "Valeur", "Compte CG", "Compte à payer", "Taux par défaut"]

    item_route_name = TVA_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]

    def stream_columns(self, tva):
        """
        Stream the table datas for the given item
        :param obj tva: The Tva object to stream
        :returns: List of labels
        """
        if tva.default:
            default = "<span class='icon'>\
                <svg><use href='{}#check'></use></svg>\
                </span><br />TVA par défaut".format(
                self.request.static_url("caerp:static/icons/icones.svg")
            )
        else:
            default = ""
        return (
            tva.name,
            render_api.format_amount(tva.value),
            tva.compte_cg or "Aucun",
            tva.compte_a_payer or "Aucun",
            default,
        )

    def stream_actions(self, tva):
        """
        Stream the actions available for the given tva object
        :param obj tva: Tva instance
        :returns: List of 5-uples (url, label, title, icon, disable)
        """
        yield Link(self._get_item_url(tva), "Voir/Modifier", icon="pen", css="icon")
        if tva.active:
            yield POSTButton(
                self._get_item_url(tva, action="disable"),
                label="Désactiver",
                title="La TVA n’apparaitra plus dans l’interface",
                icon="lock",
                css="icon",
            )
            if not tva.default:
                yield POSTButton(
                    self._get_item_url(tva, action="set_default"),
                    label="Définir comme Taux de TVA par défaut",
                    title="La TVA sera sélectionnée par défaut dans les " "formulaires",
                    icon="check",
                    css="icon",
                )
        else:
            yield POSTButton(
                self._get_item_url(tva, action="disable"),
                "Activer",
                title="La TVA apparaitra dans l’interface",
                icon="lock-open",
                css="icon",
            )

    def load_items(self):
        return (
            self.request.dbsession.execute(
                select(Tva).order_by(Tva.active.desc(), Tva.value)
            )
            .scalars()
            .all()
        )

    def more_template_vars(self, result):
        result["nodata_msg"] = "Aucun taux de TVA n'a été configuré"
        if result["items"]:
            if Tva.get_default() is None:
                result["warn_msg"] = (
                    "Aucun taux de TVA par défaut n’a été configuré. "
                    "Des problèmes peuvent être rencontrés lors de "
                    "l’édition de devis/factures."
                )
        return result


class TvaAddView(BaseAdminAddView):
    """
    Add view
    """

    route_name = TVA_URL
    schema = get_tva_edit_schema()
    factory = Tva
    title = "Ajouter"
    help_msg = HELP_MSG
    validation_msg = VALIDATION_MSG
    permission = PERMISSIONS["global.config_accounting"]


class TvaEditView(BaseAdminEditView):
    """
    Edit view
    """

    route_name = TVA_ITEM_URL

    schema = get_tva_edit_schema()
    factory = Tva
    title = "Modifier"
    help_msg = HELP_MSG
    validation_msg = VALIDATION_MSG
    permission = PERMISSIONS["global.config_accounting"]

    def submit_success(self, appstruct):
        old_products = []
        for product in self.context.products:
            if product.id not in [p.get("id") for p in appstruct["products"]]:
                product.active = False
                old_products.append(product)

        for order, product in enumerate(appstruct["products"]):
            product["order"] = order

        model = self.schema.objectify(appstruct, self.context)
        model.products.extend(old_products)
        self.dbsession.merge(model)
        self.dbsession.flush()

        if self.msg:
            self.request.session.flash(self.msg)

        return self.redirect(appstruct)


class TvaSetDefaultView(BaseView):
    """
    Set the given tva as default
    """

    route_name = TVA_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]

    def __call__(self):
        for tva in Tva.query(include_inactive=True):
            tva.default = False
            self.request.dbsession.merge(tva)
        self.context.default = True
        self.request.dbsession.merge(tva)
        return HTTPFound(TVA_URL)


class TvaDisableView(BaseAdminDisableView):
    route_name = TVA_ITEM_URL
    disable_msg = "Le taux de TVA a bien été désactivé"
    enable_msg = "Le taux de TVA a bien été activé"
    permission = PERMISSIONS["global.config_accounting"]


def includeme(config):
    """
    Add routes and views
    """
    config.add_route(TVA_URL, TVA_URL)
    config.add_route(TVA_ITEM_URL, TVA_ITEM_URL, traverse="/tvas/{id}")

    config.add_admin_view(
        TvaListView,
        parent=SaleAccountingIndex,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        TvaDisableView,
        parent=TvaListView,
        request_param="action=disable",
        require_csrf=True,
        request_method="POST",
    )
    config.add_admin_view(
        TvaAddView,
        parent=TvaListView,
        request_param="action=add",
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        TvaEditView,
        parent=TvaListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        TvaSetDefaultView,
        request_param="action=set_default",
        require_csrf=True,
        request_method="POST",
    )
