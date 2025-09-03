import datetime
import logging
from caerp.controllers.rgpd.inspect import get_inspector
from caerp.models.user import User
from caerp.models.user.userdatas import UserDatas, start_listening, stop_listening
from caerp.utils.datetimes import format_date

logger = logging.getLogger(__name__)
COMPANY_ATTRIBUTES = (
    "email",
    "phone",
    "mobile",
    "address",
    "zip_code",
    "city",
    "country",
    "latitude",
    "longitude",
    "logo_file",
    "header_file",
    "RIB",
    "IBAN",
    "code_compta",
    "general_customer_account",
    "general_expense_account",
    "third_party_customer_account",
    "general_supplier_account",
    "third_party_supplier_account",
    "internalgeneral_customer_account",
    "internalthird_party_customer_account",
    "internalgeneral_supplier_account",
    "internalthird_party_supplier_account",
    "bank_account",
    "follower",
    "antenne",
)


def get_default_userdatas_dict(request):
    now = datetime.datetime.now()
    today = format_date(now.date())
    ts = datetime.datetime.timestamp(now)
    return {
        "coordonnees_lastname": "RGPD",
        "lastname": "RGPD",
        "coordonnees_firstname": f"Anonymisé le {today}",
        "firstname": f"Anonymisé le {today}",
        "coordonnees_email1": f"anonyme_{ts}@example.com",
        "email": f"anonyme_{ts}@example.com",
    }


def rgpd_clean_user(request, user: User):
    """
    RGPD clean user related data
    """
    userdata: UserDatas = user.userdatas

    stop_listening()
    inspector = get_inspector(UserDatas)
    inspector.anonymize(request, userdata)
    start_listening()
    for key, value in get_default_userdatas_dict(request).items():
        logger.debug(f"Setting default value for {key}")
        if hasattr(userdata, key):
            setattr(userdata, key, value)
        elif hasattr(user, key):
            setattr(user, key, value)

    request.dbsession.merge(userdata)
    request.dbsession.merge(user)
    if user.login:
        request.dbsession.delete(user.login)

    for file_ in userdata.files:
        request.dbsession.delete(file_)

    for company in user.companies:
        logger.debug(f"Cleaning company {company.name}")
        if len(company.get_active_employees()) <= 1:
            company.name = "RGPD : enseigne anonymisée"

            for attr in COMPANY_ATTRIBUTES:
                logger.debug(f"Setting None value for {attr}")
                setattr(company, attr, None)
            request.dbsession.merge(company)
