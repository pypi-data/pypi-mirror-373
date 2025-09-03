import colander

from caerp.forms.tasks.payment import get_payment_schema


def get_sap_payment_schema(*args, **kwargs):
    schema = get_payment_schema(*args, **kwargs)
    # Unset default value to current date
    schema["date"].default = colander.null

    # … And warns how important it is for SAP
    schema["date"].description = (
        "Doit impérativement correspondre à la date de paiement "
        "effectif par le client (date du chèque, du virement, etc…)."
    )
    return schema
