from types import MethodType

import colander
from caerp_base.consts import CIVILITE_OPTIONS
from colanderalchemy import SQLAlchemySchemaNode

from caerp import forms
from caerp.consts.insee_countries import COUNTRIES
from caerp.consts.insee_departments import DEPARTMENTS
from caerp.forms.third_party.customer import get_individual_customer_schema
from caerp.plugins.sap_urssaf3p.models.customer import UrssafCustomerData
from caerp.utils.colanderalchemy import patched_objectify


def get_urssaf_data_schema() -> SQLAlchemySchemaNode:
    result = SQLAlchemySchemaNode(UrssafCustomerData)

    result.objectify = MethodType(patched_objectify, result)
    return result


def get_urssaf_individual_customer_schema() -> SQLAlchemySchemaNode:
    """
    Build the customer form schema specific to Urssaf related data
    """
    schema = get_individual_customer_schema()
    schema.objectify = MethodType(patched_objectify, schema)
    schema["urssaf_data"] = get_urssaf_data_schema()

    for field in (
        "civilite",
        "firstname",
        "email",
        "mobile",
        "city",
        "city_code",
        "zip_code",
        "address",
    ):
        schema[field].missing = colander.required

    schema["civilite"].validator = colander.OneOf(
        [opt[0] for opt in CIVILITE_OPTIONS[1:]]
    )
    schema["mobile"].validator = colander.Regex(
        r"^(0|\+33)[6-7]([0-9]{2}){4}$",
        msg=(
            "Veuillez saisir un numéro de mobile valide sans espace "
            "(0610111213 ou  +33610111213)"
        ),
    )

    schema["firstname"].label = "Prénom(s)"
    schema[
        "firstname"
    ].description = "Prénom(s) d'usage du client séparés par des espaces"

    for field in (
        "bank_account_bic",
        "bank_account_iban",
        "bank_account_owner",
    ):
        schema[field].missing = colander.required

    for field in (
        "street_type",
        "birthdate",
        "birthplace_city",
        "birthplace_country_code",
    ):
        schema["urssaf_data"][field].missing = colander.required

    schema["urssaf_data"]["street_number_complement"].validator = colander.OneOf(
        ["", "B", "T", "Q", "C"]
    )
    schema["urssaf_data"]["birthplace_country_code"].widget = forms.get_select(
        [(country["code_insee"], country["name"]) for country in COUNTRIES]
    )
    schema["urssaf_data"]["birthplace_department_code"].widget = forms.get_select(
        [(dept["code_insee"], dept["name"]) for dept in DEPARTMENTS]
    )

    return schema
