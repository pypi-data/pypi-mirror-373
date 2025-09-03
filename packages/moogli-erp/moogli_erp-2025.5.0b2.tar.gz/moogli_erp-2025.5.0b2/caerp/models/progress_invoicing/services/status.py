import logging

from caerp_base.models.base import DBSESSION
from caerp.compute import math_utils


logger = logging.getLogger(__name__)


class ChapterStatusService:
    @classmethod
    def get_or_create(cls, status_class, business, source_task_line_group, **kwargs):
        """
        Get or create the status class related to the estimation
        "source_task_line"
        """
        result = (
            status_class.query()
            .filter(
                status_class.business_id == business.id,
                status_class.source_task_line_group_id == source_task_line_group.id,
            )
            .first()
        )

        if result is None:
            result = status_class(
                business=business, source_task_line_group=source_task_line_group
            )
            DBSESSION().add(result)
            DBSESSION().flush()
        return result

    @classmethod
    def sync_with_plan(cls, status, progress_invoicing_plan):
        """
        Sync the current chapter status with the given plan

        Generates the ProgressInvoicingChapter
        """
        from caerp.models.progress_invoicing import ProgressInvoicingChapter

        chapter = (
            ProgressInvoicingChapter.query()
            .filter_by(
                plan_id=progress_invoicing_plan.id,
                status_id=status.id,
            )
            .first()
        )
        if not chapter:
            chapter = ProgressInvoicingChapter(
                plan=progress_invoicing_plan,
                status=status,
                order=status.source_task_line_group.order,
            )
            DBSESSION().add(chapter)
            DBSESSION().flush()

        for product_status in status.product_statuses:
            product_status.sync_with_plan(chapter)
        return chapter

    @classmethod
    def is_completely_invoiced(cls, status):
        result = True
        for product in status.product_statuses:
            if not product.is_completely_invoiced():
                result = False
                break
        return result


class BaseProductStatusService:
    @classmethod
    def get_or_create(
        cls, status_class, source_task_line, chapter_status, percent_to_invoice
    ):
        result = (
            status_class.query()
            .filter(
                status_class.chapter_status_id == chapter_status.id,
                status_class.source_task_line_id == source_task_line.id,
            )
            .first()
        )

        if result is None:
            result = status_class(
                source_task_line=source_task_line,
                chapter_status=chapter_status,
                percent_to_invoice=percent_to_invoice,
            )
            DBSESSION().add(result)
        elif percent_to_invoice != result.percent_to_invoice:
            result.percent_to_invoice = percent_to_invoice
            DBSESSION().merge(result)
        DBSESSION().flush()
        return result

    @classmethod
    def total_deposit(cls, status):
        deposit_percentage = math_utils.round(100 - status.percent_to_invoice, 2)
        return math_utils.percentage(cls._total_ht(status), deposit_percentage)

    @classmethod
    def _total_ht(cls, status):
        """
        Total ht managed by this progress_invoicing status
        """
        result = status.source_task_line.total_ht()
        return result

    @classmethod
    def total_ht_to_invoice(cls, status):
        """
        Return the total ht to invoice

        :param obj status: The ProgressInvoicingLineStatus/
        ProgressInvoicingGroupStatus

        :returns: The total ht to invoice in *10^5 format
        :rtype: int
        """
        return math_utils.percentage(cls._total_ht(status), status.percent_to_invoice)

    @classmethod
    def _total_tva(cls, status):
        """
        Total tva managed by this progress_invoicing status
        """
        return status.source_task_line.tva_amount()

    @classmethod
    def tva_to_invoice(cls, status):
        """
        Compute the tva amount to invoice

        :param obj status: The ProgressInvoicingLineStatus /
        ProgressInvoicingGroupStatus

        :returns: The total tva to invoice in *10^5 format
        :rtype: int
        """
        source_line_tva = cls._total_tva(status)
        return math_utils.percentage(source_line_tva, status.percent_to_invoice)

    @classmethod
    def _total_ttc(cls, status):
        """
        Total ttc managed by this progress_invoicing status
        """
        return status.source_task_line.total()

    @classmethod
    def total_ttc_to_invoice(cls, status):
        """
        Compute the total ttc to invoice

        :param obj status: The ProgressInvoicingLineStatus /
        ProgressInvoicingGroupStatus

        :returns: The total ttc to invoice in *10^5 format
        :rtype: int
        """
        source_line_ttc = cls._total_ttc(status)
        return math_utils.percentage(source_line_ttc, status.percent_to_invoice)

    @classmethod
    def invoiced_percentage(cls, status, product=None) -> int:
        """
        Calcule le pourcentage déjà facturé
        Si un product est passé en paramètre, le calcul s'arrête avant ce product

        Le pourcentage est exprimé au format UI (de 0 à 100 indépendamment de l'acompte)
        """
        result = 0
        for invoiced_product in status.invoiced_elements:
            if product and product == invoiced_product:
                break
            else:
                percentage = invoiced_product.percentage or 0
                result += percentage
        return math_utils.round(result, 2)

    @classmethod
    def invoiced_ht(cls, status, product=None) -> int:
        """
        Calcule le total ht déjà facturé
        Si un product est passé en paramètre, le calcul s'arrête avant ce produit
        """
        result = 0
        for invoiced_product in status.invoiced_elements:
            if product and product == invoiced_product:
                break
            else:
                result += invoiced_product.task_line.total_ht()
        return result

    # TODO : refactor
    @classmethod
    def get_current_percent_left(cls, status):
        """
        Compute the percent left regarding the current status (also when an
        invoice is currently edited)

        :rtype: float or None
        """
        return status.percent_left

    @classmethod
    def total_ht_left(cls, status):
        """
        Compute the total ht regarding the current status (also when an invoice
        is currently edited)

        :rtype: int
        """
        total_ht_to_invoice = cls.total_ht_to_invoice(status)
        invoiced_total_ht = cls.invoiced_ht(status)
        return total_ht_to_invoice - invoiced_total_ht

    @classmethod
    def get_cost(cls, status, ui_percentage, product, percent_left=None):
        """
        Calcule le total ht correspondant au pourcentage fourni

        Cas 1 (on solde le produit)
        Si on atteint les 100%, on déduit le total déjà facturé du total à facturer

        Cas 2 (facturation intermédiaire du produit)
        Sinon on calcule un montant en fonction du pourcentage

        :param obj status: The current ProgressInvoicingLineStatus
        :param float ui_percentage: The percentage to apply
        :param obj product: The product we are asking the cost for

        :param float percent_left: The percentage to invoice before the
        taskline we work on
        """
        if ui_percentage == 0:
            return 0
        # FIXMe
        if percent_left is None:
            percent_left = status.percent_left

        logger.debug(
            "get cost : {} {} {} {}".format(
                status, ui_percentage, percent_left, product
            )
        )
        total_ht = cls.total_ht_to_invoice(status)
        # Facture de solde, on prend directement ce qu'il reste à facturer
        if percent_left - ui_percentage == 0:
            invoiced = cls.invoiced_ht(status, product)
            logger.debug(f"    + Sold invoice : Was already invoiced before {invoiced}")
            result = total_ht - invoiced
        else:
            logger.debug(
                f"   + Retrieve the cost {ui_percentage} % of the total to "
                f"invoice {total_ht}"
            )
            logger.debug("Computing the percentage")
            result = math_utils.percentage(total_ht, ui_percentage)
        logger.debug(f"Cost for the new task line {result}")
        return result

    @classmethod
    def is_completely_invoiced(cls, status):
        return status.invoiced_percentage() == 100


class ProductStatusService(BaseProductStatusService):
    @classmethod
    def sync_with_plan(cls, status, chapter):
        from caerp.models.progress_invoicing import ProgressInvoicingProduct

        result = (
            ProgressInvoicingProduct.query()
            .filter_by(base_status_id=status.id, chapter_id=chapter.id)
            .first()
        )
        if result is None:
            result = ProgressInvoicingProduct(
                status=status,
                chapter=chapter,
                already_invoiced=cls.invoiced_percentage(status),
                order=status.source_task_line.order,
                percentage=0,
            )
            DBSESSION().add(result)
            DBSESSION().flush()
        return result


class WorkStatusService(BaseProductStatusService):
    @classmethod
    def invoiced_percentage(cls, status, product=None) -> int:
        if status.locked:
            return super().invoiced_percentage(status, product)
        else:
            return None

    @classmethod
    def invoiced_ht(cls, status, work=None):
        if status.locked:
            return super().invoiced_ht(status, work)
        else:
            return sum(
                item_status.invoiced_ht() for item_status in status.item_statuses
            )

    @classmethod
    def sync_with_plan(cls, status, chapter):
        from caerp.models.progress_invoicing import ProgressInvoicingWork

        work = (
            ProgressInvoicingWork.query()
            .filter_by(base_status_id=status.id, chapter_id=chapter.id)
            .first()
        )
        if work is None:
            work = ProgressInvoicingWork(
                status=status,
                chapter=chapter,
                order=status.source_task_line.order,
                already_invoiced=cls.invoiced_percentage(status),
                locked=status.locked,
                percentage=0,
            )
            DBSESSION().add(work)
            DBSESSION().flush()
        for item_status in status.item_statuses:
            item_status.sync_with_plan(work)

        return work

    @classmethod
    def is_completely_invoiced(cls, status):
        if status.locked:
            result = super().is_completely_invoiced(status)
        else:
            result = True
            for item in status.item_statuses:
                if not item.is_completely_invoiced():
                    result = False
                    break
        return result

    @classmethod
    def get_cost(cls, status, ui_percentage, work, percent_left=None):
        logger.debug(
            f"WorkService get cost : Status {status.id} Work {work.id} {ui_percentage}  "
            f"{percent_left} Locked ? : {work.locked}"
        )
        if ui_percentage == 0:
            return 0
        if work.locked:
            return super().get_cost(status, ui_percentage, work, percent_left)
        elif cls.is_completely_invoiced(status):
            logger.debug("Is completely invoiced !")
            # Si les WorkItems sont tous à 100%, on veut s'assurer que le total_ht va
            # correspondre au reste à facturer (la somme des totaux HT des avancements
            # des items est potentiellement différentes du total_ht à facturer)
            result = super().get_cost(status, 100, work, 0)
        else:
            logger.debug("Sum the item costs")
            result = sum(
                item.status.get_cost(item.percentage, item, item.get_percent_left())
                for item in work.items
            )
            if result > status.total_ht_to_invoice():
                result = status.total_ht_to_invoice()
        return result


class WorkItemStatusService:
    @classmethod
    def get_or_create(
        cls, status_class, price_study_work_item, work_status, percent_to_invoice
    ):
        result = (
            status_class.query()
            .filter(
                status_class.work_status_id == work_status.id,
                status_class.price_study_work_item_id == price_study_work_item.id,
            )
            .first()
        )

        if result is None:
            result = status_class(
                price_study_work_item=price_study_work_item,
                work_status=work_status,
                percent_to_invoice=percent_to_invoice,
            )
            DBSESSION().add(result)

        elif result.percent_to_invoice != percent_to_invoice:
            result.percent_to_invoice = percent_to_invoice
            DBSESSION().merge(result)
        DBSESSION().flush()
        return result

    @classmethod
    def total_deposit(cls, status):
        deposit_percentage = 100 - status.percent_to_invoice
        return math_utils.percentage(cls._total_ht(status), deposit_percentage)

    @classmethod
    def _total_ht(cls, status):
        """
        Total ht managed by this progress_invoicing status
        """
        result = status.price_study_work_item.total_ht
        return result

    @classmethod
    def total_ht_to_invoice(cls, status):
        """
        Return the total ht to invoice

        :param obj status: The ProgressInvoicingWorkItemStatus
        :returns: The total ht to invoice in *10^5 format
        :rtype: int
        """
        return math_utils.percentage(cls._total_ht(status), status.percent_to_invoice)

    @classmethod
    def _total_tva(cls, status):
        """
        Total tva managed by this progress_invoicing status
        """
        return status.price_study_work_item.compute_total_tva()

    @classmethod
    def tva_to_invoice(cls, status):
        """
        Compute the tva amount to invoice

        :param obj status: The ProgressInvoicingLineStatus /
        ProgressInvoicingGroupStatus

        :returns: The total tva to invoice in *10^5 format
        :rtype: int
        """
        price_study_work_item_tva = cls._total_tva(status)
        return math_utils.percentage(
            price_study_work_item_tva, status.percent_to_invoice
        )

    @classmethod
    def _total_ttc(cls, status):
        """
        Total ttc managed by this progress_invoicing status
        """
        return status.price_study_work_item.ttc()

    @classmethod
    def total_ttc_to_invoice(cls, status):
        """
        Compute the total ttc to invoice

        :param obj status: The ProgressInvoicingLineStatus /
        ProgressInvoicingGroupStatus

        :returns: The total ttc to invoice in *10^5 format
        :rtype: int
        """
        price_study_work_item_ttc = cls._total_ttc(status)
        return math_utils.percentage(
            price_study_work_item_ttc, status.percent_to_invoice
        )

    @classmethod
    def invoiced_percentage(cls, status, work_item=None) -> int:
        """
        Calcule le pourcentage déjà facturé
        Si un work_item est passé en paramètre, le calcul s'arrête avant ce work_item

        Le pourcentage est exprimé au format UI (de 0 à 100 indépendamment de l'acompte)
        """
        result = 0
        for invoiced_work_item in status.invoiced_elements:
            # Les éléments sont triés par date de création donc on ne parcourt
            # que les éléments qui précèdent dans le temps
            if work_item and work_item == invoiced_work_item:
                break
            else:

                result += invoiced_work_item.percentage or 0
        return result

    @classmethod
    def invoiced_ht(cls, status, work_item=None) -> int:
        """
        Calcule le total ht déjà facturé
        Si un work_item est passé en paramètre, le calcul s'arrête avant ce produit
        """
        result = 0
        for invoiced in status.invoiced_elements:
            if work_item and work_item == invoiced:
                break
            else:
                result += invoiced.total_ht()
        return result

    @classmethod
    def total_ht_left(cls, status):
        """
        Compute the total ht regarding the current status (also when an invoice
        is currently edited)

        :rtype: int
        """
        total_ht_to_invoice = cls.total_ht_to_invoice(status)
        invoiced_total_ht = cls.invoiced_ht(status)
        return total_ht_to_invoice - invoiced_total_ht

    @classmethod
    def get_cost(cls, status, ui_percentage, work_item, percent_left=None):
        """
        Calcule le total ht correspondant au pourcentage fourni

        Cas 1 (on solde le produit)
        Si on atteint les 100%, on déduit le total déjà facturé du total à facturer

        Cas 2 (facturation intermédiaire du produit)
        Sinon on calcule un montant en fonction du pourcentage

        :param obj status: The current ProgressInvoicingWorkItemStatus
        :param float ui_percentage: The percentage to apply
        :param obj work_item: The wor   k_item we are asking the cost for

        :param float percent_left: The percentage to invoice before the
        taskline we work on
        """
        if ui_percentage == 0:
            return 0
        if percent_left is None:
            percent_left = status.percent_left

        logger.debug(
            f"WorkItem get cost : Status {status.id} Item {work_item.id} "
            f"{ui_percentage} {percent_left}"
        )
        total_ht = cls.total_ht_to_invoice(status)
        # Facture de solde, on prend directement ce qu'il reste à facturer
        if percent_left - ui_percentage == 0:
            invoiced = cls.invoiced_ht(status, work_item)
            logger.debug(f"    + Sold : Was already invoiced before {invoiced}")
            result = total_ht - invoiced
        else:
            logger.debug(
                f"   + Retrieve the cost {ui_percentage} % of the total to "
                f"invoice {total_ht}"
            )
            logger.debug("Computing the percentage")
            result = math_utils.percentage(total_ht, ui_percentage)
        logger.debug(f"Cost for the new task line {result}")
        return result

    @classmethod
    def is_completely_invoiced(cls, status):
        return status.invoiced_percentage() == 100

    @classmethod
    def sync_with_plan(cls, status, work):
        from caerp.models.progress_invoicing import ProgressInvoicingWorkItem

        result = (
            ProgressInvoicingWorkItem.query()
            .filter_by(base_status_id=status.id, work_id=work.id)
            .first()
        )
        if result is None:
            result = ProgressInvoicingWorkItem(
                status=status,
                work=work,
                order=status.price_study_work_item.order,
                _already_invoiced=cls.invoiced_percentage(status),
                _percentage=0,
            )
            DBSESSION().add(result)
            DBSESSION().flush()
        return result
