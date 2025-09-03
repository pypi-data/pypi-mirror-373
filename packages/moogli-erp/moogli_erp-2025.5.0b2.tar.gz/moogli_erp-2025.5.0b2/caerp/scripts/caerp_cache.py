import argparse
import logging
import datetime

from caerp.scripts.utils import (
    argparse_command,
)
from caerp.models.task import (
    Task,
)
from caerp_base.models.base import DBSESSION as db


def refresh_task_amount_command(arguments, env):
    """
    Refresh the task amount cache

    Refresh only the tasks after a given date.
    """
    logger = logging.getLogger(__name__)
    logger.debug("Refreshing cached Task amounts")
    session = db()
    index = 0

    if arguments.date is None:
        date = datetime.date(datetime.date.today().year, 1, 1)
    else:
        date = datetime.datetime.strptime(arguments.date, "%Y-%m-%d").date()

    logger.debug("Refreshing tasks dated after {}".format(date))

    query = Task.query()
    query = query.filter(Task.date >= date)
    logger.debug("Refreshing data for {} tasks".format(query.count()))
    for task in query:
        try:
            task.cache_totals()
            index += 1
            if index % 200 == 0:
                logger.debug("flushing")
                session.flush()
        except Exception:
            logger.exception("Error while caching total : {0}".format(task.id))


def refresh_task_pdf_command(arguments, env):
    """
    Refresh task's pdf cached files
    """
    from caerp.models.company import Company
    from caerp.models.files import File

    logger = logging.getLogger(__name__)

    session = db()
    if arguments.all:
        companies = [c[0] for c in session.query(Company.id)]
    else:
        companies = [int(id_) for id_ in arguments.companies.split(",")]

    if not companies:
        raise Exception("Missing mandatory --companies argument (or --all)")

    logger.debug("Cleaning cache for {}".format(companies))
    from caerp.models.task import Task

    pdf_ids = []
    tasks = (
        Task.query()
        .filter(Task.status == "valid")
        .filter(Task.company_id.in_(companies))
        .filter(Task.pdf_file_id != None)
        .all()
    )

    for task in tasks:
        pdf_ids.append(task.pdf_file_id)
        task.pdf_file = None
        session.merge(task)

    session.flush()

    for file_ in pdf_ids:
        session.delete(File.get(file_))


def purge_pdf_files_command(arguments, env):
    """
    Purge cached pdf files older than a given number of days
    """
    from caerp.models.files import File
    from caerp.models.task import Task

    logger = logging.getLogger(__name__)

    dbsession = db()

    import datetime

    from_day = datetime.date.today() - datetime.timedelta(days=arguments.day)

    query = Task.query().join(Task.pdf_file).filter(File.created_at >= from_day)

    if arguments.silent:
        logger.info("{} tasks' pdf will be cleared".format(query.count()))
    else:
        for task in query:
            dbsession.delete(task.pdf_file)


def sync_sale_product_amount_command(arguments, env):
    """
    Refresh sale catalog amounts
    """
    logger = logging.getLogger(__name__)
    logger.debug("Refreshing sale catalog amounts")

    if arguments.product_type in ("base_sale_product", "all"):
        logger.debug("> Syncing BaseSaleProduct amounts...")
        from caerp.models.sale_product.base import BaseSaleProduct

        for p in BaseSaleProduct.query():
            p.sync_amounts()

    if arguments.product_type in ("work_item", "all"):
        logger.debug("> Syncing WorkItem amounts...")
        from caerp.models.sale_product import WorkItem

        for wi in WorkItem.query():
            wi.sync_amounts()

    logger.debug("Sale catalog amounts refreshed !")


def sync_progress_task_amounts_command(arguments, env):
    """
    Sync amounts on progress invoicing tasks (all or given)

    Possibly restricting to a certain task by id.
    """
    import transaction
    from caerp.models.task import Task

    logger = logging.getLogger(__name__)

    cache = {}
    if arguments.id is None:
        tasks = Task.query().filter(Task.progress_invoicing_plan != None)
    else:
        tasks = [Task.get(arguments.id)]
        if tasks[0] is None or tasks[0].progress_invoicing_plan is None:
            raise Exception(
                f"Task {arguments.id} doesn't exist or is not in progress invoicing mode"
            )

    logger.debug("Synchronisation des montants d'avancement...")
    for t in tasks:
        logger.debug(f" > Synchronisation de {t.official_number} ({t.id})")
        cache[t.id] = [t.ht, t.tva, t.ttc]
        t.progress_invoicing_plan.sync_with_task()
    logger.debug("Fin de la synchronisation")

    transaction.commit()
    transaction.begin()

    logger.debug("Vérification des documents modifiés...")
    if arguments.id is None:
        tasks = Task.query().filter(Task.progress_invoicing_plan != None)
    else:
        tasks = [Task.get(arguments.id)]
    for t in tasks:
        ht, tva, ttc = cache.get(t.id)
        if t.ht != ht:
            logger.debug(
                f" > {t.official_number} ({t.id}) : Le HT a changé \
après la synchronisation {ht} => {t.ht}"
            )
    logger.debug("Fin de la vérification")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="enDi cache utilities")
    parser.add_argument("config_uri")

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    refresh_task_amount_parser = subparsers.add_parser(
        "refresh_task_amount", description=refresh_task_amount_command.__doc__.strip()
    )
    refresh_task_amount_parser.add_argument(
        "--date", help="Defaults to first day of this year"
    )
    refresh_task_amount_parser.set_defaults(func=refresh_task_amount_command)

    refresh_task_pdf_parser = subparsers.add_parser(
        "refresh_task_pdf", description=refresh_task_pdf_command.__doc__.strip()
    )
    group = refresh_task_pdf_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--companies")
    group.add_argument("--all", action="store_true", default=False)
    refresh_task_pdf_parser.set_defaults(func=refresh_task_pdf_command)

    purge_pdf_parser = subparsers.add_parser(
        "purge_pdf", description=purge_pdf_files_command.__doc__.strip()
    )
    purge_pdf_parser.add_argument("--days", type=int, required=True)
    purge_pdf_parser.add_argument("--silent", action="store_true", default=False)
    purge_pdf_parser.set_defaults(func=purge_pdf_files_command)

    sync_sale_product_amount_parser = subparsers.add_parser(
        "sync_sale_product_amount",
        description=sync_sale_product_amount_command.__doc__.strip(),
    )
    sync_sale_product_amount_parser.add_argument(
        "--type",
        required=True,
        choices=["base_sale_product", "work_item", "all"],
    )
    sync_sale_product_amount_parser.set_defaults(func=sync_sale_product_amount_command)

    sync_progress_task_amounts_parser = subparsers.add_parser(
        "sync_progress_task_amounts",
        description=sync_sale_product_amount_command.__doc__.strip(),
    )
    sync_progress_task_amounts_parser.add_argument("--id", help="task id")
    sync_progress_task_amounts_parser.set_defaults(
        func=sync_progress_task_amounts_command
    )
    return parser


def cache_entry_point():
    def callback(arguments, env):
        return arguments.func(arguments, env)

    try:
        return argparse_command(callback, get_parser())
    finally:
        pass
