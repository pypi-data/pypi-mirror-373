import datetime
import calendar
import logging
from sqlalchemy import (
    not_,
    and_,
    or_,
    func,
)

from caerp_base.models.base import DBSESSION
from caerp.models.statistics import (
    StatisticCriterion,
)
from caerp.models.statistics import StatisticEntry
from .inspect import get_inspector


logger = logging.getLogger(__name__)


class MissingDatasError(Exception):
    """
    Custom exception raised when some datas is missing for filtering
    """

    def __init__(self, message, *args, **kwargs):
        Exception.__init__(self, message, *args)
        for key, value in list(kwargs.items()):
            setattr(self, key, value)


class SheetQueryFactory:
    """
    Statistics sheet

    Compound of :
        a list of entries

    Rendering:

            A sheet should be rendered as a csv file, the headers :
                ('label', 'count', 'description')
            each row matches an entry

    :param obj model: The model we're building stats on (UserDatas)
    :param obj sheet: The StatisticSheet instance we're mapping
    :param obj inspector: The model's sqlalchemy inspector used to retrieve
    database related informations
    """

    entries = []

    def __init__(self, model, sheet, inspector):
        self.entries = []
        for entry in sheet.entries:
            self.entries.append(
                EntryQueryFactory(
                    model,
                    entry,
                    inspector,
                )
            )

    @property
    def headers(self):
        return (
            {"name": "label", "label": "Libellé"},
            {"name": "description", "label": "Description"},
            {"name": "count", "label": "Nombre"},
        )

    @property
    def rows(self):
        """
        Return the rows of our sheet output
        """
        result = []
        for entry in self.entries:
            result.append(entry.render_row())

        return result


class EntryQueryFactory:
    """
    Statistic entry

    Compound of :
        a label
        a description
        a list of criteria

    :param obj model: The model we're building stats on (UserDatas)
    :param obj entry_model: The StatisticEntry model instance
    :param obj inspector: The model's sqlalchemy inspector used to retrieve
    database related informations

    Return a unique sqlalchemy query object
    If needed, we make independant queries that we group in the main query
    filtering on the resulting ids
    """

    def __init__(self, model, entry_model, inspector):
        self.entry = entry_model

        self.query_object = QueryFactory(model, self.entry.criteria, inspector)

    def query(self):
        """
        :returns: A sqla query matching the selected criteria in the form
        [(model.id, model_instance)...]
        :rtype: A query object
        """
        return self.query_object.query()

    def render_row(self):
        """
        Returns the datas expected for statistics rendering
        """
        return {
            "label": self.entry.title,
            "count": self.query_object.count(),
            "description": self.entry.description or "",
        }


def get_query_helper(model, criterion_model, inspector):
    """
    Return the appropriate helper class used to build filters on a given
    criterion

    :param model: The model we are building stats on (e.g: UserDatas)
    :param criterion_model: The criterion we want to build a helper from
    :param inspector: A SQLAlchemy inspection class

    :returns: A CriterionQueryHelper instance
    """
    if criterion_model.type == "string":
        factory = StrCriterionQueryHelper
    elif criterion_model.type == "number":
        factory = NumericCriterionQueryHelper
    elif criterion_model.type == "manytoone":
        factory = OptRelCriterionQueryHelper
    elif criterion_model.type == "static_opt":
        factory = StaticOptRelCriterionQueryHelper
    elif criterion_model.type in ("date", "multidate"):
        factory = DateCriterionQueryHelper
    elif criterion_model.type == "bool":
        factory = BoolCriterionQueryHelper
    else:
        raise Exception("Unknown Criterion model type : %s" % (criterion_model.type,))
    return factory(model, criterion_model, inspector)


def get_query_factory(model, criterion_model, inspector):
    """
    Return a query factory for the given criterion_model

    :param model: The model we are building stats on (e.g: UserDatas)
    :param criterion_model: The criterion we want to build a helper from
    :param inspector: A SQLAlchemy inspection class

    :returns: A QueryFactory instance
    """
    if criterion_model.type == "or":
        factory = OrQueryFactory

    elif criterion_model.type == "and":
        factory = AndQueryFactory

    elif criterion_model.type == "onetomany":
        factory = OneToManyQueryFactory

    else:
        factory = QueryFactory
    return factory(model, criterion_model, inspector, root=False)


class CriterionQueryHelper:
    """
    Statistic criterion

    Compound of :
        a model we query on
        a field name
        a condition key
        conditions values
        a type
    """

    model = None
    key = None
    search1 = None
    type = "str"
    # 0 can't be a none value since it can be a valid one (0 children)
    none_values = (None, "")

    def __init__(self, model, criterion_model, inspector):
        self.model = model
        self.criterion_model = criterion_model

        self.key = criterion_model.key
        self.method = criterion_model.method

        self.sqla_datas = inspector.get(self.key)
        if self.sqla_datas is None:
            raise KeyError(
                "La clé statistique ({}) {} n'existe plus".format(
                    criterion_model.id,
                    self.key,
                )
            )
        self.column = self.sqla_datas["column"]

    def get_join_class(self):
        """
        Return a related class if this criterion used one
        """
        return self.sqla_datas.get("join_class")

    def gen_filter(self):
        result = None
        if self.key:
            filter_method = getattr(self, "filter_%s" % self.method, None)
            if filter_method is not None:
                result = filter_method(self.column)
        return result

    def gen_having_clause(self):
        """
        Generate a 'having' clause and its associated group_by clause
        """
        result = None
        if self.key:
            having_method = getattr(self, "having_%s" % self.method, None)
            if having_method is not None:
                result = having_method(self.column)
        return result

    def filter_nll(self, attr):
        """null"""
        return attr.in_(self.none_values)

    def filter_nnll(self, attr):
        """not null"""
        return not_(attr.in_(self.none_values))

    def filter_eq(self, attr):
        """equal"""
        if self.search1:
            return attr == self.search1

    def filter_neq(self, attr):
        """not equal"""
        if self.search1:
            return attr != self.search1


class StrCriterionQueryHelper(CriterionQueryHelper):
    """
    Statistic criterion related to strings
    """

    def __init__(self, model, criterion_model, inspector):
        CriterionQueryHelper.__init__(self, model, criterion_model, inspector)
        self.search1 = criterion_model.search1
        self.search2 = criterion_model.search2

    def filter_has(self, attr):
        """contains"""
        if self.search1:
            like_str = "%" + self.search1 + "%"
            return attr.like(like_str)

    def filter_sw(self, attr):
        """startswith"""
        if self.search1:
            like_str = self.search1 + "%"
            return attr.like(like_str)

    def filter_ew(self, attr):
        """endswith"""
        if self.search1:
            like_str = self.search1 + "%"
            return attr.like(like_str)

    def filter_nhas(self, attr):
        """not contains"""
        f = self.filter_has(attr)
        if f is not None:
            return not_(f)


class BoolCriterionQueryHelper(CriterionQueryHelper):
    def filter_true(self, attr):
        return attr == True  # noqa: E712

    def filter_false(self, attr):
        return attr == False  # noqa: E712


class StaticOptRelCriterionQueryHelper(CriterionQueryHelper):
    def __init__(self, model, criterion_model, inspector):
        CriterionQueryHelper.__init__(self, model, criterion_model, inspector)
        self.searches = criterion_model.searches

    def filter_ioo(self, attr):
        """is one of"""
        if self.searches:
            return attr.in_(self.searches)

    def filter_nioo(self, attr):
        """is not one of"""
        if self.searches:
            return or_(
                not_(attr.in_(self.searches)),
                attr == None,  # noqa: E711
            )


class OptRelCriterionQueryHelper(StaticOptRelCriterionQueryHelper):
    """
    Statistic criterion related to related options
    """

    def __init__(self, model, criterion_model, inspector):
        StaticOptRelCriterionQueryHelper.__init__(
            self, model, criterion_model, inspector
        )
        self.column = getattr(model, self.sqla_datas["foreign_key"])


class RelatedCriterionQueryHelper(CriterionQueryHelper):
    pass


class NumericCriterionQueryHelper(CriterionQueryHelper):
    """
    Statistic criterion for filtering numeric datas
    """

    def __init__(self, model, criterion_model, inspector):
        CriterionQueryHelper.__init__(self, model, criterion_model, inspector)
        self.search1 = criterion_model.search1
        self.search2 = criterion_model.search2

    def filter_lte(self, attr):
        if self.search1:
            return attr <= self.search1
        return

    def filter_gte(self, attr):
        if self.search1:
            return attr >= self.search1
        return

    def filter_lt(self, attr):
        if self.search1:
            return attr < self.search1
        return

    def filter_gt(self, attr):
        if self.search1:
            return attr > self.search1
        return

    def bw(self, attr):
        if self.search1 and self.search2:
            return and_(attr > self.search1, attr < self.search2)

    def nbw(self, attr):
        if self.search1 and self.search2:
            return or_(attr <= self.search1, attr >= self.search2)


class DateCriterionQueryHelper(CriterionQueryHelper):
    """
    Statistic criterion related to Dates
    """

    def __init__(self, model, criterion_model, inspector):
        CriterionQueryHelper.__init__(self, model, criterion_model, inspector)
        self.search1 = criterion_model.date_search1
        self.search2 = criterion_model.date_search2

    def filter_dr(self, attr):
        if self.search1 and self.search2:
            return and_(
                attr >= self.search1,
                attr <= self.search2,
            )
        raise MissingDatasError(
            "Il manque des informations pour générer la requête statistique",
            key=self.key,
            method=self.method,
        )

    def filter_ndr(self, attr):
        if self.search1 and self.search2:
            return or_(
                attr <= self.search1,
                attr >= self.search2,
            )
        raise MissingDatasError(
            "Il manque des informations pour générer la requête statistique",
            key=self.key,
            method=self.method,
        )

    def filter_this_year(self, attr):
        """
        This year
        """
        current_year = datetime.date.today().year
        first_day = datetime.date(current_year, 1, 1)
        last_day = datetime.date(current_year, 12, 31)
        return and_(
            attr >= first_day,
            attr <= last_day,
        )

    def filter_previous_year(self, attr):
        """
        Last year
        """
        previous_year = datetime.date.today().year - 1
        first_day = datetime.date(previous_year, 1, 1)
        last_day = datetime.date(previous_year, 12, 31)
        return and_(
            attr >= first_day,
            attr <= last_day,
        )

    def filter_this_month(self, attr):
        """
        This month
        """
        today = datetime.date.today()
        first_day = datetime.date(today.year, today.month, 1)
        num_days = calendar.monthrange(today.year, today.month)[1]
        last_day = datetime.date(today.year, today.month, num_days)
        return and_(attr >= first_day, attr <= last_day)

    def get_first_day_of_previous_month(self, today, nb_months=1):
        """
        Return the first day of this month - nb_months
        Handle year switch

        :param int nb_months: the number of months to go back
        """
        month = today.month - 1 - nb_months
        year = today.year + int(month / 12)
        month = month % 12 + 1
        return datetime.date(year, month, 1)

    def filter_previous_month(self, attr):
        """
        Last month
        """
        today = datetime.date.today()
        first_day = self.get_first_day_of_previous_month(today)
        last_day = datetime.date(today.year, today.month, 1)
        return and_(attr >= first_day, attr < last_day)

    def having_first_dr(self, attr):
        return self.filter_dr(func.min(attr))

    def having_first_this_year(self, attr):
        return self.filter_this_year(func.min(attr))

    def having_first_this_month(self, attr):
        return self.filter_this_month(func.min(attr))

    def having_first_previous_year(self, attr):
        return self.filter_previous_year(func.min(attr))

    def having_first_previous_month(self, attr):
        return self.filter_previous_month(func.min(attr))

    def having_last_dr(self, attr):
        return self.filter_dr(func.max(attr))

    def having_last_this_year(self, attr):
        return self.filter_this_year(func.max(attr))

    def having_last_this_month(self, attr):
        return self.filter_this_month(func.max(attr))

    def having_last_previous_year(self, attr):
        return self.filter_previous_year(func.max(attr))

    def having_last_previous_month(self, attr):
        return self.filter_previous_month(func.max(attr))


class QueryFactory:
    """
    A query factory that produce a sqlalchemy query, can combine multiple query
    factories or/and query helpers

    :attr list criteria: The list of StatisticCriterion handled by this object
    :attr obj model: The Sqlalchemy model we're talking about
    :attr obj inspector: The Statistic SQLA inspector used to collect columns
    ..
    :attr bool root: Is this object at the top level of our entry
    """

    def __init__(self, model, criteria, inspector, root=True, id_key="id"):
        self.model = model
        # Dans le cas des relations one to many, on ira chercher les valeurs
        # des foreignkey (userdatas_id par exemple)
        self.id_column = getattr(self.model, id_key)
        self.inspector = inspector
        self.root = root

        if not hasattr(criteria, "__iter__"):
            criteria = [criteria]
        self.criteria = criteria

        # When building queries we should ensure we limit the joins
        self.already_joined = []

        # Factories renvoie des ids
        self.query_factories = []
        # helpers fournit les outils de filtrage
        self.query_helpers = []
        self._wrap_criteria()

    def _wrap_criteria(self):
        """
        Wrap criteria with adapted wrappers

            What goes in the main_query will be wrapped as Stat
            CriterionQueryHelper

            What should be queried independantly should be wrapped with a Query
            Factory object
        """
        for criterion in self.criteria:
            if criterion.complex:
                self.query_factories.append(
                    get_query_factory(
                        self.model,
                        criterion,
                        self.inspector,
                    )
                )
            else:
                self.query_helpers.append(
                    get_query_helper(self.model, criterion, self.inspector)
                )

    def _get_ids_from_factories(self):
        """
        Return the ids of matching entries retrieved through the
        query_factories
        """
        ids = None
        for factory in self.query_factories:
            if ids is None:
                ids = factory.get_ids()
            else:
                # AND CLAUSE
                ids = ids.intersection(factory.get_ids())
        return ids

    def query(self):
        """
        Return the main query used to find objects

        e.g:

            query = DBSESSION().query(distinct(UserDatas.id), UserDatas)
            query = query.filter(UserDatas.name.startswith('test'))
            query = query.filter(UserDatas.conseiller_id.in_(['1', '2']))
            query = query.filter(
                UserDatas.id.in_(
                    [list of ids retrieved from independant queries]
                )
            )

        """
        self.already_joined = []
        if self.root:
            main_query = DBSESSION().query(self.id_column.distinct(), self.model)
        else:
            main_query = DBSESSION().query(self.id_column.distinct())

        # Pour chaque critère sur lesquels on va ajouter des filtres, on a
        # besoin d'être sûr que la classe concernée est bien requêtée, il faut
        # donc ajouter des outerjoins pour chaque classe liée.

        # NOTE: on ne gère pas les alias (les joins sur deux tables identiques
        # pour deux relations différentes)
        for criterion in self.query_helpers:
            try:
                # On génère le filtre
                filter_ = criterion.gen_filter()

                # si il y a un filtre ...
                if filter_ is not None:
                    main_query = main_query.filter(filter_)
            except Exception:
                logger.exception("Error while managing criterion {}".format(criterion))

        if self.query_factories:
            ids = self._get_ids_from_factories()
            if ids is not None:
                ids = list(ids)
            else:
                ids = []
            main_query = main_query.filter(self.model.id.in_(ids))

        return main_query

    def get_ids(self):
        """
        Return the ids matched by the current query
        """
        return set([item[0] for item in self.query() if item[0] is not None])

    def count(self):
        """
        Return the number of entries matching this query
        """
        return self.query().count()


class OrQueryFactory(QueryFactory):
    """
    An independant OR query factory
    All children of the or query are requested indepedantly
    Or clause is done Python side
    """

    def _wrap_criteria(self):
        """
        Wrap criteria with adapted wrappers

            What goes in the main_query will be wrapped as Stat
            CriterionQueryHelper

            What should be queried independantly should be wrapped with a Query
            Factory object
        """
        parent_criterion = self.criteria[0]
        for criterion in parent_criterion.children:
            self.query_factories.append(
                get_query_factory(
                    self.model,
                    criterion,
                    self.inspector,
                )
            )

    def get_ids(self):
        """
        Compute the or clause on the independant query factories resulting ids
        list
        """
        ids = None
        for factory in self.query_factories:
            if ids is None:
                ids = factory.get_ids()
            else:
                # OR CLAUSE
                ids = ids.union(factory.get_ids())
        return ids


class AndQueryFactory(OrQueryFactory):
    """
    An independant AND query factory

    All children of the or query are requested indepedantly
    End clause is done Python side
    """

    def get_ids(self):
        """
        Compute the and clause on the independant query factories resulting ids
        list
        """
        ids = None
        for factory in self.query_factories:
            if ids is None:
                ids = factory.get_ids()
            else:
                # AND CLAUSE
                ids = ids.intersection(factory.get_ids())
        return ids


class OneToManyQueryFactory(QueryFactory):
    """
    An independant OneToMany query factory

    Query on a related table and retrieve foreign key values (ids)
    """

    def __init__(self, model, criterion, inspector, root=True):
        self._parameters = inspector.get(criterion.key)
        QueryFactory.__init__(
            self,
            self._parameters["table"],
            criterion.children,
            self._parameters["inspector"],
            root=False,
            id_key=self._parameters["remote_side_id"],
        )


def get_query(model, where):
    """
    Return a query on the given model based on a filter list


    E.g :

        get_query(
            UserDatas,
            [
                {
                    "key":"created_at",
                    "method":"dr",
                    "type":"date",
                    "search1":"1999-01-01",
                    "search2":"2016-12-31"
                }
            ]
        )

    Filter syntax

        key

            The model attribute

        method

            See caerp.statistics.__init__.py for keywords and their meaning

        type

            One of
                string
                number
                bool

        search1

            The first search entry

        search2

            Regarding the method of this filter, we may need a second parameter



    :param cls model: The model to get items from
    :param list where: List of criteria in dict form
    :returns: A SQLA query
    :rtype: obj
    """
    entry = StatisticEntry(title="script related entry", description="")

    for criterion_dict in where:
        entry.criteria.append(StatisticCriterion(**criterion_dict))

    inspector = get_inspector(model)
    query_factory = EntryQueryFactory(model, entry, inspector)
    return query_factory.query()
