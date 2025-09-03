import functools
import colander
import deform

from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.task.estimation import (
    Estimation,
    PaymentLine,
    ESTIMATION_STATES,
    PAYMENTDISPLAYCHOICES,
    get_estimation_years,
)
from caerp.utils.strings import format_amount
from caerp.models.task.invoice import Invoice
from caerp.utils.renderer import get_json_dict_repr

from caerp import forms
from caerp.forms.company import company_filter_node_factory
from caerp.forms.third_party.customer import customer_filter_node_factory
from caerp.forms.custom_types import AmountType
from caerp.forms.tasks.lists import (
    PeriodSchema,
    AmountRangeSchema,
)
from caerp.forms.tasks.task import get_edit_task_schema, business_type_filter_node
from caerp.forms.widgets import CleanMappingWidget

SIGNED_STATUS_OPTIONS = (
    ("all", "Tous"),
    ("waiting", "Devis en cours"),
    ("signed", "Devis signés"),
    ("noinv", "Devis signés non facturés"),
    ("geninv", "Devis concrétisés (avec facture)"),
    ("aborted", "Devis annulés"),
)

STATUS_OPTIONS = (
    ("all", "Tous"),
    ("draft", "Brouillon"),
    ("wait", "En attente de validation"),
    ("invalid", "Invalide"),
    ("valid", "Validé"),
)


TYPE_OPTIONS = (
    ("both", "Tous"),
    ("estimation", "Seulement les devis externes"),
    ("internalestimation", "Seulement les devis internes"),
)


def get_list_schema(request, is_global=False, excludes=()):
    """
    Return the estimation list schema

    :param bool is_global: Should we include global search fields (CAE wide)
    :param tuple excludes: List of field to exclude
    :returns: The list schema
    :rtype: colander.SchemaNode
    """
    schema = forms.lists.BaseListsSchema().clone()

    # del schema["search"]

    schema.insert(0, business_type_filter_node())

    if "customer" not in excludes:
        schema.insert(
            0,
            customer_filter_node_factory(
                is_global=is_global,
                name="customer_id",
                title="Client",
                with_estimation=True,
            ),
        )

    if is_global:
        schema.insert(
            0, company_filter_node_factory(name="company_id", title="Enseigne")
        )
        forms.add_antenne_option_field(request, schema)

    schema.insert(
        0,
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
        0,
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

    if "status" not in excludes:
        schema.insert(0, forms.status_filter_node(STATUS_OPTIONS))

    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="doctype",
            title="Types de devis",
            widget=deform.widget.SelectWidget(values=TYPE_OPTIONS),
            validator=colander.OneOf([s[0] for s in TYPE_OPTIONS]),
            missing="both",
            default="both",
        ),
    )

    if "signed_status" not in excludes:
        schema.insert(
            0,
            forms.status_filter_node(
                SIGNED_STATUS_OPTIONS,
                name="signed_status",
                title="Statut client",
            ),
        )

    if "year" not in excludes:
        node = forms.year_filter_node(
            name="year",
            title="Année",
            query_func=get_estimation_years,
        )
        schema.insert(0, node)

    if "auto_validated" not in excludes:
        schema.add_before(
            "items_per_page",
            colander.SchemaNode(
                colander.Boolean(),
                name="auto_validated",
                label="Documents auto-validés",
                arialabel="Activer pour afficher seulement les documents auto-validés",
                missing=colander.drop,
            ),
        )

    schema["search"].title = "Numéro de devis"

    return schema


@colander.deferred
def deferred_invoice_widget(node, kw):
    """
    Return a select for estimation selection
    """
    estimation = kw["request"].context
    query = Invoice.query()
    query = query.filter(Invoice.project_id == estimation.project_id)
    query = query.filter(Invoice.customer_id == estimation.customer_id)
    query = query.filter(Invoice.business_type_id == estimation.business_type_id)
    choices = []
    for invoice in query:
        if invoice.mode == "ttc":
            amount_label = format_amount(
                invoice.total_ttc(), precision=5, grouping=False
            )
            amount_mode = "TTC"
        else:
            amount_label = format_amount(
                invoice.total_ht(), precision=5, grouping=False
            )
            amount_mode = "HT"
        label = f"{invoice.name} - {amount_label} € {amount_mode}"

        if invoice.official_number is not None:
            label = f"N° {invoice.official_number} - {label}"

        if invoice.estimation_id is not None:
            label += " (déjà rattachée à un devis)"
        choices.append((invoice.id, label))
    return deform.widget.CheckboxChoiceWidget(values=choices)


class InvoiceAttachSchema(colander.Schema):
    invoice_ids = colander.SchemaNode(
        colander.Set(),
        widget=deferred_invoice_widget,
        missing=colander.drop,
        title="Factures disponibles",
    )


def _customize_paymentline_schema(schema):
    """
    Customize PaymentLine related form schema

    :param obj schema: The schema generated by colanderalchemy
    :rtype: `colander.SQLAlchemySchemaNode`
    """
    customize = functools.partial(forms.customize_field, schema)
    customize("id", widget=deform.widget.HiddenWidget(), missing=colander.drop)
    customize("task_id", missing=colander.required)
    customize("description", validator=forms.textarea_node_validator)
    customize(
        "amount",
        typ=AmountType(5),
        missing=colander.required,
    )
    return schema


def _customize_estimation_schema(schema):
    """
    Add form schema customization to the given Estimation edition schema

    :param obj schema: The schema to edit
    """
    customize = functools.partial(forms.customize_field, schema)
    customize(
        "signed_status",
        widget=deform.widget.SelectWidget(values=ESTIMATION_STATES),
        validator=colander.OneOf([i[0] for i in ESTIMATION_STATES]),
    )
    customize(
        "deposit",
        validator=colander.Range(
            0,
            100,
            min_err="Ce nombre n'est pas compris en 0 et 100",
            max_err="Ce nombre n'est pas compris en 0 et 100",
        ),
    )
    customize(
        "paymentDisplay",
        widget=deform.widget.SelectWidget(values=PAYMENTDISPLAYCHOICES),
        validator=colander.OneOf([i[0] for i in PAYMENTDISPLAYCHOICES]),
    )
    customize(
        "payment_lines",
        validator=colander.Length(min=1, min_err="Au moins un paiement est requis"),
        missing=colander.required,
    )

    if "payment_lines" in schema:
        child_schema = schema["payment_lines"].children[0]
        _customize_paymentline_schema(child_schema)
    return schema


def get_add_edit_paymentline_schema(includes=None, excludes=None):
    """
    Return add edit schema for PaymentLine edition

    :param tuple includes: Field that should be included in the schema
    :param tuple excludes: Field that should be excluded in the schema
    (incompatible with includes option)

    :rtype: `colanderalchemy.SQLAlchemySchemaNode`
    """
    if includes is not None:
        excludes = None

    schema = SQLAlchemySchemaNode(PaymentLine, includes=includes, excludes=excludes)
    schema = _customize_paymentline_schema(schema)
    return schema


def get_edit_estimation_schema(
    isadmin=False, includes=None, excludes=None, **kw
) -> SQLAlchemySchemaNode:
    """
    Return edit schema for Estimation edition

    :param bool isadmin: Are we asking for an admin schema ?
    :param tuple includes: Field that should be included in the schema
    :param tuple excludes: Field that should be excluded in the schema
    (incompatible with includes option)
    """
    schema = get_edit_task_schema(
        Estimation, isadmin=isadmin, includes=includes, excludes=excludes, **kw
    )
    schema = _customize_estimation_schema(schema)
    return schema


def validate_estimation(estimation_object: "Estimation", request):
    """
    Globally validate an estimation_object

    :param obj estimation_object: An instance of Estimation
    :param obj request: The pyramid request
    :raises: colander.Invalid

    try:
        validate_estimation(est, self.request)
    except colander.Invalid as err:
        error_messages = err.messages
    """
    schema = get_edit_estimation_schema()
    schema = schema.bind(request=request)
    appstruct = get_json_dict_repr(estimation_object, request=request)
    appstruct["line_groups"] = get_json_dict_repr(
        estimation_object.line_groups, request=request
    )
    appstruct["discounts"] = get_json_dict_repr(
        estimation_object.discounts, request=request
    )
    appstruct["payment_lines"] = get_json_dict_repr(
        estimation_object.payment_lines, request=request
    )
    cstruct = schema.deserialize(appstruct)
    return cstruct
