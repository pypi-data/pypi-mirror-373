import colander
from colanderalchemy import SQLAlchemySchemaNode

from caerp.forms import customize_field
from caerp.forms.lists import BaseListsSchema
from caerp.models.project.business import Business


def get_list_schema():
    """
    Return the schema for the project search form
    :rtype: colander.Schema
    """
    schema = BaseListsSchema().clone()

    schema["search"].title = "Nom de l'affaire"

    return schema


class APIBusinessListSchema(BaseListsSchema):
    project_id = colander.SchemaNode(
        colander.Integer(),
        name="project_id",
        missing=colander.drop,
    )

    customer_id = colander.SchemaNode(
        colander.Integer(),
        name="customer_id",
        missing=colander.drop,
    )


def get_business_edit_schema():
    """
    Build the businedd edition schema

    :rtype: :class:`colander.Schema`
    """
    schema = SQLAlchemySchemaNode(Business, includes=("name",))
    customize_field(schema, "name", title="Nom de l'affaire")
    return schema
