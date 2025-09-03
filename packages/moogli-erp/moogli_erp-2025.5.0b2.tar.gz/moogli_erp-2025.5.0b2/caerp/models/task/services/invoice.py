import datetime
import logging

from .task import (
    TaskService,
    InternalProcessService,
)

logger = logging.getLogger(__name__)


class InvoiceService(TaskService):
    @classmethod
    def create(cls, request, customer, data: dict, no_price_study: bool = False):
        invoice = super().create(request, customer, data, no_price_study)
        if "financial_year" not in data:
            invoice.financial_year = datetime.date.today().year
        return invoice

    @classmethod
    def _set_business_data(cls, request, instance):
        result = super()._set_business_data(request, instance)
        result.populate_indicators()
        return result

    @classmethod
    def get_customer_task_factory(cls, customer):
        from caerp.models.task import InternalInvoice
        from caerp.models.task import Invoice

        if customer.is_internal():
            factory = InternalInvoice
        else:
            factory = Invoice
        return factory

    @classmethod
    def duplicate(cls, request, original, user, **kw):
        invoice = super(InvoiceService, cls).duplicate(request, original, user, **kw)
        invoice.financial_year = datetime.date.today().year
        cls.post_duplicate(request, original, invoice, user, **kw)
        return invoice

    @classmethod
    def _populate_classic_cancelinvoice(cls, invoice, cancelinvoice):
        """
        Populate the cancelinvoice lines when we work in classic invoicing mode
        """
        from caerp.models.task import TaskLine
        from caerp.models.tva import Product
        from caerp.compute import math_utils

        order = invoice.get_next_row_index()

        for discount in invoice.discounts:
            discount_line = TaskLine(
                cost=discount.amount,
                tva=discount.tva,
                quantity=1,
                description=discount.description,
                order=order,
                unity="",
                mode=invoice.mode,
            )
            discount_line.product_id = Product.first_by_tva_value(discount.tva)
            order += 1
            cancelinvoice.default_line_group.lines.append(discount_line)

        for index, payment in enumerate(invoice.payments):
            paid_line = TaskLine(
                cost=math_utils.compute_ht_from_ttc(
                    payment.amount,
                    payment.tva.value,
                    False,
                    division_mode=(invoice.mode != "ttc"),
                ),
                tva=payment.tva.value,
                quantity=1,
                description="Paiement {0}".format(index + 1),
                order=order,
                unity="",
            )
            paid_line.product_id = Product.first_by_tva_value(payment.tva.value)
            order += 1
            cancelinvoice.default_line_group.lines.append(paid_line)
        return cancelinvoice

    @classmethod
    def gen_cancelinvoice(cls, request, invoice, user):
        kw = dict(
            user=user,
            company=invoice.company,
            project=invoice.project,
            customer=invoice.customer,
            phase_id=invoice.phase_id,
            address=invoice.address,
            workplace=invoice.workplace,
            description=invoice.description,
            invoice=invoice,
            expenses_ht=-1 * invoice.expenses_ht,
            financial_year=datetime.date.today().year,
            display_units=invoice.display_units,
            display_ttc=invoice.display_ttc,
            business_type_id=invoice.business_type_id,
            business_id=invoice.business_id,
            mode=invoice.mode,
            start_date=invoice.start_date,
            decimal_to_display=invoice.decimal_to_display,
            invoicing_mode=invoice.invoicing_mode,
            mentions=invoice.mentions,
            payment_conditions="Réglé",
        )
        cancelinvoice = CancelInvoiceService._new_instance(
            request, invoice.customer, kw
        )
        cancelinvoice.line_groups = []
        request.dbsession.merge(cancelinvoice)
        request.dbsession.flush()
        if invoice.has_progress_invoicing_plan():
            invoice.business.populate_progress_invoicing_cancelinvoice(
                request, invoice, cancelinvoice
            )

        else:
            for group in invoice.line_groups:
                cancelinvoice.line_groups.append(group.gen_cancelinvoice_group(request))

            if invoice.invoicing_mode == invoice.CLASSIC_MODE:
                cls._populate_classic_cancelinvoice(invoice, cancelinvoice)

        cancelinvoice.cache_totals(request)
        return cancelinvoice


class InternalInvoiceService(InvoiceService):
    pass


class CancelInvoiceService(TaskService):
    @classmethod
    def get_customer_task_factory(cls, customer):
        from caerp.models.task.invoice import CancelInvoice
        from caerp.models.task import InternalCancelInvoice

        if customer.is_internal():
            factory = InternalCancelInvoice
        else:
            factory = CancelInvoice
        return factory

    @classmethod
    def get_price_study(cls, task):
        return None

    @classmethod
    def has_price_study(cls, task):
        return False


class InternalInvoiceProcessService(InternalProcessService):
    @classmethod
    def _generate_supplier_document(cls, document, request, supplier):
        logger.info("  + Generating a supplier_invoice for {}".format(document))
        from caerp_base.models.base import DBSESSION
        from caerp.models.supply.internalsupplier_invoice import (
            InternalSupplierInvoice,
        )

        supplier_invoice = InternalSupplierInvoice.from_invoice(document, supplier)
        supplier_invoice.supplier = supplier
        DBSESSION().add(supplier_invoice)
        file_ = document.pdf_file.duplicate()
        file_.parent_id = supplier_invoice.id
        DBSESSION().merge(file_)
        document.supplier_invoice = supplier_invoice

        if document.estimation and document.estimation.supplier_order:
            order = document.estimation.supplier_order
            order.supplier_invoice = supplier_invoice
            DBSESSION().merge(order)

        DBSESSION().merge(document)
        DBSESSION().flush()

        logger.info(f"  + Done : {supplier_invoice}")
        return supplier_invoice


class InternalCancelInvoiceProcessService(InternalProcessService):
    @classmethod
    def _generate_supplier_document(cls, document, request, supplier):
        logger.info("  + Generating a supplier_invoice for {}".format(document))
        from caerp_base.models.base import DBSESSION
        from caerp.models.supply.internalsupplier_invoice import (
            InternalSupplierInvoice,
        )

        supplier_invoice = InternalSupplierInvoice.from_invoice(document, supplier)
        supplier_invoice.supplier = supplier
        DBSESSION().add(supplier_invoice)
        file_ = document.pdf_file.duplicate()
        file_.parent_id = supplier_invoice.id
        DBSESSION().merge(file_)
        document.supplier_invoice = supplier_invoice

        DBSESSION().merge(document)
        DBSESSION().flush()
        # Quand on valide un avoir, on veut que la facture frns associée soit validée également.
        from caerp.controllers.state_managers import set_validation_status

        set_validation_status(
            request,
            supplier_invoice,
            "valid",
        )
        DBSESSION().merge(supplier_invoice)
        logger.info(f"  + Done : {supplier_invoice}")
        return supplier_invoice
