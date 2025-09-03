"""
Form schema used to configure BusinessType and TaskMention association
"""
import colander
from colanderalchemy import SQLAlchemySchemaNode

from caerp.forms import customize_field
from caerp.forms.tasks.task import task_type_validator
from caerp.models.project.mentions import BusinessTypeTaskMention


def _get_business_type_task_mention_schema():
    """
    Build a schema for BusinessTypeTaskMention configuration

    :rtype: :class:`colanderalchemy.SQLAlchemySchemaNode`
    """
    schema = SQLAlchemySchemaNode(
        BusinessTypeTaskMention,
        includes=("task_mention_id", "business_type_id", "doctype", "mandatory"),
    )
    customize_field(
        schema,
        "doctype",
        validator=task_type_validator,
    )
    customize_field(
        schema,
        "mandatory",
        typ=colander.String(),
        validator=colander.OneOf(
            ("true", "false"),
        ),
        missing=colander.drop,
    )
    return schema


class BusinessTypeMentionEntry(colander.SequenceSchema):
    item = _get_business_type_task_mention_schema()


class BusinessTypeMentionEntries(colander.MappingSchema):
    items = BusinessTypeMentionEntry()
