"""
Job related forms
"""
import colander
import deform
from caerp import forms


STATUS_OPTIONS = (
    (
        "",
        "Toutes",
    ),
    (
        "planned",
        "Les tâches plannifiées",
    ),
    (
        "failed",
        "Les tâches ayant échouées",
    ),
    (
        "completed",
        "Les tâches terminées",
    ),
)
TYPES_OPTIONS = (
    (
        "",
        "Tous",
    ),
    ("csv_import", "Importation de données csv"),
)


def get_list_schema():
    """
    Return the schema for the job list search form
    """
    schema = forms.lists.BaseListsSchema().clone()
    del schema["search"]
    schema.insert(
        0,
        forms.status_filter_node(
            STATUS_OPTIONS,
            default=colander.drop,
        ),
    )
    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="type_",
            title="Type",
            widget=deform.widget.SelectWidget(values=TYPES_OPTIONS),
            validator=colander.OneOf([s[0] for s in TYPES_OPTIONS]),
            missing=colander.drop,
        ),
    )

    return schema
