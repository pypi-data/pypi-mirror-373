import deform
from deform_extensions import GridFormWidget
from caerp.forms.expense import ExpensePaymentSchema


def get_payment_form(request, counter=None):
    """
    Return a payment form object
    """
    valid_btn = deform.Button(
        name="submit",
        value="paid",
        type="submit",
        title="Valider",
    )
    schema = ExpensePaymentSchema().bind(request=request)
    if request.context.__name__ == "expense":
        action = request.route_path(
            "/expenses/{id}/addpayment",
            id=request.context.id,
        )
    else:
        action = request.route_path(
            "/expenses/{id}/addpayment",
            id=-1,
        )
    form = deform.Form(
        schema=schema,
        buttons=(valid_btn,),
        formid="paymentform",
        action=action,
        counter=counter,
    )
    GRID_FORM = (
        (
            ("amount", 4),
            ("date", 4),
        ),
        (
            ("mode", 4),
            ("bank_id", 8),
        ),
        (("waiver", 12),),
        (("resulted", 12),),
    )
    form.widget = GridFormWidget(named_grid=GRID_FORM)

    return form
