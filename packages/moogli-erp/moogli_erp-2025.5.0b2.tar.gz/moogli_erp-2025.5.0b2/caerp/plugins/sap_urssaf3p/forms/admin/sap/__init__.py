import colander
import deform

from caerp import forms
from caerp.models.payments import BankAccount


@colander.deferred
def deferred_bank_account_widget(node, kw):
    """
    Renvoie le widget pour la sélection d'un compte bancaire
    """
    options = [(bank.id, bank.label) for bank in BankAccount.query()]
    widget = forms.get_select(options)
    return widget


@colander.deferred
def deferred_bank_account_validator(node, kw):
    return colander.OneOf([bank.id for bank in BankAccount.query()])


class SapAvanceImmediateConfigSchema(colander.Schema):

    urssaf3p_payment_bank_id = colander.SchemaNode(
        colander.Integer(),
        title="Compte bancaire",
        widget=deferred_bank_account_widget,
        validator=deferred_bank_account_validator,
        default=forms.get_deferred_default(BankAccount),
        description="Configurables dans Configuration - Module Ventes - "
        "Configuration comptable des encaissements",
    )

    urssaf3p_automatic_payment_creation = colander.SchemaNode(
        # Tricky : ne pas utiliser un colander.Boolean() car ça n'est pas stocké comme tel
        colander.Integer(),
        title="Création automatique des paiements en avance immédiate",
        description=(
            "Si coché, les paiements validés par l'URSSAF seront "
            "automatiquement créés dans MoOGLi."
        ),
        widget=deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    )
