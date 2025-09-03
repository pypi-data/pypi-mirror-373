from deform import Form
from deform_extensions import GridFormWidget

from caerp.forms.third_party.supplier import (
    get_supplier_schema,
)
from caerp.views import submit_btn

SUPPLIER_FORM_GRID = (
    (("code", 6),),
    (
        ("registration", 6),
        ("tva_intracomm", 6),
    ),
    (("company_name", 12),),
    (("address", 12),),
    (("additional_address", 12),),
    (
        ("zip_code", 4),
        ("city", 8),
    ),
    (("country", 6),),
    (("civilite", 6),),
    (
        ("lastname", 6),
        ("firstname", 6),
    ),
    (("function", 12),),
    (("email", 12),),
    (
        ("mobile", 6),
        ("phone", 6),
    ),
    (("fax", 6),),
    (
        ("compte_cg", 6),
        ("compte_tiers", 6),
    ),
    (("bank_account_iban", 12),),
    (
        ("bank_account_bic", 6),
        ("bank_account_owner", 6),
    ),
)


def get_supplier_form(request, counter=None):
    """
    Returns the supplier add/edit form
    :param obj request: Pyramid's request object
    :param obj counter: An iterator for field number generation
    :returns: a deform.Form instance
    """
    schema = get_supplier_schema()
    schema = schema.bind(request=request)
    form = Form(
        schema,
        buttons=(submit_btn,),
        counter=counter,
        formid="supplier",
    )
    form.widget = GridFormWidget(named_grid=SUPPLIER_FORM_GRID)
    return form
