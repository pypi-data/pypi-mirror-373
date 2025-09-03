import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.task.insurance import TaskInsuranceOption

from caerp.forms import (
    customize_field,
)


@colander.deferred
def deferred_rate_widget(node, kw):
    readonly = False
    if isinstance(kw["request"].context, TaskInsuranceOption):
        readonly = kw["request"].context.is_used
    return deform.widget.TextInputWidget(
        input_append="%",
        readonly=readonly,
    )


@colander.deferred
def deferred_rate_missing(node, kw):
    if isinstance(kw["request"].context, TaskInsuranceOption):
        result = kw["request"].context.rate
    else:
        result = colander.required
    return result


def get_admin_task_insurance_schema():
    """
    Build the task insurance  admin schema
    """
    schema = SQLAlchemySchemaNode(
        TaskInsuranceOption,
        includes=(
            "label",
            "rate",
            "help_text",
            "title",
            "full_text",
            "order",
        ),
    )
    customize_field(
        schema,
        "label",
        title="Libellé",
        description="Libellé utilisé dans l'interface",
    )
    customize_field(
        schema,
        "full_text",
        widget=deform.widget.TextAreaWidget(cols=80, rows=4),
    )
    customize_field(
        schema,
        "rate",
        description="Taux en pourcentage (ex : 10.5)",
        validator=colander.Range(
            0,
            99,
            min_err="Un montant positif est attendu",
            max_err="Une valeur inférieur à 100 est attendue",
        ),
        missing=deferred_rate_missing,
        widget=deferred_rate_widget,
    )
    customize_field(schema, "order", widget=deform.widget.HiddenWidget())
    return schema
