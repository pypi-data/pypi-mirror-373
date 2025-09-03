import logging
import io

from py3o.template import Template

from caerp.models.project.file_types import BusinessTypeFileTypeTemplate
from caerp.models.files import FileType
from caerp.models.task import Task
from caerp.utils.datetimes import format_date
from caerp.utils.strings import format_amount

logger = logging.getLogger(__name__)


class BusinessPy3oController:
    """
    Controller class for the business file generation
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _format_task_template_amount(self, task, amount_type):
        if amount_type == "ht":
            amount = task.total_ht()
        elif amount_type == "tva":
            amount = task.tva_amount()
        elif amount_type == "ttc":
            amount = task.total()
        else:
            raise Exception(f"Unknown amount type: {amount_type}")
        return format_amount(
            amount,
            precision=5,
            display_precision=task.decimal_to_display,
            html=False,
            currency=True,
        )

    def _get_company(self):
        return self.context.project.company

    def _get_customer(self):
        return self.context.tasks[0].customer

    def _get_empty_task_template_data(self):
        task_template_data_list = [
            "name",
            "description",
            "workplace",
            "date",
            "start_date",
            "number",
            "total_ht",
            "total_tva",
            "total_ttc",
        ]
        return {key: "" for key in task_template_data_list}

    def _get_estimation_template_data(self, estimation):
        data = self._get_empty_task_template_data()
        data["name"] = estimation.name
        data["description"] = estimation.description
        data["workplace"] = estimation.workplace
        data["date"] = format_date(estimation.date)
        data["start_date"] = format_date(estimation.start_date)
        data["number"] = estimation.internal_number
        data["total_ht"] = self._format_task_template_amount(estimation, "ht")
        data["total_tva"] = self._format_task_template_amount(estimation, "tva")
        data["total_ttc"] = self._format_task_template_amount(estimation, "ttc")
        return data

    def _get_invoice_template_data(self, invoice):
        data = self._get_empty_task_template_data()
        data["name"] = invoice.name
        data["description"] = invoice.description
        data["workplace"] = invoice.workplace
        data["date"] = format_date(invoice.date)
        data["start_date"] = format_date(invoice.start_date)
        data["number"] = invoice.official_number
        data["total_ht"] = self._format_task_template_amount(invoice, "ht")
        data["total_tva"] = self._format_task_template_amount(invoice, "tva")
        data["total_ttc"] = self._format_task_template_amount(invoice, "ttc")
        return data

    def _get_context_tasks_data(self, context_task_id):
        estimation_context_data = self._get_empty_task_template_data()
        invoice_context_data = self._get_empty_task_template_data()
        context_task = Task.get(context_task_id)
        if context_task:
            if "estimation" in context_task.type_:
                estimation_context_data = self._get_estimation_template_data(
                    context_task
                )
            elif "invoice" in context_task.type_:
                if context_task.estimation:
                    estimation_context_data = self._get_estimation_template_data(
                        context_task.estimation
                    )
                invoice_context_data = self._get_invoice_template_data(context_task)
        return estimation_context_data, invoice_context_data

    def _get_template(self, business_type_id, file_type_id):
        return (
            BusinessTypeFileTypeTemplate.query()
            .filter_by(business_type_id=business_type_id)
            .filter_by(file_type_id=file_type_id)
            .first()
        )

    def _get_company_header_data(self):
        company = self._get_company()
        if company.header_file:
            return company.header_file.getvalue()
        else:
            return ""

    def _get_company_logo_data(self):
        company = self._get_company()
        if company.logo_file:
            return company.logo_file.getvalue()
        else:
            return ""

    def get_template_data(self, context_task_id=None):
        company = self._get_company()
        company_data = {
            "name": company.name,
            "address": company.address,
            "zip_code": company.zip_code,
            "city": company.city,
            "country": company.country,
            "email": company.email,
            "phone": company.phone,
            "mobile": company.mobile,
        }
        customer = self._get_customer()
        customer_data = {
            "label": customer.label,
            "company_name": customer.company_name,
            "civilite": customer.civilite,
            "lastname": customer.lastname,
            "firstname": customer.firstname,
            "function": customer.function,
            "address": customer.address,
            "zip_code": customer.zip_code,
            "city": customer.city,
            "country": customer.country,
            "email": customer.email,
            "phone": customer.phone,
            "mobile": customer.mobile,
            "fax": customer.fax,
            "registration": customer.registration,
            "tva_intracomm": customer.tva_intracomm,
        }
        estimation_data, invoice_data = self._get_context_tasks_data(context_task_id)
        return dict(
            company=company_data,
            customer=customer_data,
            estimation=estimation_data,
            invoice=invoice_data,
        )

    def compile_template(self, business_type_id, file_type_id, context_task_id):
        template = self._get_template(business_type_id, file_type_id)
        if not template:
            raise KeyError(
                "No template found ( business_type_id:{} ; file_type_id:{} )".format(
                    business_type_id,
                    file_type_id,
                )
            )
        logger.debug(
            " + Templating ({}, {})".format(
                template.file.name,
                template.file_id,
            )
        )
        output_buffer = io.BytesIO()
        odt_builder = Template(template.file.data_obj, output_buffer)
        odt_builder.set_image_data(
            "staticimage.company_header",
            self._get_company_header_data(),
        )
        odt_builder.set_image_data(
            "staticimage.company_logo",
            self._get_company_logo_data(),
        )
        odt_builder.render(self.get_template_data(context_task_id))
        return template, output_buffer

    def get_available_templates(self, business_type_id) -> list:
        available_templates = BusinessTypeFileTypeTemplate.query()
        available_templates = (
            available_templates.filter_by(business_type_id=business_type_id)
            .join(FileType)
            .order_by(FileType.label)
        )
        return available_templates.all()
