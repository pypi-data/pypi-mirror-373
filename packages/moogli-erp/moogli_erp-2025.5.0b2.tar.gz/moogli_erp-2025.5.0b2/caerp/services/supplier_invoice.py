import datetime

from beaker.cache import cache_region
from sqlalchemy import extract, select

from caerp.models.supply import SupplierInvoice


def get_supplier_invoices_years(kw):
    """
    Return a cached query for the years we have invoices configured

    :param kw: kw['request'] is the current request object
    """

    @cache_region("long_term", "supplier_invoices_years")
    def years():
        """
        return the distinct financial years available in the database
        """
        request = kw["request"]
        query = select(extract("year", SupplierInvoice.date).distinct())
        query = query.order_by(SupplierInvoice.date)
        values = request.dbsession.execute(query).scalars().all()
        years = [value for value in values if value is not None]
        current = datetime.date.today().year
        if current not in years:
            years.append(current)
        return years

    return years()
