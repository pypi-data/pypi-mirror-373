import functools
import logging
import colander
from typing import Optional

from deform import widget
from colanderalchemy import SQLAlchemySchemaNode
from sqlalchemy.orm import load_only

from caerp.utils.html import (
    clean_html,
)
from caerp.views.third_party.customer.routes import CUSTOMER_ITEM_ROUTE
from caerp.models.tva import (
    Tva,
    Product,
)
from caerp.models.task import WorkUnit
from caerp.models.task.mentions import TaskMention
from caerp.models.task.task import (
    DiscountLine,
    PostTTCLine,
    TaskLineGroup,
    TaskLine,
    ALL_STATES,
    Task,
)

from caerp import forms
from caerp.forms.custom_types import (
    AmountType,
    QuantityType,
)
from caerp.forms.user import get_deferred_user_choice

from caerp.models.project.types import BusinessType
from caerp.models.project.business import Business
from caerp.models.third_party import Customer
from caerp.models.project.project import (
    Project,
    ProjectCustomer,
    ProjectBusinessType,
)
from caerp.models.project import Phase
from caerp.models.services.naming import NamingService

from caerp.models.task.insurance import TaskInsuranceOption
from .base import (
    business_type_id_validator,
    task_after_bind,
    get_task_type_from_factory,
)


logger = logging.getLogger(__name__)


def tva_product_validator(node, value):
    """
    Validator checking that tva and product_id matches
    """
    product_id = value.get("product_id")
    if product_id is not None:
        tva_id = value.get("tva_id")
        if tva_id is not None:
            tva = Tva.get(tva_id)
            if product_id not in [p.id for p in tva.products]:
                exc = colander.Invalid(
                    node, "Ce produit ne correspond pas à la TVA configurée"
                )
                exc["product_id"] = (
                    "Le code produit doit correspondre à la                    "
                    " TVA configurée pour cette prestation"
                )
                raise exc


def _customize_discountline_fields(schema):
    """
    Customize DiscountLine colander schema related fields

    :param obj schema: The schema to modify
    """
    customize = functools.partial(forms.customize_field, schema)
    customize("id", widget=widget.HiddenWidget())
    customize("task_id", missing=colander.required)
    customize(
        "description",
        widget=widget.TextAreaWidget(),
        validator=forms.textarea_node_validator,
        preparer=clean_html,
    )
    customize(
        "amount",
        typ=AmountType(5),
        missing=colander.required,
    )
    customize(
        "tva",
        typ=AmountType(2),
        validator=forms.get_deferred_select_validator(Tva, id_key="value"),
        missing=colander.required,
    )

    return schema


def _customize_post_ttc_line_fields(schema):
    """
    Customize PostTTCLine colander schema related fields

    :param obj schema: The schema to modify
    """
    customize = functools.partial(forms.customize_field, schema)
    customize("id", widget=widget.HiddenWidget())
    customize("task_id", missing=colander.required)
    customize(
        "amount",
        typ=AmountType(5),
        missing=colander.required,
    )
    return schema


def _customize_taskline_fields(schema):
    """
    Customize TaskLine colander schema related fields

    :param obj schema: The schema to modify
    """
    schema.validator = tva_product_validator
    customize = functools.partial(forms.customize_field, schema)
    customize("id", widget=widget.HiddenWidget())
    customize(
        "description",
        widget=widget.TextAreaWidget(),
        validator=forms.textarea_node_validator,
        preparer=clean_html,
    )
    customize("cost", typ=AmountType(5), missing=colander.required)
    customize("quantity", typ=QuantityType(), missing=colander.required)
    customize(
        "unity",
        validator=forms.get_deferred_select_validator(WorkUnit, id_key="label"),
        missing=colander.drop,
    )
    customize(
        "tva",
        typ=AmountType(2),
        validator=forms.get_deferred_select_validator(Tva, id_key="value"),
        missing=colander.required,
    )
    customize(
        "product_id",
        validator=forms.get_deferred_select_validator(Product),
        missing=colander.drop,
    )
    return schema


def _customize_tasklinegroup_fields(schema):
    """
    Customize TaskLineGroup colander schema related fields

    :param obj schema: The schema to modify
    """
    # pré-remplissage de la variable schema de la fonction
    # forms.customize_field
    customize = functools.partial(forms.customize_field, schema)
    customize("id", widget=widget.HiddenWidget())
    customize("task_id", missing=colander.required)
    customize(
        "description",
        widget=widget.TextAreaWidget(),
        preparer=clean_html,
    )
    customize(
        "lines",
        validator=colander.Length(
            min=1,
            min_err="Une prestation au moins doit être incluse",
        ),
    )
    if "lines" in schema:
        child_schema = schema["lines"].children[0]
        _customize_taskline_fields(child_schema)

    return schema


@colander.deferred
def deferred_task_cohesion_validator(node: SQLAlchemySchemaNode, kw: dict):
    """
    Check that the Task data is globally valid
    Tva used in the doc ...
    """
    if "request" not in kw or kw["request"].context is None:
        return None
    task: Task = kw["request"].context
    validators = []

    def _discount_validator(node, values):
        logger.debug("In the discount validator")
        logger.debug(node)

        line_tvas = [line.tva for line in task.all_lines]
        logger.debug(f"Line tvas {line_tvas}")
        for discount in task.discounts:
            if discount.tva not in line_tvas:
                logger.debug(f"The discount tva {discount.tva}")

                raise colander.Invalid(
                    node["discounts"],
                    "Une remise utilise une TVA qui n'est pas utilisée dans "
                    "les prestations",
                )
        discount_ht = task.discount_total_ht()
        line_ht = task.groups_total_ht()
        if discount_ht and abs(discount_ht) > abs(line_ht):
            raise colander.Invalid(
                node["discounts"],
                "Le montant des remises dépasse le montant des prestations",
            )

    if task.discounts and "discounts" in node:
        logger.debug("TASK HAS DISCOUNTS")
        validators.append(_discount_validator)
    else:
        logger.debug("TASK HAS NO DISCOUNTS")
    return colander.All(*validators)


def _customize_task_fields(schema):
    """
    Add Field customization to the task form schema

    :param obj schema: The schema to modify
    """
    customize = functools.partial(forms.customize_field, schema)
    schema.after_bind = task_after_bind
    customize("id", widget=widget.HiddenWidget(), missing=colander.drop)
    if "status":
        customize(
            "status",
            widget=widget.SelectWidget(values=list(zip(ALL_STATES, ALL_STATES))),
            validator=colander.OneOf(ALL_STATES),
        )
    customize(
        "status_comment",
        widget=widget.TextAreaWidget(),
    )
    customize(
        "status_user_id",
        widget=get_deferred_user_choice(),
    )
    customize(
        "business_type_id",
        validator=business_type_id_validator,
        missing=colander.drop,  # We drop it in edit mode
    )
    customize(
        "description",
        widget=widget.TextAreaWidget(),
        validator=forms.textarea_node_validator,
        missing=colander.required,
    )
    customize("date", missing=colander.required)
    for field_name in "ht", "ttc", "tva", "expenses_ht":
        customize(field_name, typ=AmountType(5))

    customize(
        "address",
        widget=widget.TextAreaWidget(),
        validator=forms.textarea_node_validator,
        missing=colander.required,
    )
    customize(
        "workplace",
        widget=widget.TextAreaWidget(),
    )
    customize(
        "payment_conditions",
        widget=widget.TextAreaWidget(),
        validator=forms.textarea_node_validator,
        missing=colander.required,
    )
    customize(
        "insurance_id",
        validator=forms.get_deferred_select_validator(TaskInsuranceOption),
        # TODO : dynamiquement setter le missing
        missing=colander.drop,
    )
    customize(
        "mentions",
        children=forms.get_sequence_child_item(TaskMention),
    )
    customize(
        "line_groups",
        validator=colander.Length(min=1, min_err="Une entrée est requise"),
        missing=colander.required,
    )
    if "line_groups" in schema:
        child_schema = schema["line_groups"].children[0]
        _customize_tasklinegroup_fields(child_schema)

    if "discounts" in schema:
        child_schema = schema["discounts"].children[0]
        _customize_discountline_fields(child_schema)

    schema.validator = deferred_task_cohesion_validator
    return schema


def get_add_edit_discountline_schema(includes=None, excludes=None):
    """
    Return add edit schema for DiscountLine edition

    :param tuple includes: field that should be included (if None,
    excludes will be used instead)
    :param tuple excludes: Model attributes that should be excluded for schema
    generation (if None, a default one is provided)

    :rtype: `colanderalchemy.SQLAlchemySchemaNode`
    """
    if includes is not None:
        excludes = None

    schema = SQLAlchemySchemaNode(
        DiscountLine,
        includes=includes,
        excludes=excludes,
    )
    schema = _customize_discountline_fields(schema)
    return schema


def get_add_edit_post_ttc_line_schema(includes=None, excludes=None):
    """
    Return add edit schema for PostTTCLine edition

    :param tuple includes: field that should be included (if None,
    excludes will be used instead)
    :param tuple excludes: Model attributes that should be excluded for schema
    generation (if None, a default one is provided)

    :rtype: `colanderalchemy.SQLAlchemySchemaNode`
    """
    if includes is not None:
        excludes = None

    schema = SQLAlchemySchemaNode(
        PostTTCLine,
        includes=includes,
        excludes=excludes,
    )
    schema = _customize_post_ttc_line_fields(schema)
    return schema


def get_add_edit_taskline_schema(includes=None, excludes=None):
    """
    Return add edit schema for TaskLine edition

    :param tuple includes: field that should be included (if None,
    excludes will be used instead)
    :param tuple excludes: Model attributes that should be excluded for schema
    generation (if None, a default one is provided)

    :rtype: `colanderalchemy.SQLAlchemySchemaNode`
    """
    if includes is not None:
        excludes = None

    schema = SQLAlchemySchemaNode(
        TaskLine,
        includes=includes,
        excludes=excludes,
    )
    schema = _customize_taskline_fields(schema)
    return schema


def get_add_edit_tasklinegroup_schema(includes=None, excludes=None):
    """
    Return add edit schema for TaskLineGroup edition

    :param tuple includes: field that should be included (if None,
    excludes will be used instead)
    :param tuple excludes: Model attributes that should be excluded for schema
    generation (if None, a default one is provided)

    :rtype: `colanderalchemy.SQLAlchemySchemaNode`
    """
    if includes is not None:
        excludes = None

    schema = SQLAlchemySchemaNode(TaskLineGroup, includes=includes, excludes=excludes)
    schema = _customize_tasklinegroup_fields(schema)
    return schema


def get_edit_task_schema(
    factory, isadmin=False, includes=None, excludes=None, **kw
) -> SQLAlchemySchemaNode:
    """
    Return a schema for task edition

    :param class factory: The type of task we want to edit
    :param bool isadmin: Are we asking for an admin schema ?
    :param tuple includes: field that should be included (if None,
    excludes will be used instead)
    :param tuple excludes: Model attributes that should be excluded for schema
    generation (if None, a default one is provided)
    :returns: `colanderalchemy.SQLAlchemySchemaNode`
    """
    if includes is not None:
        excludes = None
    elif excludes is None:
        excludes = (
            "id",
            "children",
            "parent",
            "exclude",
            "phase_id",
            "owner_id",
            "company_id",
            "project_id",
            "customer_id",
            "expenses",
            "insurance",
        )
        if not isadmin:
            excludes = excludes + ("status",)

    schema = SQLAlchemySchemaNode(factory, excludes=excludes, includes=includes, **kw)
    schema = _customize_task_fields(schema)
    return schema


task_type_validator = colander.OneOf(("invoice", "cancelinvoice", "estimation"))


def business_type_filter_node(
    name="business_type_id", title="Type d'affaire", default="all"
):
    """
    "Filter by business type" SchemaNode for listings
    """

    return colander.SchemaNode(
        colander.String(),
        name=name,
        title=title,
        widget=deferred_business_type_options,
        validator=deferred_business_type_validator,
        missing=default,
        default=default,
    )


@colander.deferred
def deferred_business_type_options(node, kw):
    business_type_options = get_business_types_option_list()
    return widget.SelectWidget(values=business_type_options)


@colander.deferred
def deferred_business_type_validator(node, kw):
    business_type_options = get_business_types_option_list()
    return colander.OneOf([str(b[0]) for b in business_type_options])


def get_business_types_option_list():
    """
    Return structured option list for business types widget
    """
    options = [
        (business_type.id, business_type.label.title())
        for business_type in BusinessType.query().filter_by(active=True)
    ]
    options.insert(0, ("all", "Tous"))
    return options


@colander.deferred
def deferred_task_add_validator(node, kw):
    request = kw["request"]
    dbsession = request.dbsession

    def task_add_data_integrity(schema: SQLAlchemySchemaNode, appstruct: dict):
        """
        Check that submitted data are compatible with each others

        :raises: colander.Invalid if an error is raised
        """
        project_id = appstruct["project_id"]
        customer_id = appstruct["customer_id"]
        business_type_id = appstruct.get("business_type_id")
        project = Project.get(project_id)
        customer = Customer.get(customer_id)

        if (
            dbsession.query(BusinessType.id)
            .filter_by(id=business_type_id, project_type_id=project.project_type_id)
            .count()
            == 0
        ) and (
            dbsession.query(ProjectBusinessType)
            .filter_by(project_id=project_id, business_type_id=business_type_id)
            .count()
            == 0
        ):
            error = "Cet type d'affaire ne peut être menée dans ce projet"
            raise forms.colander_invalid_on_multiple_nodes(
                node, ["project_id", "business_type_id"], error
            )

        phase_id = appstruct.get("phase_id")
        if phase_id:
            if Phase.query().filter_by(id=phase_id, project_id=project_id).count() == 0:
                error = "Ce sous-dossier n'appartient pas au projet sélectionné"
                raise forms.colander_invalid_on_multiple_nodes(
                    node, ["project_id", "phase_id"], error
                )

        if customer.type == "company" and not customer.registration:
            come_from = request.referrer
            query_params = {"action": "edit"}
            if come_from:
                if "?" in come_from:
                    come_from += f"&customer_id={customer_id}"
                else:
                    come_from += f"?customer_id={customer_id}"
                query_params["come_from"] = come_from

            url = request.route_url(
                CUSTOMER_ITEM_ROUTE,
                id=customer_id,
                _query=query_params,
            )
            raise colander.Invalid(
                node["customer_id"],
                "Le numéro d'immatriculation est obligatoire pour facturer ce client. "
                f"Veuillez le renseigner sur <a href={url}>sa fiche client</a>.",
            )

    return task_add_data_integrity


def get_new_task_name(
    factory, project: Optional[Project] = None, business: Optional[Business] = None
) -> str:
    """Build a default new task name

    :param factory: Estimation / Invoice
    :type factory: class

    :param project: project in which we add a task
    :param business: business in which we add a task (case of progress invoicing)

    :return: the name to use for the new task
    """
    name = ""
    tasktype = get_task_type_from_factory(factory)
    if project is not None:
        method = "get_next_{0}_index".format(tasktype)
        number = getattr(project, method)()

        type_label = NamingService.get_label_for_context(tasktype, project)
        name = f"{type_label} {number}"
    else:
        if tasktype == "estimation":
            name = "Nouveau devis"
        else:
            name = "Nouvelle facture"
    return name


def get_add_task_schema(
    factory,
    request,
    company_id: int,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    phase_id: Optional[int] = None,
) -> SQLAlchemySchemaNode:
    """
    Build the Task add schema

    NB : must be called during the request processing in a view's method,
    not once as class attribute (once in the WSGI context)
    """
    dbsession = request.dbsession
    includes = (
        "name",
        "customer_id",
        "project_id",
        "phase_id",
        "business_type_id",
    )
    schema = SQLAlchemySchemaNode(factory, includes=includes)
    customize = functools.partial(forms.customize_field, schema)

    project = None
    business_type_id = None

    # On détermine les valeurs par défaut si le contexte courant est un projet
    if project_id is not None:
        # Le dossier
        project = Project.get(project_id)

        # Le client (s'il n'y en a qu'un sur le dossier)
        query = dbsession.query(ProjectCustomer.c.customer_id).filter(
            ProjectCustomer.c.project_id == project_id
        )
        if query.count() == 1:
            customer_id = query.scalar()

        # Le type d'affaire (s'il n'y en a qu'un sur le dossier)
        btypes = Project.get(project_id).get_all_business_types(request)
        if len(btypes) == 1:
            business_type_id = btypes[0].id

    customize(
        "name",
        title="Nom du document",
        default=get_new_task_name(factory, project),
        description="Ce nom n'apparaît pas dans le document final",
    )

    customize(
        "customer_id",
        title="Client",
        missing=colander.required,
        default=customer_id,
        validator=colander.OneOf(
            [
                c.id
                for c in dbsession.query(Customer)
                .options(load_only("id"))
                .filter(Customer.company_id == company_id)
                .filter(Customer.archived == False)
            ]
        ),
    )
    customize(
        "project_id",
        title="Dossier",
        default=project_id,
        validator=colander.OneOf(
            [
                p.id
                for p in dbsession.query(Project)
                .options(load_only("id"))
                .filter(Project.company_id == company_id)
                .filter(Project.archived == False)
            ]
        ),
    )
    customize(
        "business_type_id",
        title="Type d'affaire",
        validator=business_type_id_validator,
        default=business_type_id,
    )
    customize("phase_id", missing=None, default=phase_id, title="Sous-dossier")

    schema.validator = deferred_task_add_validator
    return schema
