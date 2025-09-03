import logging
from sqlalchemy import distinct, not_

from caerp_base.models.base import DBSESSION
from caerp.scripts.utils import (
    command,
)


def clean_business_command(arguments, env):
    """
    Clean business instances (without tasks associated to it)
    """
    logger = logging.getLogger(__name__)
    from caerp.models.project.business import Business
    from caerp.models.task import Task

    task_business_ids = DBSESSION().query(distinct(Task.business_id))
    businesses = Business.query().filter(not_(Business.id.in_(task_business_ids)))

    for business in businesses:
        logger.info("Deleting %s" % business.name)
        DBSESSION().delete(business)


def clean_price_study_and_sale_product_totals(arguments, env):
    """
    Synchronize all the cached totals of all elements of the Sale product
    catalog and the price study
    """
    from caerp.models.sale_product.base import BaseSaleProduct

    for product in BaseSaleProduct.query():
        ht = product.ht
        product.sync_amounts()
        if product.ht != ht:
            product._caerp_service.sync_price_study(product)

    from caerp.models.price_study.price_study import PriceStudy

    for study in PriceStudy.query():
        for product in study.products:
            product.on_before_commit(state="add")

        study.sync_amounts()


def clean_entry_point():
    """
    MoOGLi cleaning tools
    Usage:
        caerp-clean <config_uri> business
        caerp-clean <config_uri> catalog_and_price_cache

    Options:
        -h --help     Show this screen.
    """

    def callback(arguments, env):
        args = ()
        if arguments["business"]:
            func = clean_business_command
        elif arguments["catalog_and_price_cache"]:
            func = clean_price_study_and_sale_product_totals
        return func(arguments, env)

    try:
        return command(callback, clean_entry_point.__doc__)
    finally:
        pass
