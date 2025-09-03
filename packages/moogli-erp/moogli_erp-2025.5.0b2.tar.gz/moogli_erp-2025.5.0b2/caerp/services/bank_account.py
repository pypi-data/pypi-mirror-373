from typing import List, Optional
from sqlalchemy import select
from caerp.models.payments import BankAccount


def get_active_bank_accounts_for_select(
    request, more_filters: List = []
) -> List[tuple[int, str]]:
    """
    Renvoie une liste [(id, label)] des comptes bancaires actifs

    >>> get_active_bank_accounts_for_select(
        request,
        more_filters=[
            BankAccount.bank_account_iban != None,
            BankAccount.bank_account_bic != None
        ]
    )
    """
    query = (
        select(BankAccount.id, BankAccount.label)
        .where(BankAccount.active == True)
        .order_by(BankAccount.label)
    )
    for filter_ in more_filters:
        query = query.where(filter_)
    return request.dbsession.execute(query).all()


def get_active_bank_accounts_ids(request, more_filters: List = []) -> List[int]:
    """
    Renvoie une liste des ids des comptes bancaires actifs
    """
    query = select(BankAccount.id).where(BankAccount.active == True)

    for filter_ in more_filters:
        query = query.where(filter_)
    return request.dbsession.execute(query).scalars().all()


def get_default_bank_account_id(request, more_filters: List = []) -> Optional[int]:
    """
    Renvoie l'id du compte bancaire par défaut
    """
    query = select(BankAccount.id).where(
        BankAccount.active == True, BankAccount.default == True
    )
    for filter_ in more_filters:
        query = query.where(filter_)
    return request.dbsession.execute(query).scalar()
