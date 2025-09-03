import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.expense import (
    EXPENSE_URL,
    ExpenseIndexView,
)


EXPENSE_NUMBERING_CONFIG_URL = os.path.join(EXPENSE_URL, "numbering")


class ExpenseNumberingConfigView(BaseConfigView):
    title = "Numérotation des notes de dépenses"
    description = "Configurer la manière dont sont numérotées les notes de dépenses"

    route_name = EXPENSE_NUMBERING_CONFIG_URL

    keys = (
        "expensesheet_number_template",
        "global_expensesheet_sequence_init_value",
        "year_expensesheet_sequence_init_value",
        "year_expensesheet_sequence_init_date",
        "month_expensesheet_sequence_init_value",
        "month_expensesheet_sequence_init_date",
    )

    schema = get_config_schema(keys)

    info_message = """Il est possible de personaliser le gabarit du numéro de note \
de dépense.<br/ >\
<p>Plusieurs variables et séquences chronologiques sont à disposition.</p>\
<h4>Variables :</h4>\
<ul>\
<li><code>{YYYY}</code> : année, sur 4 digits</li>\
<li><code>{YY}</code> : année, sur 2 digits</li>\
<li><code>{MM}</code> : mois, sur 2 digits</li>\
<li><code>{ANA}</code> : code analytique de l'enseigne</li>\
</ul>\
<h4>Numéros de séquence :</h4>\
<ul>\
<li><code>{SEQGLOBAL}</code> : numéro de séquence global (aucun ràz)</li>\
<li><code>{SEQYEAR}</code> : numéro de séquence annuel (ràz chaque année)</li>\
<li><code>{SEQMONTH}</code> : numéro de séquence mensuel (ràz chaque mois)</li>\
<li><code>{SEQMONTHANA}</code>: numéro de séquence par enseigne et par mois \
(ràz chaque mois)</li>\
</ul>\
<br/ >\
<p>Dans le cas d'une migration depuis un autre outil de gestion, il est possible \
d'initialiser les séquences à une valeur différente de zéro.</p>\
<p>La valeur définie ici correspond à la dernière déjà utilisée, \
la numérotation reprendra au numéro suivant.</p>\
    """
    permission = PERMISSIONS["global.config_accounting"]


def add_routes(config):
    config.add_route(EXPENSE_NUMBERING_CONFIG_URL, EXPENSE_NUMBERING_CONFIG_URL)


def includeme(config):
    add_routes(config)
    config.add_admin_view(
        ExpenseNumberingConfigView,
        parent=ExpenseIndexView,
    )
