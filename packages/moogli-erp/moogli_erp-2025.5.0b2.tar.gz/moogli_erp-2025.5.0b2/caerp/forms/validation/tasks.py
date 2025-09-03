import colander
import deform

from caerp import forms
from caerp.forms.company import company_filter_node_factory
from caerp.forms.third_party.customer import customer_filter_node_factory
from caerp.forms.tasks.task import business_type_filter_node
from caerp.forms.user import follower_filter_node_factory


TYPE_OPTIONS = (
    (
        "both",
        "Tous",
    ),
    (
        "invoice",
        "Seulement les factures",
    ),
    (
        "internalinvoice",
        "Seulement les factures internes",
    ),
    (
        "cancelinvoice",
        "Seulement les avoirs",
    ),
    (
        "internalcancelinvoice",
        "Seulement les avoirs internes",
    ),
    (
        "internal",
        "Seulement les factures/avoirs internes",
    ),
    ("external", "Seulement les factures/avoirs externes"),
)


def get_list_schema(request, excludes=()):
    """
    Return a schema for invoice validation listing
    The schema is run on request so it can access db data directly
    """
    schema = forms.lists.BaseListsSchema().clone()
    del schema["search"]
    schema.insert(
        0,
        customer_filter_node_factory(
            is_global=True,
            name="customer_id",
            title="Client",
            with_invoice=True,
        ),
    )
    schema.insert(0, business_type_filter_node())
    if "doctype" not in excludes:
        schema.insert(
            0,
            colander.SchemaNode(
                colander.String(),
                name="doctype",
                title="Types de factures",
                widget=deform.widget.SelectWidget(values=TYPE_OPTIONS),
                validator=colander.OneOf([s[0] for s in TYPE_OPTIONS]),
                missing="both",
                default="both",
            ),
        )
    schema.insert(0, company_filter_node_factory(name="company_id", title="Enseigne"))
    schema.insert(
        0,
        follower_filter_node_factory(
            name="follower_id",
            title="Accompagnateur",
        ),
    )
    forms.add_antenne_option_field(request, schema)
    return schema
