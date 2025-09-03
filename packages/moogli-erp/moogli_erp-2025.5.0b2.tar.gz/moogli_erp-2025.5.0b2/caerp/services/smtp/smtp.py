import base64
import os
from typing import Optional, Union
from sqlalchemy import select
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.debug import DebugMailer
from caerp.models.company import Company
from caerp.models.smtp import SmtpSettings
from caerp.services import get_model_by_id


def get_fernet_for_smtp_password(request, salt: str) -> Fernet:
    """
    Build a Fernet object used for symmetrical encryption
    The built fernet object allows to encrypt a password with both a
    salt and a password

    :param salt: The salt string used for the derivation encryption
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=390000,
    )
    password = request.registry.settings.get("caerp.smtp_encryption_password", "secret")
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    fernet = Fernet(key)
    return fernet


def unhash_smtp_password(request, derivation_salt, hashed_smtp_password):
    """extract the original SMTP password from the hashed one"""
    fernet = get_fernet_for_smtp_password(request, derivation_salt)
    decrypted_password = fernet.decrypt(hashed_smtp_password.encode()).decode()
    return decrypted_password


def get_smtp_by_company_id(
    request, company_id: Optional[int] = None
) -> Optional[SmtpSettings]:
    """
    Query SMTP settings for a given company_id

    If no company_id is provided, returns the default (Global) SMTP settings.
    """
    query = select(SmtpSettings).filter(SmtpSettings.company_id == company_id)
    return request.dbsession.execute(query).scalar_one_or_none()


def get_cae_smtp(request):
    """Return the global smtp settings configured through admin"""
    return get_smtp_by_company_id(request, None)


def get_company_smtp_by_company_id(request, company_id) -> Optional[SmtpSettings]:
    """
    Retrieve the smtp settings to use for a given company.

    Fallback on the default smtp settings if the company has enabled
    the use of global smtp
    """
    company_smtp_config = request.dbsession.execute(
        select(Company.smtp_configuration).filter(Company.id == company_id)
    ).scalar()
    if company_smtp_config == "company":
        result = get_smtp_by_company_id(request, company_id)
    elif company_smtp_config == "cae":
        result = get_cae_smtp(request)
    else:
        result = None
    return result


def get_smtp_by_id(request, smtp_settings_id) -> Optional[SmtpSettings]:
    return get_model_by_id(request, SmtpSettings, smtp_settings_id)


def smtp_settings_to_pyramid_mailer_settings(
    request, smtp_settings: SmtpSettings
) -> dict:
    return {
        "host": smtp_settings.smtp_host,
        "port": smtp_settings.smtp_port,
        "username": smtp_settings.smtp_user,
        "password": unhash_smtp_password(
            request, smtp_settings.smtp_password_salt, smtp_settings.smtp_password_hash
        ),
        "ssl": smtp_settings.smtp_ssl,
        "tls": smtp_settings.smtp_tls,
    }


def get_mailer_from_smtp_settings(
    request, smtp_settings: SmtpSettings
) -> Union[Mailer, DebugMailer]:
    """Construit une instance de Mailer à partir d'un SmtpSettings"""
    send_emails = request.registry.settings.get("caerp.smtp_send_emails", None)
    if send_emails is None or send_emails.lower() == "false":
        return DebugMailer(os.path.join(os.getcwd(), "mail"))
    settings = smtp_settings_to_pyramid_mailer_settings(request, smtp_settings)
    return Mailer(**settings)


def smtp_settings_to_json(request, smtp_settings: SmtpSettings) -> dict:
    return {
        "id": smtp_settings.id,
        "smtp_host": smtp_settings.smtp_host,
        "smtp_port": smtp_settings.smtp_port,
        "smtp_user": smtp_settings.smtp_user,
        "smtp_ssl": smtp_settings.smtp_ssl,
        "smtp_tls": smtp_settings.smtp_tls,
        "sender_email": smtp_settings.sender_email,
        "company_id": smtp_settings.company_id,
        "created_at": smtp_settings.created_at,
        "updated_at": smtp_settings.updated_at,
    }
