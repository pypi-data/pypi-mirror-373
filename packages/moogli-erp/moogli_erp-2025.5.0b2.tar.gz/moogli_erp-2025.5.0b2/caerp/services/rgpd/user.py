"""
Utilitaires permettant de requêter les comptes Utilisateurs
"""
import datetime
from typing import List

from sqlalchemy import and_, func, or_, select

from caerp.models.user import Login, User, UserConnections, UserDatas


def get_accounts_not_used_for(request, days_threshold: int) -> List[User]:
    """
    Retrouve les comptes actifs qui n'ont pas été utilisés depuis plus de X jours.
    """
    reference_date = datetime.datetime.now() - datetime.timedelta(days=days_threshold)
    subq = (
        select(
            UserConnections.user_id,
            func.max(UserConnections.month_last_connection).label("maxdate"),
        )
        .group_by(UserConnections.user_id)
        .subquery()
    )
    query = (
        select(User)
        .join(Login)
        .join(subq, User.id == subq.c.user_id)
        .where(Login.active == True)
        .where(User.special == False)
        .where(subq.c.maxdate < reference_date)
    )
    return request.dbsession.execute(query).scalars().all()


def get_userdatas_not_used_for(request, days_threshold: int) -> List[UserDatas]:
    """
    Retrouve les Fiches de gestion sociale qui n'ont pas été utilisées
    depuis plus de X jours.

    Une fiche de gestion sociale est considérée comme utilisée si elle est associée
    à un compte actif ou en fonction de sa date de dernière modification.
    """
    reference_date = datetime.datetime.now() - datetime.timedelta(days=days_threshold)
    subq = (
        select(
            UserConnections.user_id,
            func.max(UserConnections.month_last_connection).label("maxdate"),
        )
        .group_by(UserConnections.user_id)
        .subquery()
    )
    login_related_query = (
        select(Login.user_id)
        .join(subq, Login.user_id == subq.c.user_id)
        .where(subq.c.maxdate < reference_date)
    )
    query = (
        select(UserDatas)
        .where(
            or_(
                and_(
                    UserDatas.user_id.not_in(select(Login.user_id)),
                    UserDatas.created_at <= reference_date,  # type: ignore
                ),
                UserDatas.user_id.in_(login_related_query),
            )
        )
        .where(UserDatas.coordonnees_lastname != "RGPD")
    )

    return request.dbsession.execute(query).scalars().all()
