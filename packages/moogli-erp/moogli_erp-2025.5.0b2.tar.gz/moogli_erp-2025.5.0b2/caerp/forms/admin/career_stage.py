import functools
from colanderalchemy import SQLAlchemySchemaNode
from caerp.models.career_stage import CareerStage, STAGE_TYPE_OPTIONS
from caerp.models.user.userdatas import CaeSituationOption
from caerp.forms import (
    customize_field,
    get_deferred_select,
    get_select,
)


def customize_schema(schema):
    """
    Customize the form schema
    :param obj schema: A CareerStage schema
    """
    customize = functools.partial(customize_field, schema)
    customize("cae_situation_id", get_deferred_select(CaeSituationOption))
    customize("stage_type", get_select(STAGE_TYPE_OPTIONS))


def get_career_stage_schema():
    schema = SQLAlchemySchemaNode(
        CareerStage,
        includes=(
            "name",
            "cae_situation_id",
            "stage_type",
        ),
    )
    customize_schema(schema)
    return schema
