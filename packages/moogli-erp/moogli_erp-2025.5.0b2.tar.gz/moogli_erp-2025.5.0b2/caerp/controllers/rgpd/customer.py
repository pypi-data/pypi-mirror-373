import datetime
from caerp.models.third_party.third_party import stop_listening, start_listening
from caerp.utils.datetimes import format_datetime
from caerp.consts.rgpd import RGPD_CUSTOMER_LABEL
from caerp.models.status import StatusLogEntry
from caerp.models.third_party.customer import Customer


RGPD_MEMO_TEMPLATE = """Compte client anonymisé par {user} le {date}."""


def rgpd_clean_customer(request, customer: Customer):
    """
    RGPD clean customer data
    """
    if customer.type != "individual":
        raise Exception("Only individual customers can be cleaned")
    one_to_one_relationships = "urssaf_data"
    for rel in one_to_one_relationships:
        related = getattr(customer, rel, None)
        if related:
            request.dbsession.delete(related)

    one_to_many_relationships = ("statuses",)
    for rel in one_to_many_relationships:
        related = getattr(customer, rel, None)
        if related:
            for rel in related:
                request.dbsession.delete(rel)

    attributes = (
        "lastname",
        "firstname",
        "civilite",
        "email",
        "phone",
        "mobile",
        "fax",
        "address",
        "additional_address",
        "zip_code",
        "city",
        "country",
        "compte_cg",
        "compte_tiers",
        "bank_account_owner",
        "bank_account_bic",
        "bank_account_iban",
    )
    for attr in attributes:
        setattr(customer, attr, "")
    stop_listening()
    customer.label = RGPD_CUSTOMER_LABEL
    customer.archived = True

    username = request.identity.login.login

    customer.statuses.append(
        StatusLogEntry(
            label="[RGPD]",
            comment=RGPD_MEMO_TEMPLATE.format(
                user=username, date=format_datetime(datetime.datetime.now())
            ),
            user_id=request.identity.id,
        )
    )
    request.dbsession.merge(customer)
    request.dbsession.flush()
    start_listening()
    return customer
