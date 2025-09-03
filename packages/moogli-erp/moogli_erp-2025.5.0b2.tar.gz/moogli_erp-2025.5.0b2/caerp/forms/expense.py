"""
    Form models related to the expenses configuration
    * expense status configuration
    * period selection
    * expenseline configuration
"""
import functools
import logging

import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode
import deform_extensions
from sqlalchemy import select

from caerp import forms
from caerp.forms.payments import (
    deferred_bank_account_validator,
    deferred_bank_account_widget,
    deferred_payment_mode_validator,
    deferred_payment_mode_widget,
)
from caerp.forms.user import contractor_filter_node_factory
from caerp.models.expense.payment import ExpensePayment
from caerp.models.expense.sheet import (
    BaseExpenseLine,
    ExpenseKmLine,
    ExpenseLine,
    ExpenseSheet,
    get_expense_years,
    get_new_expense_years,
)
from caerp.models.expense.types import ExpenseKmType, ExpenseType
from caerp.models.files import File
from caerp.models.payments import BankAccount
from caerp.utils import strings
from caerp.utils.strings import remove_newlines

from .custom_types import AmountType
from .third_party.supplier import get_deferred_supplier_select_validator

STATUS_OPTIONS = (
    ("all", "Tous"),
    ("wait", "En attente de validation"),
    ("valid", "Validées"),
    ("invalid", "Invalidées"),
    ("paid", "Partiellement payées"),
    ("resulted", "Payées"),
    ("notpaid", "Non payées"),
)

DOC_STATUS_OPTIONS = (
    ("all", "Tous"),
    ("notjustified", "Justfificatifs en attente"),
    ("justified", "Justficatifs reçus"),
)


logger = logging.getLogger(__name__)


def get_expense_types(dbsession):
    return dbsession.execute(
        select(ExpenseType.id, ExpenseType.label)
        .filter(ExpenseType.type.in_(["expense", "expensetel"]))
        .filter(ExpenseType.active == True)
        .order_by(ExpenseType.label)
    ).all()


def get_deferred_select_expense_type(default=False):
    @colander.deferred
    def deferred_select_expense_type(node, kw):
        dbsession = kw["request"].dbsession
        values = [(a.id, a.label) for a in get_expense_types(dbsession)]
        if default:
            values.insert(0, (-1, "Tous les types de dépense"))
        return deform.widget.SelectWidget(values=values)

    return deferred_select_expense_type


@colander.deferred
def deferred_type_id_validator(node, kw):
    """
    deferred Expensetype id validator
    """
    from caerp.models.expense.types import ExpenseType

    ids = [t[0] for t in kw["request"].dbsession.query(ExpenseType.id)]
    ids.append(-1)
    return colander.OneOf(ids)


def get_amount_topay(kw):
    """
    Retrieve the amount to be paid regarding the context
    """
    topay = 0
    context = kw["request"].context
    if isinstance(context, ExpenseSheet):
        topay = context.topay()
    elif isinstance(context, ExpensePayment):
        topay = context.expense.topay()
        topay += context.get_amount()
    return topay


@colander.deferred
def deferred_amount_default(node, kw):
    """
    default value for the payment amount
    """
    topay = get_amount_topay(kw)

    # Avoid pre-filling the <input> with "0.0", as
    # to have less clicks to do.
    if topay == 0:
        topay = colander.null
    return topay


@colander.deferred
def deferred_expense_total_validator(node, kw):
    """
    Validate the amount to keep the sum under the total
    """
    topay = get_amount_topay(kw)
    amount_msg = (
        "Le montant ne doit pas dépasser %s (total TTC - somme \
    des paiements)"
        % (topay / 100.0)
    )
    if topay < 0:
        min_val = topay
        max_val = 0
        min_msg = amount_msg
        max_msg = "Le montant doit être négatif"
    else:
        min_val = 0
        max_val = topay
        min_msg = "Le montant doit être positif"
        max_msg = amount_msg
    return colander.Range(
        min=min_val,
        max=max_val,
        min_err=min_msg,
        max_err=max_msg,
    )


class ExpensePaymentSchema(colander.MappingSchema):
    """
    Schéma de saisie des paiements des notes de dépenses
    """

    come_from = forms.come_from_node()
    date = forms.today_node()
    amount = colander.SchemaNode(
        AmountType(),
        title="Montant du paiement",
        validator=deferred_expense_total_validator,
        default=deferred_amount_default,
    )
    mode = colander.SchemaNode(
        colander.String(),
        title="Mode de paiement",
        widget=deferred_payment_mode_widget,
        validator=deferred_payment_mode_validator,
    )
    bank_id = colander.SchemaNode(
        colander.Integer(),
        title="Banque",
        missing=colander.drop,
        widget=deferred_bank_account_widget,
        validator=deferred_bank_account_validator,
        default=forms.get_deferred_default(BankAccount),
    )
    waiver = colander.SchemaNode(
        colander.Boolean(),
        title="Abandon de créance",
        description="""Indique que ce paiement correspond à un abandon de
créance à la hauteur du montant indiqué, le mode de paiement et la banque sont
alors ignorés""",
        missing=False,
        default=False,
    )
    resulted = colander.SchemaNode(
        colander.Boolean(),
        title="Soldé",
        description="""Indique que le document est soldé (
ne recevra plus de paiement), si le montant indiqué correspond au
montant de la note de dépenses, celle-ci est soldée automatiquement""",
        missing=False,
        default=False,
    )


def customize_schema(schema):
    """
    Add custom field configuration to the schema

    :param obj schema: colander Schema
    """
    customize = functools.partial(forms.customize_field, schema)
    customize(
        "month",
        widget=forms.get_month_select_widget({}),
        validator=colander.OneOf(list(range(1, 13))),
        default=forms.default_month,
        missing=colander.required,
    )
    customize(
        "year",
        widget=forms.get_year_select_deferred(query_func=get_new_expense_years),
        validator=colander.Range(min=0, min_err="Veuillez saisir une année valide"),
        default=forms.deferred_default_year,
        missing=colander.required,
    )
    customize(
        "title",
        missing=colander.drop,
        description="""Facultatif - Permet de nommer cette note de dépense et de mieux 
la réperer dans les listes""",
    )


def get_add_edit_sheet_schema():
    """
    Return a schema for expense add/edit

    Only month and year are available for edition

    :rtype: colanderalchemy.SQLAlchemySchemaNode
    """
    from caerp.models.expense.sheet import ExpenseSheet

    schema = SQLAlchemySchemaNode(
        ExpenseSheet,
        includes=("month", "year", "title"),
    )
    customize_schema(schema)
    return schema


@colander.deferred
def deferred_expense_km_type_id_validator(node, kw):
    """
    Build a custom type_id validator for ExpenseKmLine

    Only types associated to the current sheet's year are allowed

    Ref https://framagit.org/caerp/caerp/issues/1088
    """
    context = kw["request"].context

    if isinstance(context, ExpenseSheet):
        year = context.year
    else:
        year = context.sheet.year

    # NB : La valeur du filtre dépend du contexte
    deferred_validator = forms.get_deferred_select_validator(
        ExpenseKmType, filters=[("year", year)]
    )
    return deferred_validator(node, kw)


def get_add_edit_line_schema(factory, expense_sheet=None):
    """
    Build a schema for expense line

    :param class model: The model for which we want to generate the schema
    :rerturns: A SQLAlchemySchemaNode schema
    """
    logger.debug("Get add edit line schema")
    excludes = ("sheet_id", "justified")
    schema = SQLAlchemySchemaNode(factory, excludes=excludes)
    if factory == ExpenseLine:
        typ_filter = ExpenseType.type.in_(("expense", "expensetel"))
        forms.customize_field(
            schema,
            "type_id",
            validator=forms.get_deferred_select_validator(
                ExpenseType, filters=[typ_filter]
            ),
            missing=colander.required,
        )
        forms.customize_field(
            schema,
            "files",
            children=forms.get_sequence_child_item(
                File, filters=[["parent_id", expense_sheet.id]]
            ),
        )
        forms.customize_field(
            schema,
            "supplier_id",
            validator=get_deferred_supplier_select_validator(),
        )

    elif factory == ExpenseKmLine:
        forms.customize_field(
            schema,
            "type_id",
            validator=deferred_expense_km_type_id_validator,
            missing=colander.required,
        )

    forms.customize_field(
        schema,
        "ht",
        typ=AmountType(2),
        missing=colander.required,
    )
    forms.customize_field(
        schema,
        "tva",
        typ=AmountType(2),
        missing=colander.required,
    )
    forms.customize_field(
        schema,
        "manual_ttc",
        typ=AmountType(2),
        missing=colander.required,
    )
    forms.customize_field(
        schema,
        "km",
        typ=AmountType(2),
        missing=colander.required,
    )
    forms.customize_field(
        schema,
        "customer_id",
        missing=None,
    )
    forms.customize_field(
        schema,
        "project_id",
        missing=None,
    )
    forms.customize_field(
        schema,
        "business_id",
        missing=None,
    )
    forms.customize_field(
        schema,
        "description",
        preparer=remove_newlines,
    )
    return schema


def _get_linkable_expense_lines(node, kw):
    business = kw["request"].context
    assert business.__name__ == "business"
    query = BaseExpenseLine.linkable(business)
    # Do not offer "frais généraux" lines
    return query.filter(BaseExpenseLine.category == "2")


def _get_deferred_expense_line_choices(widget_options):
    default_option = widget_options.pop("default_option", None)

    @colander.deferred
    def deferred_expense_line_choices(node, kw):
        query = _get_linkable_expense_lines(node, kw)
        # most recent first
        query = query.order_by(
            BaseExpenseLine.date.desc(),
            BaseExpenseLine.id.desc(),
        )
        values = [(v.id, v.long_label()) for v in query]
        if default_option:
            # Cleaner fix would be to replace `default_option` 2-uple arg with
            # a `placeholder` str arg, as in JS code.
            # Use of placeholder arg is mandatory with Select2 ; otherwise, the
            # clear button crashes. https://github.com/select2/select2/issues/5725
            values.insert(0, default_option)
            widget_options["placeholder"] = default_option[1]

        return deform.widget.Select2Widget(values=values, **widget_options)

    return deferred_expense_line_choices


def _expense_choice_node(multiple=False, **kw):
    widget_options = kw.pop("widget_options", {})
    widget_options.setdefault("default_option", ("", ""))
    return colander.SchemaNode(
        colander.Set() if multiple else colander.Integer(),
        widget=_get_deferred_expense_line_choices(widget_options),
        validator=forms.deferred_id_validator(
            _get_linkable_expense_lines,
        ),
        **kw,
    )


expense_choice_node = forms.mk_choice_node_factory(
    _expense_choice_node, resource_name="une ligne de note de dépense"
)


class ExpenseSeq(colander.SequenceSchema):
    line = expense_choice_node()


class BookMarkSchema(colander.MappingSchema):
    """
    Schema for bookmarks
    """

    type_id = colander.SchemaNode(
        colander.Integer(), validator=deferred_type_id_validator
    )
    description = colander.SchemaNode(
        colander.String(),
        missing="",
    )
    ht = colander.SchemaNode(colander.Float())
    tva = colander.SchemaNode(colander.Float())
    customer_id = colander.SchemaNode(colander.Integer(), missing=colander.drop)
    project_id = colander.SchemaNode(colander.Integer(), missing=colander.drop)
    business_id = colander.SchemaNode(colander.Integer(), missing=colander.drop)


def get_list_schema(request):
    """
    Build a form schema for expensesheet listing
    """
    schema = forms.lists.BaseListsSchema().clone()

    schema["search"].title = "Numéro de pièce"

    schema.insert(
        0,
        forms.status_filter_node(
            DOC_STATUS_OPTIONS,
            name="justified_status",
            title="Justificatifs",
        ),
    )
    schema.insert(0, forms.status_filter_node(STATUS_OPTIONS))

    schema.insert(
        0,
        forms.month_select_node(
            title="Mois",
            missing=-1,
            default=-1,
            name="month",
            widget_options={"default_val": (-1, "")},
        ),
    )

    schema.insert(
        0,
        forms.year_filter_node(
            name="year",
            title="Année",
            query_func=get_expense_years,
        ),
    )

    schema.insert(2, contractor_filter_node_factory(name="owner_id"))
    forms.add_antenne_option_field(request, schema)

    return schema


def get_files_export_schema():
    title = "Exporter une archive de justificatifs de dépenses"
    schema = colander.Schema(title=title)
    schema.add(contractor_filter_node_factory(name="owner_id", title="Entrepreneur"))
    schema.add(
        forms.month_select_node(
            title="Mois",
            missing=-1,
            default=-1,
            name="month",
            widget_options={"default_val": (-1, "Tous")},
        ),
    )
    schema.add(
        forms.year_select_node(
            name="year",
            title="Année",
            query_func=get_expense_years,
        ),
    )
    return schema


def get_sepa_waiting_schema(sheet):
    topay = sheet.amount_waiting_for_payment()
    topay_label = strings.format_amount(topay, html=False, currency=True)

    class SEPAWaitingSchema(colander.Schema):
        full = colander.SchemaNode(
            colander.Boolean(),
            title=f"En totalité ({topay_label})",
            missing=False,
            default=True,
            description="Mettre l'ensemble de la somme à payer (décocher pour spécifier un montant partiel)",
            widget=deform_extensions.CheckboxToggleWidget(
                true_target="", false_target="amount"
            ),
        )
        amount = colander.SchemaNode(
            AmountType(),
            title="Montant",
            required=True,
            default=topay,
            validator=colander.Range(
                min=1,
                max=topay,
                min_err="Merci de saisir un montant supérieur à 0",
                max_err="Merci de saisir un montant inférieur ou égal à "
                f"{topay_label}",
            ),
        )

    return SEPAWaitingSchema()
