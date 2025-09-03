from sqlalchemy import (
    desc,
    extract,
    func,
)
from caerp_base.models.base import DBSESSION


class BaseAccountingMeasureGridService:
    @classmethod
    def get_measure_by_type(cls, grid, measure_type_id):
        result = None
        for measure in grid.measures:
            if measure.measure_type_id == measure_type_id:
                result = measure
                break
        return result


class BalanceSheetMeasureGridService(BaseAccountingMeasureGridService):
    @classmethod
    def last(cls, grid_class, company_id):
        print(grid_class)
        query = DBSESSION().query(grid_class).filter_by(company_id=company_id)
        query = query.order_by(desc(grid_class.date))
        return query.first()

    @classmethod
    def get_years(cls, grid_class, company_id=None):
        query = DBSESSION().query(extract("year", grid_class.date).distinct())
        if company_id is not None:
            query = query.filter_by(company_id=company_id)

        result = [a[0] for a in query.all()]
        result.sort()
        return result

    @classmethod
    def get_grid_from_year(cls, grid_class, company_id, year):
        query = (
            DBSESSION()
            .query(grid_class)
            .filter_by(company_id=company_id)
            .filter(extract("year", grid_class.date) == year)
            .order_by(desc(grid_class.date))
        )
        return query.first()


class TreasuryMeasureGridService(BaseAccountingMeasureGridService):
    @classmethod
    def last(cls, grid_class, company_id):
        query = DBSESSION().query(grid_class).filter_by(company_id=company_id)
        query = query.order_by(desc(grid_class.date))
        return query.first()

    @classmethod
    def get_years(cls, grid_class, company_id=None):
        query = DBSESSION().query(extract("year", grid_class.date).distinct())
        if company_id is not None:
            query = query.filter_by(company_id=company_id)

        result = [a[0] for a in query.all()]
        result.sort()
        return result


class IncomeStatementMeasureGridService(BaseAccountingMeasureGridService):
    @classmethod
    def get_years(cls, grid_class, company_id=None):
        query = DBSESSION().query(grid_class.year.distinct())
        if company_id is not None:
            query = query.filter_by(company_id=company_id)

        result = [a[0] for a in query.all()]
        result.sort()
        return result


class BaseAccountingMeasureService:
    @classmethod
    def get_measure_types(cls, measure_class, grid_id, type_class):
        id_query = (
            DBSESSION()
            .query(measure_class.measure_type_id)
            .filter_by(grid_id=grid_id)
            .order_by(measure_class.order)
        )

        ids = [i[0] for i in id_query]
        if ids:
            return (
                type_class.query()
                .filter(type_class.id.in_(ids))
                .order_by(func.field(type_class.id, *ids))
                .all()
            )
        else:
            return []
