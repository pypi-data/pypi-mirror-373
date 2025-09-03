"""
BankRemittance handling forms schemas
"""
import colander
from caerp import forms
from caerp.forms.lists import BaseListsSchema
from caerp.models.payments import PaymentMode, BankAccount


@colander.deferred
def deferred_payment_mode_widget(node, kw):
    """
    Renvoie le widget pour la sélection du mode de paiement
    """
    options = [(mode.label, mode.label) for mode in PaymentMode.query()]
    options.insert(0, ("", "Tous"))
    return forms.get_select(options)


@colander.deferred
def deferred_bank_account_widget(node, kw, add_all_option=None):
    """
    Renvoie le widget pour la sélection d'un compte bancaire
    """
    options = [(bank.id, bank.label) for bank in BankAccount.query()]
    options.insert(0, ("", "Tous"))
    return forms.get_select(options)


def get_bank_remittances_list_schema():
    """
    Return the schema for the bank remittances search list
    """
    schema = BaseListsSchema().clone()
    schema["search"].title = "Numéro de remise"
    schema.insert(
        1,
        colander.SchemaNode(
            colander.String(),
            name="payment_mode",
            title="Mode de paiement",
            widget=deferred_payment_mode_widget,
            missing=colander.drop,
        ),
    )
    schema.insert(
        2,
        colander.SchemaNode(
            colander.Integer(),
            name="bank_id",
            title="Compte bancaire",
            widget=deferred_bank_account_widget,
            missing=colander.drop,
        ),
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="closed",
            label="Inclure les remises fermées",
            title="",
            default=True,
        )
    )
    return schema


class RemittanceDateSchema(colander.Schema):
    """
    Schema for the remittance date input
    """

    remittance_date = colander.SchemaNode(colander.Date())
