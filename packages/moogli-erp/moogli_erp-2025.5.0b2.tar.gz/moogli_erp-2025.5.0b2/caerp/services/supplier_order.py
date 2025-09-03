import datetime
from sqlalchemy import extract
from beaker.cache import cache_region

from caerp.models.supply import SupplierOrder


def get_supplier_orders_years(kw):
    """
        Return a cached query for the years we have invoices configured

    :param kw: kw['request'] is the current request object
    """

    @cache_region("long_term", "supplier_orders_years")
    def years():
        """
        return the distinct financial years available in the database
        """
        request = kw["request"]
        # Ici on ne peut pas utiliser
        # select(extract('year', SupplierInvoice.created_at).distinct())
        # Car il y a un bug dans SQLAlchemy et
        # le select se fait uniquement sur la table à laquelle appartient created_at
        # (Node)
        query = request.dbsession.query(
            extract("year", SupplierOrder.created_at).distinct()
        )
        query = query.order_by(SupplierOrder.created_at)

        years = [value[0] for value in query if value is not None]
        current = datetime.date.today().year
        if current not in years:
            years.append(current)
        return years

    return years()
