"""6.2.0 migration des statistiques

Revision ID: 2d0297c64801
Revises: e591a210dd65
Create Date: 2021-05-21 11:47:30.243814

"""

# revision identifiers, used by Alembic.
revision = "2d0297c64801"
down_revision = "e591a210dd65"

from alembic import op
import sqlalchemy as sa
from caerp.alembic.utils import disable_constraints


def migrate_dates(base_helper, conn, session):
    from caerp.models.statistics import StatisticCriterion

    d_helper = sa.Table(
        "date_statistic_criterion",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("search1", sa.Date()),
        sa.Column("search2", sa.Date()),
    )

    j = base_helper.join(d_helper, d_helper.c.id == base_helper.c.id)
    date_entries = sa.select([base_helper, d_helper]).select_from(j)

    for i in conn.execute(date_entries):
        item = StatisticCriterion(
            type="date",
            method=i.method,
            key=i.key,
            date_search1=i.search1,
            date_search2=i.search2,
            entry_id=i.entry_id,
            parent_id=i.parent_id,
        )
        session.add(item)


def migrate_commons(base_helper, conn, session):
    from caerp.models.statistics import StatisticCriterion

    d_helper = sa.Table(
        "common_statistic_criterion",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("search1", sa.String(255)),
        sa.Column("search2", sa.String(255)),
    )

    j = base_helper.join(d_helper, d_helper.c.id == base_helper.c.id)
    entries = sa.select([base_helper, d_helper]).select_from(j)

    for i in conn.execute(entries):
        item = StatisticCriterion(
            type=i.type,
            method=i.method,
            key=i.key,
            search1=i.search1,
            search2=i.search2,
            entry_id=i.entry_id,
            parent_id=i.parent_id,
        )
        session.add(item)


def migrate_static_opts(base_helper, conn, session):
    from caerp.models.statistics import StatisticCriterion

    d_helper = sa.Table(
        "opt_list_statistic_criterion",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("searches", sa.Text),
    )

    j = base_helper.join(d_helper, d_helper.c.id == base_helper.c.id)
    entries = sa.select([base_helper, d_helper]).select_from(j)
    import json

    for i in conn.execute(entries):
        searches = None
        if i.searches is not None:
            searches = json.loads(i.searches)
        item = StatisticCriterion(
            type=i.type,
            method=i.method,
            key=i.key,
            searches=searches,
            entry_id=i.entry_id,
            parent_id=i.parent_id,
        )
        session.add(item)


def migrate_bool(base_helper, conn, session):
    from caerp.models.statistics import StatisticCriterion

    d_helper = sa.Table(
        "bool_statistic_criterion",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
    )

    j = base_helper.join(d_helper, d_helper.c.id == base_helper.c.id)
    entries = sa.select([base_helper, d_helper]).select_from(j)

    for i in conn.execute(entries):
        item = StatisticCriterion(
            type=i.type,
            method=i.method,
            key=i.key,
            entry_id=i.entry_id,
            parent_id=i.parent_id,
        )
        session.add(item)


def migrate_or_and(base_helper, conn, session):
    from caerp.models.statistics import StatisticCriterion

    and_helper = sa.Table(
        "and_statistic_criterion",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
    )

    or_helper = sa.Table(
        "or_statistic_criterion",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
    )

    for d_helper in (or_helper, and_helper):
        j = base_helper.join(d_helper, d_helper.c.id == base_helper.c.id)
        entries = sa.select([base_helper, d_helper]).select_from(j)
        for i in conn.execute(entries):
            if not i.entry_id and not i.parent_id:
                continue
            item = StatisticCriterion(
                type=i.type,
                method=i.method,
                key=i.key,
                entry_id=i.entry_id,
                parent_id=i.parent_id,
            )
            session.add(item)


def migrate_one_to_many(base_helper, conn, session):
    from caerp.models.statistics import StatisticCriterion

    # entry_id -> parent_id -> parent_class -> [criteria]
    criteria_by_entry = {}

    for i in StatisticCriterion.query().filter(StatisticCriterion.key.contains("-")):
        parent_key, child_key = i.key.split("-")
        dict_key = (i.entry_id, i.parent_id, parent_key)
        i.key = child_key
        session.merge(i)
        criteria_by_entry.setdefault(dict_key, []).append(i)
    session.flush()

    for (entry_id, parent_id, parent_key), criteria in criteria_by_entry.items():
        parent = StatisticCriterion(
            key=parent_key, type="onetomany", parent_id=parent_id, entry_id=entry_id
        )
        parent.criteria = criteria
        session.add(parent)
        session.flush()


def add_default_and_clause_on_top(conn, session):
    from caerp.models.statistics import StatisticCriterion, StatisticEntry

    for entry in StatisticEntry.query():
        # On insère une clause et si le plus haut parent de la hiérarchie n'est
        # pas une clause et
        if not (len(entry.criteria) == 1 and entry.criteria[0].type == "and"):
            and_clause = StatisticCriterion(type="and")
            session.add(and_clause)
            session.flush()
            StatisticCriterion.query().filter_by(entry_id=entry.id).update(
                {StatisticCriterion.parent_id: and_clause.id}
            )
            session.flush()

            and_clause.entry_id = entry.id
            session.merge(and_clause)

    StatisticCriterion.query().filter_by(entry_id=None).delete()


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from alembic.context import get_bind
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    conn.execute(
        "update base_statistic_criterion set type='manytoone' " "where type='optrel'"
    )
    conn.execute(
        "delete from base_statistic_criterion where type in ('or', 'and') "
        "and id not in (select distinct(parent_id) from "
        "base_statistic_criterion);"
    )
    base_criterion_helper = sa.Table(
        "base_statistic_criterion",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.String(15)),
        sa.Column("key", sa.String(250)),
        sa.Column("method", sa.String(250)),
        sa.Column("parent_id", sa.Integer),
        sa.Column("entry_id", sa.Integer),
    )
    disable_constraints()
    for meth in (
        migrate_dates,
        migrate_commons,
        migrate_static_opts,
        migrate_bool,
        migrate_or_and,
    ):
        meth(base_criterion_helper, conn, session)
        session.flush()

    migrate_one_to_many(base_criterion_helper, conn, session)
    add_default_and_clause_on_top(conn, session)
    # migrate_dates(base_criterion_helper)
    mark_changed(session)
    session.flush()

    for table in (
        "opt_list_statistic_criterion",
        "common_statistic_criterion",
        "date_statistic_criterion",
        "bool_statistic_criterion",
        "or_statistic_criterion",
        "and_statistic_criterion",
    ):
        op.drop_table(table)


def upgrade():
    migrate_datas()


def downgrade():
    pass
