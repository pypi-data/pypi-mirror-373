import logging

from caerp_base.models.base import DBSESSION
from caerp.compute.math_utils import convert_to_int
from .task import (
    InternalProcessService,
    TaskService,
)


logger = logging.getLogger(__name__)


class EstimationService(TaskService):
    @classmethod
    def create(cls, request, customer, data: dict, no_price_study: bool = False):
        estimation = super().create(request, customer, data, no_price_study)
        if "paymentDisplay" not in data:
            estimation.set_default_payment_display()

        estimation.add_default_payment_line()
        if "validity_duration" not in data:
            estimation.set_default_validity_duration()

        if "deposit" not in data:
            default_deposit = estimation.company.default_estimation_deposit
            if default_deposit:
                estimation.deposit = default_deposit
        return estimation

    @classmethod
    def _set_business_data(cls, request, instance):
        business = super()._set_business_data(request, instance)
        if (
            len(instance.payment_lines) > 1
            or instance.deposit
            or instance.project.project_type.with_business
            or business.business_type.bpf_related
        ):
            business.visible = True
        return business

    @classmethod
    def cache_totals(cls, request, task_obj):
        result = super().cache_totals(request, task_obj)
        task_obj.update_payment_lines(request)
        return result

    @classmethod
    def get_customer_task_factory(cls, customer):
        from caerp.models.task import InternalEstimation
        from caerp.models.task import Estimation

        if customer.is_internal():
            factory = InternalEstimation
        else:
            factory = Estimation
        return factory

    @classmethod
    def _duplicate_payment_lines(cls, request, original, created):
        created.payment_lines = []
        for line in original.payment_lines:
            created.payment_lines.append(line.duplicate())
        return created

    @classmethod
    def duplicate(cls, request, original, user, **kw):
        estimation = super(EstimationService, cls).duplicate(
            request, original, user, **kw
        )

        for field in (
            "deposit",
            "manualDeliverables",
            "paymentDisplay",
            "validity_duration",
        ):
            value = getattr(original, field)
            setattr(estimation, field, value)
        cls._duplicate_payment_lines(request, original, estimation)
        cls.post_duplicate(request, original, estimation, user, **kw)
        return estimation

    @classmethod
    def _clean_payment_lines(cls, estimation, session, payment_times):
        """
        Clean payment lines that should be removed
        """
        payment_lines = list(estimation.payment_lines)
        # Ici on utilise une variable intermédiaire pour éviter
        # les interférences entre la boucle et le pop
        iterator = tuple(enumerate(payment_lines[:-1]))
        for index, line in iterator:
            if index >= payment_times - 1:
                estimation.payment_lines.remove(line)
        return estimation.payment_lines

    @classmethod
    def _complete_payment_lines(cls, estimation, session, payment_times):
        """
        Complete the list of the payment lines to match the number of payments
        """
        from caerp.models.task.estimation import PaymentLine

        payment_lines = cls._clean_payment_lines(estimation, session, payment_times)
        num_lines = len(payment_lines)

        if num_lines < payment_times:
            if num_lines == 0:
                estimation.add_default_payment_line()
                payment_lines = estimation.payment_lines
                num_lines = 1
            sold_line = payment_lines[-1]
            # On s'assure de l'ordre des lignes
            for order, line in enumerate(payment_lines[:-1]):
                line.order = order
                session.merge(line)
            # On crée les lignes qui manquent entre le solde et la dernière échéance
            index = 0
            for index in range(num_lines - 1, payment_times - 1):
                line = PaymentLine(
                    description="Paiement {}".format(index + 1),
                    amount=0,
                    order=index,
                )
                estimation.payment_lines.insert(index, line)
            sold_line.order = index + 1
            session.merge(sold_line)
        elif num_lines != payment_times:
            raise Exception("Erreur dans le code")
        return payment_lines

    @classmethod
    def _update_sold(cls, estimation, session, topay):
        """
        Update the last payment line of an estimation
        """
        payments_sum = 0
        for index, line in enumerate(estimation.payment_lines[:-1]):
            line.order = index
            payments_sum += line.amount
            session.merge(line)
        last_line = estimation.payment_lines[-1]
        last_line.amount = topay - payments_sum
        session.merge(last_line)

    @classmethod
    def _update_computed_payment_lines(cls, estimation, session, payment_times, topay):
        """
        Update the computed payment lines
        """
        lines = cls._complete_payment_lines(estimation, session, payment_times)
        sold_amount = topay
        if payment_times > 1:
            part = estimation.paymentline_amount_ttc()

            for line in lines[:-1]:
                line.amount = part
                session.merge(line)
                sold_amount -= part

        sold_line = lines[-1]
        sold_line.amount = sold_amount
        logger.debug("    + The sold amount is {}".format(sold_amount))
        session.merge(sold_line)

        return lines

    @classmethod
    def update_payment_lines(cls, estimation, request, payment_times=None):
        """
        Update the payment lines

        :param obj estimation: Estimation instance

        provided params are used to know what to update, we use the estimation's
        attributes
        """
        logger.debug("Update payment lines")
        if request is None:
            session = DBSESSION()
        else:
            session = request.dbsession
        session.refresh(estimation)
        total = estimation.total()
        logger.debug("   + Total TTC {}".format(total))
        deposit = estimation.deposit_amount_ttc()
        logger.debug("   + Deposit TTC {}".format(deposit))
        topay = total - deposit
        logger.debug("   + Topay after deposit {}".format(topay))

        if estimation.manualDeliverables == 1:
            cls._update_sold(estimation, session, topay)
        else:
            if payment_times is None:
                payment_times = max(len(estimation.payment_lines), 1)
            cls._update_computed_payment_lines(
                estimation, session, payment_times, topay
            )
        session.flush()

    @classmethod
    def on_before_commit(cls, request, task, action: str, changes: dict):
        super().on_before_commit(request, task, action, changes)
        if action == "update":
            if "payment_times" in changes or "deposit" in changes:
                payment_times = changes.get("payment_times", None)
                payment_times = convert_to_int(payment_times, default=None)
                cls.update_payment_lines(task, request, payment_times)
        return task


class InternalEstimationService(EstimationService):
    pass


class InternalEstimationProcessService(InternalProcessService):
    @classmethod
    def _generate_supplier_document(cls, document, request, supplier):
        logger.info("  + Generate a supplier order document for {}".format(document.id))
        from caerp_base.models.base import DBSESSION
        from caerp.models.supply.internalsupplier_order import (
            InternalSupplierOrder,
        )

        order = InternalSupplierOrder.from_estimation(document, supplier)
        order.supplier = supplier
        DBSESSION().add(order)
        file_ = document.pdf_file.duplicate()
        file_.parent_id = order.id
        DBSESSION().merge(file_)
        document.supplier_order = order
        DBSESSION().merge(document)
        DBSESSION().flush()
        logger.info(f"  + Done : {order}")
        return order
