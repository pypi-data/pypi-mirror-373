"""
Third party handling forms schemas and related widgets
"""
import deform
import colander
from collections import OrderedDict
from pyramid_deform import CSRFSchema
from caerp import forms
from caerp.consts.permissions import PERMISSIONS
from caerp_base.consts import CIVILITE_OPTIONS
from caerp.models.third_party import ThirdParty
from caerp.models.company import Company
import pyvat


def _build_third_party_select_value(third_party):
    """
    return the tuple for building third_party select
    """
    label = third_party.label
    if third_party.code:
        label += " ({0})".format(third_party.code)
    return (third_party.id, label)


def build_third_party_values(third_parties):
    """
        Build human understandable third_party labels
        allowing efficient discrimination

    :param obj third_parties: Iterable (list or Sqlalchemy query)
    :returns: A list of 2-uples
    """
    return [
        _build_third_party_select_value(third_party) for third_party in third_parties
    ]


def build_admin_third_party_options(query):
    """
    Format options for admin third_party select widget

    :param obj query: The Sqlalchemy query
    :returns: A list of deform.widget.OptGroup
    """
    query = query.order_by(Company.name)
    values = []
    datas = OrderedDict()

    for item in query:
        datas.setdefault(item.company.name, []).append(
            _build_third_party_select_value(item)
        )

    # All third_parties, grouped by Company
    for company_name, third_parties in list(datas.items()):
        values.append(deform.widget.OptGroup(company_name, *third_parties))
    return values


def third_party_after_bind(node, kw):
    """
    After bind method for the third_party model schema

    removes nodes if the user have no rights to edit them

    :param obj node: SchemaNode corresponding to the ThirdParty
    :param dict kw: The bind parameters
    """
    request = kw["request"]
    if not request.has_permission(
        PERMISSIONS["global.manage_accounting"], request.context
    ):
        if "compte_tiers" in node:
            del node["compte_tiers"]
        if "compte_cg" in node:
            del node["compte_cg"]

        if "bank_account_bic" in node:
            del node["bank_account_bic"]
        if "bank_account_iban" in node:
            del node["bank_account_iban"]

        if "bank_account_owner" in node:
            del node["bank_account_owner"]


@colander.deferred
def deferred_default_type(node, kw):
    """
    Set the default third_party type based on the current (if in edition mode)
    """
    if isinstance(kw["request"].context, ThirdParty):
        return kw["request"].context.type
    else:
        return colander.null


def tva_intracomm_validator(node, values):
    """
    validator for VAT number. Raise a colander.Invalid exception when
    the value is not a valid vat number.
    """
    if not pyvat.is_vat_number_format_valid(values):
        raise colander.Invalid(node, "TVA intracommunautaire invalide")


def customize_third_party_schema(schema):
    """
    Add common widgets configuration for the third parties forms schema

    :param obj schema: The ThirdParty form schema
    """
    if "civilite" in schema:
        schema["civilite"].widget = forms.get_select(
            CIVILITE_OPTIONS,
        )
        schema["civilite"].validator = colander.OneOf([a[0] for a in CIVILITE_OPTIONS])
    if "additional_address" in schema:
        schema["additional_address"].widget = deform.widget.TextAreaWidget(
            cols=25,
            row=1,
        )
    if "city_code" in schema:
        schema["city_code"].widget = deform.widget.HiddenWidget()
    if "country_code" in schema:
        schema["country_code"].widget = deform.widget.HiddenWidget()

    if "email" in schema:
        schema["email"].validator = forms.mail_validator()
    if "compte_cg" in schema:
        schema[
            "compte_cg"
        ].description = "Laisser vide pour utiliser les paramètres de l'enseigne"
        schema[
            "compte_tiers"
        ].description = "Laisser vide pour utiliser les paramètres de l'enseigne"

    if "tva_intracomm" in schema:
        schema["tva_intracomm"].validator = tva_intracomm_validator

    schema.children.append(CSRFSchema()["csrf_token"])

    if "type" in schema:
        schema["type"].validator = colander.OneOf(["individual", "company", "internal"])
        schema["type"].default = deferred_default_type

    if "bank_account_bic" in schema:
        schema["bank_account_bic"].validator = forms.bic_validator
    if "bank_account_iban" in schema:
        schema["bank_account_iban"].validator = forms.iban_validator
    return schema
