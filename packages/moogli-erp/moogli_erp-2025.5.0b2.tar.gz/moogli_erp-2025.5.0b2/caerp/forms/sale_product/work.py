"""
Work item related form schemas
"""
import colander
import functools
from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.task import WorkUnit
from caerp.models.company import Company
from caerp.models.sale_product.base import BaseSaleProduct
from caerp.models.sale_product.work_item import WorkItem
from caerp.utils.html import clean_html
from caerp import forms
from caerp.forms.custom_types import (
    AmountType,
    QuantityType,
)


def _deferred_company_id_filter(node, kw):
    """
    Build a SQLAlchemy filter for company_id at execution time
    """
    context = kw["request"].context
    if isinstance(context, WorkItem):
        return {"company_id": context.sale_product_work.company_id}
    elif isinstance(context, Company):
        return {"company_id": context.id}
    elif isinstance(context, BaseSaleProduct):
        return {"company_id": context.company_id}
    else:
        raise Exception("Context is not one of WorkItem, Company {}".format(context))


def check_label_if_no_sale_product_id(form, values):
    """
    On add, if no label is provided, we need a base_sale_product_id
    """
    label = values.get("label")
    base_sale_product_id = values.get("base_sale_product_id")
    if not label and not base_sale_product_id:
        raise colander.Invalid(
            "Un label ou un base_sale_product_id doivent être fourni pour            "
            " la configuration d'un work_item"
        )


def customize_work_item_schema(schema, from_work_schema=False, add=False):
    """
    Customize the work item schema to add custom validators and defaults


    :param schema: The schema to customize

    :param bool from_work_schema: Is this customization done a SaleProductWork
    schema, in this case we add special functionnalities

    :return: schema
    """
    customize = functools.partial(forms.customize_field, schema)
    if "locked" in schema:
        customize("locked", missing=colander.drop)
    customize("type_", validator=colander.OneOf(BaseSaleProduct.SIMPLE_TYPES))
    customize(
        "description",
        preparer=clean_html,
    )

    customize("_ht", typ=AmountType(5), missing=None)
    customize("_supplier_ht", typ=AmountType(5), missing=None)
    customize(
        "_unity",
        validator=forms.get_deferred_select_validator(WorkUnit, id_key="label"),
        missing=None,
    )

    # On change le nom des noeuds pour passer par les hybrid_attribute de notre
    # modèle (cf la définition de la classe WorkItem)
    for field in ("ht", "supplier_ht", "unity", "mode"):
        customize("_%s" % field, name=field)

    customize(
        "base_sale_product_id",
        validator=forms.get_deferred_select_validator(
            BaseSaleProduct,
            filters=[
                _deferred_company_id_filter,
                BaseSaleProduct.type_.in_(BaseSaleProduct.SIMPLE_TYPES),
            ],
        ),
    )

    if add or from_work_schema:
        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="label",
                validator=colander.Length(0, 255),
                missing=colander.drop,
            )
        )
        # Ce champ n'est pas requis lors de l'ajout d'un produit composé, un
        # BaseSaleProduct est alors créé en post_format
        customize("base_sale_product_id", missing=colander.drop)

        schema.validator = check_label_if_no_sale_product_id

    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="sync_catalog",
            missing=colander.drop,
        )
    )

    if "quantity" in schema:
        customize("quantity", typ=QuantityType())

    return schema


def get_work_item_add_edit_schema(add=False):
    """
    Build a work item add edit schema
    :return:
    """
    excludes = (
        "id",
        "base_sale_product",
        "sale_product_work_id",
        "sale_product_work",
        "total_ht",
    )
    schema = SQLAlchemySchemaNode(WorkItem, excludes=excludes)

    schema = customize_work_item_schema(schema, add=add)
    return schema
