"""4.2.0  add project type

Revision ID: 44f964dc36a2
Revises: 1ad4b3e78299
Create Date: 2018-03-29 11:30:16.936487

"""

# revision identifiers, used by Alembic.
revision = "44f964dc36a2"
down_revision = "18591428772b"
import logging
from alembic import op
import sqlalchemy as sa
from caerp.alembic.utils import column_exists

logger = logging.getLogger("alembic.add_project_type")


def update_database_structure():
    op.add_column(
        "project",
        sa.Column(
            "project_type_id",
            sa.Integer,
            sa.ForeignKey("project_type.id"),
        ),
    )
    op.add_column("task_mention", sa.Column("help_text", sa.String(255)))
    op.alter_column(
        "project",
        "type",
        new_column_name="description",
        existing_type=sa.String(150),
        existing_nullable=True,
    )
    op.add_column(
        "task",
        sa.Column("business_type_id", sa.Integer, sa.ForeignKey("business_type.id")),
    )
    op.add_column(
        "task", sa.Column("business_id", sa.Integer, sa.ForeignKey("business.id"))
    )
    op.add_column(
        "task",
        sa.Column(
            "version",
            sa.Integer,
        ),
    )
    op.add_column("task", sa.Column("legacy_number", sa.Boolean(), nullable=False))

    for tbl, column in (
        ("task", "name"),
        ("task", "type_"),
        ("project", "client_id"),
        ("project", "name"),
        ("project", "creationDate"),
        ("project", "updateDate"),
        ("project", "dispatchType"),
    ):
        if column_exists(tbl, column):
            op.drop_column(tbl, column)

    op.execute("alter table task MODIFY `phase_id` int(11) DEFAULT NULL;")
    op.add_column("task", sa.Column("pdf_file_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_task_pdf_file_id"), "task", "file", ["pdf_file_id"], ["id"]
    )
    op.add_column("task", sa.Column("notes", sa.Text(), nullable=True))


def _add_business_to_all_invoices(session):
    """
    Add a Business entry to all invoices
    """
    from caerp.models.task import (
        Estimation,
        Invoice,
    )

    logger.debug("Adding business to estimations")
    eindex = 0
    iindex = 0
    for e in Estimation.query().options(
        sa.orm.load_only("id", "name", "business_type_id", "project_id")
    ):
        eindex += 1
        invoices = (
            Invoice.query()
            .options(sa.orm.load_only("id"))
            .filter_by(estimation_id=e.id)
            .all()
        )
        if invoices:
            business = e.gen_business()
            for deadline in business.payment_deadlines:
                deadline.invoiced = True
                session.merge(deadline)

            for invoice in invoices:
                iindex += 1
                op.execute(
                    "update task set business_id=%s where id=%s"
                    % (business.id, invoice.id)
                )
                op.execute(
                    "update task join cancelinvoice as c on c.id=task.id "
                    "set task.business_id=%s where c.invoice_id=%s"
                    % (business.id, invoice.id)
                )
    logger.debug(" + %s estimations treated" % eindex)
    logger.debug(" + %s invoices treated" % iindex)

    logger.debug("Adding business to direct invoices")
    iindex = 0
    for invoice in (
        Invoice.query()
        .options(sa.orm.load_only("id", "name", "business_type_id", "project_id"))
        .filter_by(estimation_id=None)
    ):
        iindex += 1
        business = invoice.gen_business()

        op.execute(
            "update task join cancelinvoice as c on c.id=task.id "
            "set task.business_id=%s where c.invoice_id=%s" % (business.id, invoice.id)
        )
    logger.debug(" + %s invoices treated" % iindex)

    session.flush()


def _add_mentions_to_default_business_type(session, default_btype_id):
    """
    migrate existing task mentions to relate them to the default business type
    """
    from caerp.models.task.mentions import TaskMention
    from caerp.models.project.mentions import BusinessTypeTaskMention

    ids = session.query(TaskMention.id)
    for (id_,) in ids:
        for doctype in ("invoice", "cancelinvoice", "estimation"):
            relation = BusinessTypeTaskMention(
                task_mention_id=id_,
                business_type_id=default_btype_id,
                doctype=doctype,
                mandatory=False,
            )
            session.add(relation)
    session.flush()


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from caerp.models.populate import populate_project_types

    populate_project_types(session)

    from caerp.models.project.types import (
        ProjectType,
        BusinessType,
    )

    from caerp.models.populate import populate_project_types

    populate_project_types(session)

    default_ptype_id = ProjectType.get_default().id
    default_btype_id = BusinessType.get_default().id

    course_ptype_id = ProjectType.query().filter_by(name="training").first().id
    course_btype_id = BusinessType.query().filter_by(name="training").first().id

    op.execute("update project set project_type_id=%s" % default_ptype_id)

    op.execute("update task set version='4.1'")

    for typ_ in ("estimation", "invoice"):
        query = "update task join {type_} on {type_}.id=task.id set \
business_type_id={btype_id} where {type_}.course={course}"
        op.execute(query.format(type_=typ_, btype_id=default_btype_id, course=0))
        op.execute(query.format(type_=typ_, btype_id=course_btype_id, course=1))

        query2 = "update project set project_type_id={ptype_id} where \
(select count(task.id) from task join {type_} on {type_}.id=task.id \
where {type_}.course=1 and task.project_id=project.id ) > 0;"
        op.execute(
            query2.format(
                type_=typ_,
                ptype_id=course_ptype_id,
            )
        )

    query = "update task join cancelinvoice on cancelinvoice.id=task.id set \
business_type_id={btype_id}".format(
        btype_id=default_btype_id
    )
    op.execute(query)
    query = "update task join cancelinvoice on cancelinvoice.id=task.id join \
task as task2 on cancelinvoice.invoice_id=task2.id set \
task.business_type_id={btype_id} where task2.business_type_id=4".format(
        btype_id=course_btype_id
    )
    op.execute(query)

    _add_business_to_all_invoices(session)
    _add_mentions_to_default_business_type(session, default_btype_id)


def clean_database():
    op.drop_column("estimation", "course")
    op.drop_column("invoice", "course")


def upgrade():
    update_database_structure()
    migrate_datas()
    clean_database()


def downgrade():
    pass
