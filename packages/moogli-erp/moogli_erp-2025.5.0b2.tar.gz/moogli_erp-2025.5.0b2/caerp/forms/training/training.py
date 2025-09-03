"""
Schema used for trainings manipulation
"""
import colander
import deform

from caerp.forms.lists import BaseListsSchema
from caerp.forms import year_filter_node

from caerp.forms.company import company_filter_node_factory
from caerp.forms.third_party.customer import customer_filter_node_factory

from caerp.models.task.invoice import get_invoice_years


def get_training_list_schema(is_global):
    """
    Build the Training list filter schema
    """
    schema = BaseListsSchema().clone()
    schema["search"].title = "Numéro de facture"
    schema.add_before(
        "items_per_page",
        year_filter_node(
            query_func=get_invoice_years,
            title="Année de facturation",
            name="invoicing_year",
        ),
    )
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.String(),
            title="BPF renseigné",
            name="bpf_filled",
            widget=deform.widget.SelectWidget(
                values=(
                    ("", "Peu importe"),
                    ("yes", "Renseigné"),
                    ("no", "Non renseigné ou partiellement renseigné"),
                )
            ),
            missing=colander.drop,
        ),
    )

    if is_global:
        schema.add_before(
            "items_per_page", company_filter_node_factory(name="company_id")
        )
    schema.add_before(
        "items_per_page",
        customer_filter_node_factory(name="customer_id", is_global=is_global),
    )
    return schema
