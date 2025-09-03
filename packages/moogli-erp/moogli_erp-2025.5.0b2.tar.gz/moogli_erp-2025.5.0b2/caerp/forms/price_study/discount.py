import functools
import colander
from colanderalchemy import SQLAlchemySchemaNode

from caerp.utils.html import clean_html

from caerp.models.tva import Tva
from caerp.models.price_study.discount import PriceStudyDiscount
from caerp.forms.price_study.common import (
    deferred_default_tva_id,
)
from caerp.forms.custom_types import (
    AmountType,
    QuantityType,
)
from caerp import forms


def customize_schema(schema):
    """
    Customize the fields to set custom default/missing/validators

    :param obj schema: A SQLAlchemySchemaNode instance
    :returns: The modified schema
    """
    customize = functools.partial(forms.customize_field, schema)
    if "description" in schema:
        customize("description", preparer=clean_html)

    if "amount" in schema:
        customize("amount", typ=AmountType(5), missing=colander.required)

    if "percentage" in schema:
        customize(
            "percentage",
            typ=QuantityType(),
            validator=colander.Range(0, 100),
            missing=colander.required,
        )

    if "tva_id" in schema:
        customize(
            "tva_id",
            validator=forms.get_deferred_select_validator(Tva),
            default=deferred_default_tva_id,
            missing=None,
        )

    if "type_" in schema:
        customize(
            "type_",
            validator=colander.OneOf(("amount", "percentage")),
            missing="amount",
        )

    return schema


def get_discount_add_edit_schema(type_):
    """
    Build a schema for discount add edit
    """
    excludes = ("price_study", "price_study_id", "tva")
    if type_ == "amount":
        excludes += ("percentage",)
    else:
        excludes += ("amount",)

    schema = SQLAlchemySchemaNode(PriceStudyDiscount, excludes=excludes)
    return customize_schema(schema)
