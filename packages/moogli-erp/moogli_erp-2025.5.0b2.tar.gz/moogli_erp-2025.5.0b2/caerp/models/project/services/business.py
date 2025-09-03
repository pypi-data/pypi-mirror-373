import datetime
import logging

from caerp_base.models.base import DBSESSION
from sqlalchemy import distinct, select

from caerp.compute.math_utils import percent
from caerp.exception import MessageException

logger = logging.getLogger(__name__)


class BusinessService:
    """
    Service class provding common Business related tools
    """

    @classmethod
    def invoicing_years(cls, business):
        """
        :returns list: of numbers
        """

        from caerp.models.task.invoice import Invoice

        q = DBSESSION.query(distinct(Invoice.financial_year),).filter(
            Invoice.business == business,
        )
        return [i[0] for i in q]

    @classmethod
    def to_invoice(cls, business, column_name="ht"):
        """
        Compute the amount that is supposed to be invoiced regarding the
        estimation and the existing invoices

        :param obj business: The business instance
        :param: column_name : ht/ttc
        :returns: The amount to be invoiced (in *10^5 format)
        ;rtype: int
        """
        to_invoice = sum(
            [
                getattr(estimation, column_name)
                for estimation in cls._get_estimations_to_invoice(business)
            ]
        )
        invoiced = sum([getattr(invoice, column_name) for invoice in business.invoices])
        return max(to_invoice - invoiced, 0)

    @classmethod
    def _add_payment_deadline(cls, business, payment_line, estimation, order):
        """
        Add a payment deadline for the given payment line to the business
        deadlines
        """
        from caerp.models.project.business import BusinessPaymentDeadline

        if payment_line not in business.payment_lines:
            date = None
            if estimation.paymentDisplay != "ALL_NO_DATE":
                if (
                    payment_line.date
                    and payment_line.date > estimation.date
                    and payment_line.date >= datetime.date.today()
                ):
                    date = payment_line.date
            business.payment_deadlines.append(
                BusinessPaymentDeadline(
                    payment_line=payment_line,
                    order=order,
                    description=payment_line.description,
                    date=date,
                    amount_ttc=payment_line.amount,
                    amount_ht=estimation.compute_ht_from_partial_ttc(
                        payment_line.amount
                    ),
                    estimation=estimation,
                )
            )

    @classmethod
    def _add_deposit_deadline(cls, business, estimation, order):
        """
        Add a deposit deadline to a business
        """
        deposit = estimation.deposit
        if not deposit:
            return business
        from caerp.models.project.business import BusinessPaymentDeadline

        query = BusinessPaymentDeadline.query()
        query = query.filter_by(business_id=business.id)
        query = query.filter_by(estimation_id=estimation.id)
        query = query.filter_by(deposit=True)
        if query.count() == 0:
            business.payment_deadlines.append(
                BusinessPaymentDeadline(
                    business_id=business.id,
                    estimation_id=estimation.id,
                    deposit=True,
                    order=order,
                    amount_ttc=estimation.deposit_amount_ttc(),
                    amount_ht=estimation.deposit_amount_ht(),
                    description=f"Facture d'acompte {estimation.deposit}%",
                )
            )
            DBSESSION().merge(business)
        return business

    @classmethod
    def populate_deadlines(cls, business, estimation=None):
        """
        Populate the business deadlines with those described in the associated
        estimation(s)

        :param obj business: The Business instance
        :param obj estimation: Optionnal Estimation instance
        :returns: The Business instance
        :rtype: obj
        """
        logger.debug("Populating deadlines for the business {}".format(business.id))
        if estimation is not None:
            estimations = [estimation]
        else:
            estimations = business.estimations

        order = max([d.order for d in business.payment_deadlines] + [0])
        for estimation in estimations:
            if estimation.deposit:
                cls._add_deposit_deadline(business, estimation, order)
                order += 1
            for payment_line in estimation.payment_lines:
                cls._add_payment_deadline(business, payment_line, estimation, order)
                order += 1

        # Update the business visible status
        if not business.visible and (
            len(business.payment_deadlines) > 1
            or business.project.project_type.with_business
            or business.business_type.bpf_related
        ):
            business.visible = True
        return DBSESSION().merge(business)

    @classmethod
    def find_deadline(cls, business, deadline_id):
        """
        Find the deadline matching this id

        :param obj business: The parent Business
        :param int deadline_id: The associated deadline_id
        """
        from caerp.models.project.business import BusinessPaymentDeadline

        result = BusinessPaymentDeadline.get(deadline_id)
        if result.business_id != business.id:
            result = None
        return result

    @classmethod
    def find_deadline_from_invoice(cls, business, invoice):
        """
        Find the deadline having this invoice attached to it

        :param obj business: The parent Business
        :param obj invoice: The associated Invoice
        """
        from caerp.models.project.business import BusinessPaymentDeadline

        result = (
            BusinessPaymentDeadline.query()
            .filter_by(invoice_id=invoice.id)
            .filter_by(business_id=business.id)
            .first()
        )
        return result

    @classmethod
    def get_next_deadline(cls, request, business) -> "BusinessPaymentDeadline":
        """
        Find next non invoiced deadline
        """
        from caerp.models.project.business import BusinessPaymentDeadline

        query_deadlines = (
            select(BusinessPaymentDeadline)
            .where(BusinessPaymentDeadline.business_id == business.id)
            .where(BusinessPaymentDeadline.invoiced == False)  # noqa: 711
            .order_by(
                BusinessPaymentDeadline.date.asc(), BusinessPaymentDeadline.order.asc()
            )
        )
        deposit_deadline = request.dbsession.execute(
            query_deadlines.where(BusinessPaymentDeadline.deposit == True)
        ).scalar()

        if deposit_deadline:
            return deposit_deadline
        else:
            next_deadline = request.dbsession.execute(query_deadlines).scalar()
            return next_deadline

    @classmethod
    def is_complex_project_type(cls, business):
        """
        Check if the parent's project type uses businesses

        :param obj business: The current business instance this service is
        attached to
        :rtype: bool
        """
        from caerp.models.project.project import Project
        from caerp.models.project.types import ProjectType

        project_type_id = (
            DBSESSION()
            .query(Project.project_type_id)
            .filter_by(id=business.project_id)
            .scalar()
        )

        ptype_with_business = (
            DBSESSION()
            .query(ProjectType.with_business)
            .filter_by(id=project_type_id)
            .scalar()
        )
        return ptype_with_business

    @classmethod
    def add_estimation(cls, request, business, user):
        """
        Add a new estimation to the current business

        :param obj business: The current business instance this service is
        attached to
        :returns: A new Estimation instance
        """
        customer = cls.get_customer(business)
        from caerp.models.task import Estimation

        data = dict(
            user=user,
            company=business.project.company,
            project=business.project,
            business_id=business.id,
            business_type_id=business.business_type_id,
        )
        estimation = Estimation.create(request, customer, data)

        if business.invoicing_mode == business.PROGRESS_MODE:
            cls.populate_progress_invoicing_status(request, business)
        DBSESSION().merge(estimation)
        DBSESSION().flush()
        return estimation

    @classmethod
    def add_invoice(
        cls, request, business, user, estimation_id=None, no_price_study=False
    ):
        """
        Freely add a new invoice to the current business

        :param obj business: The current business instance this service is
        attached to
        :param obj user: The User requesting the new invoice
        :param no_price_study: No price study should be created
        :returns: A new Invoice instance
        """
        from caerp.models.task import Invoice

        customer = cls.get_customer(business)

        data = dict(
            user=user,
            company=business.project.company,
            project=business.project,
            business_id=business.id,
            business_type_id=business.business_type_id,
            estimation_id=estimation_id,
        )
        invoice = Invoice.create(request, customer, data, no_price_study=no_price_study)

        return invoice

    @classmethod
    def get_customer(cls, business):
        """
        Find the customer associated to this bussiness

        :param obj business: The business instance this service is attached to
        :returns: A Customer id
        :rtype: int
        """
        from caerp.models.task import Task
        from caerp.models.third_party.customer import Customer

        customer_id = (
            DBSESSION()
            .query(Task.customer_id)
            .filter_by(business_id=business.id)
            .distinct()
            .one()
        )
        return Customer.get(customer_id)

    @classmethod
    def is_void(cls, business):
        """
        Check if a business is void

        :rtype: bool
        """
        from caerp.models.task import Task

        query = DBSESSION().query(Task.id).filter_by(business_id=business.id)
        return query.count() == 0

    @classmethod
    def _get_estimations_to_invoice(cls, business):
        """
        Return estimations that should be invoiced

        :param obj business: The business instance
        """
        result = []
        for estimation in business.estimations:
            if estimation.status == "valid" and estimation.signed_status != "aborted":
                result.append(estimation)
        return result

    @classmethod
    def _get_estimation_invoiced_deposit(
        cls, request, business, estimation, current_invoice=None
    ):
        """
        Find the estimation's invoiced amount (or planned to invoice)
        """
        from caerp.services.business import get_deposit_deadlines

        # On récupère les échéances d'acompte pour ce devis
        deposit_deadlines = get_deposit_deadlines(request, business, estimation)
        # Cas 1 l'acompte est facturé, on s'assure de recalculer le pourcentage
        # correspondant
        # (le montant a pu être modifié par l'entrepreneur)
        if (
            current_invoice is not None
            and current_invoice.is_deposit
            and current_invoice.estimation_id == estimation.id
        ):
            deposit = percent(current_invoice.total(), estimation.total())
        # Cas 2: on a supprimé les échéances d'acompte (ou il n'y en a pas)
        elif not deposit_deadlines:
            deposit = 0
        # Cas 3 : on n'a pas encore facturé l'acompte, on prend celui prévu dans le devis
        else:
            deposit = estimation.deposit

        return deposit

    @classmethod
    def populate_progress_invoicing_status(
        cls, request, business, exclude_estimation=None, invoice=None
    ):
        """
        Populate the progress invoicing statuses based on the current business
        estimations
        Can be launched several times
        if estimation is passed, it's excluded from the treatment

        :rtype: bool
        """
        if business.invoicing_mode != business.PROGRESS_MODE:
            raise MessageException(
                "Cette affaire n'utilise pas la facturation à l'avancement"
            )
        from caerp.models.progress_invoicing import (
            ProgressInvoicingChapterStatus,
            ProgressInvoicingProductStatus,
        )

        # On stocke les ids des statuts de l'affaire pour pouvoir supprimer ceux qui ne
        # sont plus d'actualité (en cas de devis sans suite par exemple)
        chapter_status_ids = []

        for estimation in cls._get_estimations_to_invoice(business):
            if estimation == exclude_estimation:
                continue
            price_study = estimation.price_study
            deposit = cls._get_estimation_invoiced_deposit(
                request, business, estimation, invoice
            )
            # The percent of each product to be invoiced (after deposit
            # invoice)
            percent_to_invoice = 100 - deposit

            for group in estimation.line_groups:
                chapter_status = ProgressInvoicingChapterStatus.get_or_create(
                    business,
                    group,
                )
                chapter_status_ids.append(chapter_status.id)

                for task_line in group.lines:
                    if price_study:
                        cls._populate_progress_price_study_status(
                            task_line,
                            chapter_status=chapter_status,
                            percent_to_invoice=percent_to_invoice,
                        )
                    else:
                        ProgressInvoicingProductStatus.get_or_create(
                            task_line,
                            chapter_status=chapter_status,
                            percent_to_invoice=percent_to_invoice,
                        )

        # On nettoye les status qui ne correspondent pas aux devis (quand un
        # devis a été marqué sans suite par exemple)
        cls.clear_progress_invoicing_status(request, business, chapter_status_ids)
        return True

    @classmethod
    def _populate_progress_price_study_status(
        cls, task_line, chapter_status, percent_to_invoice
    ):
        """
        Generates progress invoicing statuses when the source estimation has a
        price study
        """
        from caerp.models.price_study import PriceStudyWork
        from caerp.models.progress_invoicing import (
            ProgressInvoicingProductStatus,
            ProgressInvoicingWorkItemStatus,
            ProgressInvoicingWorkStatus,
        )

        status_ids = []
        # Do the price_study related stuff
        price_study_product = task_line.price_study_product
        if (
            isinstance(price_study_product, PriceStudyWork)
            and price_study_product.display_details
        ):
            work_status = ProgressInvoicingWorkStatus.get_or_create(
                task_line,
                chapter_status=chapter_status,
                percent_to_invoice=percent_to_invoice,
            )
            status_ids.append(work_status.id)
            for work_item in task_line.price_study_product.items:
                wi_status = ProgressInvoicingWorkItemStatus.get_or_create(
                    work_item,
                    work_status=work_status,
                    percent_to_invoice=percent_to_invoice,
                )
                status_ids.append(wi_status.id)
        else:
            status = ProgressInvoicingProductStatus.get_or_create(
                task_line,
                chapter_status=chapter_status,
                percent_to_invoice=percent_to_invoice,
            )
            status_ids.append(status.id)
        return status_ids

    @classmethod
    def clear_progress_invoicing_status(cls, request, business, exclude_status_ids=()):
        """
        Clear the progress invoicing statuses attached to this business

        :rtype: bool
        """
        from caerp.models.progress_invoicing import ProgressInvoicingChapterStatus

        # On nettoie les chapitres (les autres statuts seront supprimés en CASCADE)
        query = ProgressInvoicingChapterStatus.query().filter_by(
            business_id=business.id
        )
        if exclude_status_ids:
            query = query.filter(
                ProgressInvoicingChapterStatus.id.notin_(exclude_status_ids)
            )
        for status in query:
            if not status.invoiced_elements:
                DBSESSION().delete(status)
            else:
                logger.error(
                    "L'instance de {} {} devrait être supprimé "
                    "mais il a déjà donné lieu à facturation".format(
                        ProgressInvoicingChapterStatus, status.id
                    )
                )
                raise MessageException("Ce devis a déjà donné lieu à facturation")
        DBSESSION().flush()

    @classmethod
    def add_progress_invoicing_invoice(cls, request, business, user):
        """
        Build an Invoice in progress invoicing mode

        :param obj business: The current Business
        """
        if not business.estimations:
            raise MessageException(
                "Erreur, cette affaire {} n'a pas de devis rattaché".format(business.id)
            )
        estimation = business.estimations[0]

        # Ref #2740 / #2739 : on ne fait le lien que si on a qu'un seul devis
        # dans l'affaire
        if len(business.estimations) == 1:
            invoice = cls.add_invoice(
                request,
                business,
                user,
                estimation_id=estimation.id,
                no_price_study=True,
            )
        else:
            invoice = cls.add_invoice(request, business, user, no_price_study=True)

        for key in (
            "payment_conditions",
            "description",
            "address",
            "workplace",
            "notes",
            "display_units",
            "start_date",
        ):
            setattr(invoice, key, getattr(estimation, key))
        invoice.mentions = [
            mention for mention in estimation.mentions if mention.active
        ]

        invoice.invoicing_mode = invoice.PROGRESS_MODE
        progress_invoicing_plan = invoice.set_progress_invoicing_plan(request)
        cls.populate_progress_invoicing_plan(business, progress_invoicing_plan, invoice)
        return invoice

    @classmethod
    def add_progress_invoicing_sold_invoice(cls, request, business, user):
        invoice = cls.add_progress_invoicing_invoice(request, business, user)
        plan = invoice.progress_invoicing_plan
        plan.fill(request)
        plan.sync_with_task(invoice)
        return invoice

    @classmethod
    def populate_progress_invoicing_plan(cls, business, progress_invoicing_plan, task):
        """
        Generates the progress invoicing elements (chapters/products...)
        regarding the current business progressing invoice statuses

        :param obj business: The Business instance
        :param obj progress_invoicing_plan: The ProgressInvoicingPlan instance

        :returns: The populated plan
        """
        logger.debug("# Populate the progress invoicing plan ")
        progress_invoicing_plan.chapters = []
        for chapter_status in business.progress_invoicing_chapter_statuses:
            chapter_status.sync_with_plan(progress_invoicing_plan)

        progress_invoicing_plan.sync_with_task(task)

    @classmethod
    def populate_progress_invoicing_cancelinvoice(
        cls, request, business, invoice, cancelinvoice
    ):
        """
        Populate the progress invoicing plan for a cancelinvoice
        """
        inv_plan = invoice.progress_invoicing_plan
        progress_invoicing_plan = inv_plan.gen_cancelinvoice_plan(cancelinvoice)
        DBSESSION().add(progress_invoicing_plan)
        DBSESSION().flush()
        progress_invoicing_plan.sync_with_task(cancelinvoice)

    @classmethod
    def on_task_delete(cls, request, business, task):
        """
        Update the business when an invoice has been deleted

        :param obj business: The Business instance
        :param obj Task: The deleted Task
        """
        if business.is_void():
            DBSESSION().delete(business)
            DBSESSION().flush()

    @classmethod
    def on_estimation_signed_status_change(cls, request, business):
        """
        Manage the modification of an estimation signed status
        """
        if business.invoicing_mode == business.PROGRESS_MODE:
            cls.populate_progress_invoicing_status(request, business)

    @classmethod
    def has_previous_invoice(cls, business, invoice):
        """
        Check if it has a previous valid invoice in the business
        """
        from caerp.models.task import Invoice

        return (
            DBSESSION()
            .query(Invoice.id)
            .filter(
                Invoice.business_id == business.id,
                Invoice.invoicing_mode == Invoice.PROGRESS_MODE,
                Invoice.status == "valid",
                Invoice.id != invoice.id,
                Invoice.date < invoice.date,
            )
            .count()
            > 0
        )

    @classmethod
    def get_current_invoice(cls, business):
        """
        Retrieve an invoice with draft/wait status in the business
        """
        from caerp.models.task import Task

        return (
            DBSESSION()
            .query(Task)
            .filter(
                Task.business_id == business.id,
                Task.status.in_(("draft", "invalid", "wait")),
                Task.type_.in_(("cancelinvoice", "invoice")),
            )
            .first()
        )

    @classmethod
    def progress_invoicing_is_complete(cls, business):
        """
        Check if all the estimated products have been invoiced yet

        :param obj business: The current Business instance
        :rtype: bool
        """
        result = True
        for chapter_status in business.progress_invoicing_chapter_statuses:
            if not chapter_status.is_completely_invoiced():
                result = False
                break
        return result

    @classmethod
    def get_total_income(cls, business, column_name="ht"):
        from caerp.models.task import Task

        # total is HT whatever project type we have
        query = Task.total_income(column_name=column_name)
        return query.filter_by(business_id=business.id).scalar()

    @classmethod
    def get_total_estimated(cls, business, column_name="ht") -> int:
        from caerp.models.task import Estimation

        query = Estimation.total_estimated(column_name=column_name)
        return query.filter_by(business_id=business.id).scalar()
