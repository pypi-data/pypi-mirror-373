import colander
import deform
import functools

from colanderalchemy import SQLAlchemySchemaNode

from caerp import forms
from caerp.forms.expense import (
    get_deferred_select_expense_type,
    deferred_type_id_validator,
)
from caerp.forms.tasks.lists import (
    PeriodSchema,
    AmountRangeSchema,
)
from caerp.forms.third_party.supplier import (
    supplier_choice_node_factory,
    get_deferred_supplier_select_validator,
    get_deferred_supplier_choice_validator,
)
from caerp.forms.supply import get_list_schema
from caerp.forms.widgets import CleanMappingWidget
from caerp.models.supply import SupplierOrder
from caerp.utils.renderer import get_json_dict_repr
from caerp.services.supplier_order import get_supplier_orders_years


INVOICE_STATUS_OPTIONS = [
    ("all", ""),
    ("absent", "pas de facture"),
    ("present", "facture (tous statuts)"),
    ("draft", "facture en brouillon"),
    ("valid", "facture validée"),
    ("resulted", "facture soldée"),
]

TYPE_OPTIONS = (
    ("both", "Tous"),
    ("supplier_order", "Exclure les commandes internes"),
    ("internalsupplier_order", "Seulement les commandes internes"),
)


def get_company_from_request(request):
    from caerp.models.company import Company
    from caerp.models.supply import SupplierInvoice

    if isinstance(request.context, Company):
        company = request.context
    elif isinstance(request.context, SupplierInvoice):
        company = request.context.company
    else:
        raise ValueError("No company bound to this request")
    return company


def _customize_field(schema):
    customize = functools.partial(forms.customize_field, schema)
    if "supplier_id" in schema:
        customize(
            "supplier_id",
            validator=get_deferred_supplier_select_validator(),
            missing=colander.required,
        )

    """
    TODO : Réactiver le contrôle des types de dépenses quand ils seront 
    modifiables pour les commandes internes (ref #4207)
    """
    # if "lines" in schema:
    #     child_schema = schema["lines"].children[0]
    #     forms.customize_field(child_schema, "type_id", missing=colander.required)

    if "date" in schema:
        schema["date"].missing = colander.required

    return schema


def get_supplier_order_edit_schema(internal=False):
    """
    Build a supplier order edition schema

    :param bool internal: Is the edited document internal
    """
    excludes = ()
    if internal:
        excludes += ("supplier_id", "cae_percentage")
    schema = SQLAlchemySchemaNode(SupplierOrder, excludes=excludes)
    _customize_field(schema)
    return schema


def validate_supplier_order(supplier_order_object: SupplierOrder, request):
    """
    Globally validate an SupplierInvoice

    :param obj invoice_object: An instance of SupplierInvoice
    :param obj request: The pyramid request
    :raises: colander.Invalid

    try:
        validate_supplier_order(est, self.request)
    except colander.Invalid as err:
        error_messages = err.messages
    """
    schema = get_supplier_order_edit_schema(internal=supplier_order_object.internal)
    schema = schema.bind(request=request)

    appstruct = get_json_dict_repr(supplier_order_object, request)
    appstruct["lines"] = get_json_dict_repr(
        supplier_order_object.lines, request=request
    )
    cstruct = schema.deserialize(appstruct)

    return cstruct


def get_supplier_orders_list_schema(request, is_global=False):
    schema = get_list_schema(
        request,
        years_func=get_supplier_orders_years,
        is_global=is_global,
    )
    schema.insert(
        1,
        PeriodSchema(
            name="period",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg="La date de début doit précéder la date de fin",
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )
    schema.insert(
        3,
        AmountRangeSchema(
            name="ttc",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg=("Le montant minimal doit être inférieur ou égal au maximum"),
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )
    schema.insert(
        4,
        colander.SchemaNode(
            colander.String(),
            name="invoice_status",
            title="Facture fournisseur",
            widget=deform.widget.SelectWidget(values=INVOICE_STATUS_OPTIONS),
            validator=colander.OneOf([s[0] for s in INVOICE_STATUS_OPTIONS]),
            missing="all",
            default="all",
        ),
    )
    schema.insert(
        4,
        colander.SchemaNode(
            colander.String(),
            name="doctype",
            title="Types de commandes",
            widget=deform.widget.SelectWidget(values=TYPE_OPTIONS),
            validator=colander.OneOf([s[0] for s in TYPE_OPTIONS]),
            missing="both",
            default="both",
        ),
    )
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.Integer(),
            name="expense_type_id",
            title="Types de dépenses",
            widget=get_deferred_select_expense_type(default=True),
            validator=deferred_type_id_validator,
            missing=-1,
            default=-1,
        ),
    )
    return schema


def get_supplier_order_add_schema():
    schema = SQLAlchemySchemaNode(
        SupplierOrder,
        includes=["supplier_id"],
    )
    schema["supplier_id"] = supplier_choice_node_factory(
        description="Si le fournisseur manque, l'ajouter d'abord "
        "dans Achats → Fournisseurs."
    )
    schema.validator = get_deferred_supplier_choice_validator()
    return schema


def get_company_supplier_orders_from_request(request):
    company = get_company_from_request(request)
    query = SupplierOrder.query().filter_by(company_id=company.id)
    exclude = "internalsupplier_order"
    query = query.filter(SupplierOrder.type_ != exclude)
    return query


def get_deferred_supplier_order_choices(
    widget_options,
    query_func=get_company_supplier_orders_from_request,
):
    """
    Builds a Select2Widget for selecting SupplierOrder

    :param query_func: a function returning a SupplierOrder query
    :returns: a deferred Select2Widget
    """

    @colander.deferred
    def _get_deferred_supplier_order_choice(node, kw):
        request = kw["request"]
        values = [(i.id, i.name) for i in query_func(request)]

        return deform.widget.Select2Widget(values=values, **widget_options)

    return _get_deferred_supplier_order_choice


def get_deferred_supplier_order_select_validator(
    query_func=get_company_supplier_orders_from_request,
    multiple=False,
    required=True,
):
    """
    :returns: A colander deferred validator
    """

    @colander.deferred
    def _deferred_supplier_order_select_validator(node, kw):
        def orders_allin(value):
            request = kw["request"]
            if multiple:
                selected_ids = value
            else:
                selected_ids = [value]
            allowed_ids = [i.id for i in query_func(request)]

            if required and (len(selected_ids) == 0):
                return "Veuillez choisir au moins une commande fournisseur"
            for selected_id in selected_ids:
                if selected_id in ("0", 0):
                    return "Veuillez choisir une commande fournisseur"
                elif int(selected_id) not in allowed_ids:
                    return "Choix de commande invalide"
            return True

        return colander.Function(orders_allin)

    return _deferred_supplier_order_select_validator


def supplier_order_node(
    multiple=False,
    query_func=get_company_supplier_orders_from_request,
    extra_validator=None,
    required=True,
    **kw,
):
    """
    Builds a node for selecting one or several SupplierOrder

    Takes care of listing options and validating them using the same query.
    """
    widget_options = kw.pop("widget_options", {})
    validator = get_deferred_supplier_order_select_validator(
        query_func=query_func,
        multiple=multiple,
        required=required,
    )
    if extra_validator:
        validators = [validator, extra_validator]
    else:
        validators = [validator]

    return colander.SchemaNode(
        colander.Set() if multiple else colander.Integer(),
        widget=get_deferred_supplier_order_choices(
            widget_options,
            query_func=query_func,
        ),
        validator=forms.DeferredAll(*validators),
        **kw,
    )


supplier_order_choice_node = forms.mk_choice_node_factory(
    supplier_order_node,
    resource_name="une commande fournisseur",
    resource_name_plural="de zéro a plusieurs commandes fournisseur",
    required=False,
)
