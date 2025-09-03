"""
Common utilities used for task edition
"""
import logging

from caerp.forms.tasks.base import get_business_types_from_request
from caerp.models.form_options import FormFieldDefinition
from caerp.models.task import PaymentConditions, TaskInsuranceOption, WorkUnit
from caerp.models.price_study.base import BasePriceStudyProduct
from caerp.utils.widgets import Link

from caerp.views.project.routes import PROJECT_ITEM_ROUTE
from caerp.views.business.routes import BUSINESS_ITEM_ROUTE

logger = logging.getLogger(__name__)


def get_business_types(request):
    return [
        dict(label=i.label, value=i.id, tva_on_margin=i.tva_on_margin)
        for i in get_business_types_from_request(request)
    ]


def get_mentions(request):
    """
    Collect Task mentions regarding the context's business type

    :param obj request: The current request object with a Task context
    :returns: List of TaskMention in their json repr
    """
    context = request.context
    doctype = context.type_
    business_type = context.business_type
    mentions = business_type.optionnal_mentions(doctype)
    return mentions


def get_task_insurance_options(request):
    """
    Collect insurance options
    """
    return TaskInsuranceOption.query().filter_by(active=True).all()


def get_tvas(request):
    """
    Collect tva objects regarding the request context

    :param obj request: The current request object with a Task context
    :returns: List of Tva objects
    """
    return request.context.get_selectable_tvas()


def get_products(request):
    """
    Collect products regarding the context

    :param obj request: The current request object with a Task context
    :returns: List of Product objects
    """
    return request.context.get_selectable_products()


def get_workunits(request):
    """
    Collect available Workunits

    :param obj request: The current request object
    :returns: List of Workunits
    """
    return WorkUnit.query().all()


def get_payment_conditions(request):
    """
    Collect available PaymentConditions

    :param obj request: The current request object
    :returns: List of PaymentConditions
    """
    return PaymentConditions.query().all()


def get_default_tva(request, tva_options):
    """
    Return the default tva to be used in this specific context

    - The last used in the document
    or
    - The default one

    :param obj request: The pyramid request with a Task context
    :param list tva_options: The available options for the end user
    :rtype: str
    """
    return request.context.get_default_tva(tva_options)


def get_default_product_id(request, products, default_tva):
    """
    Try to find a default product_id regarding the current context

    :param obj request: A pyramid request with a Task context
    :param list products: A list of Product instances
    :param obj tva: The default tva

    :rtype: int or None
    """
    return request.context.get_default_product_id(products, default_tva) or ""


def get_task_view_type(task):
    """
    Compute the view/acl label for the given task based on its type_
    """
    type_ = task.type_
    if "internal" in type_:
        type_ = type_[8:]
    return type_


def get_task_url(
    request,
    task=None,
    _query={},
    suffix="",
    api=False,
    _anchor=None,
    absolute=False,
):
    """
    Return the route_name associated to the given Task

    :param request: Pyramid request
    :param task: Task instance
    :param dict _query: Query parameters
    :param bool api: Do we ask for api url
    :param str _anchor: Url anchor to add at the end e.g : #payment
    :param bool absolute: Absolute url ?
    """
    if task is None:
        task = request.context

    type_ = get_task_view_type(task)
    route = "/%ss/{id}" % type_

    if suffix:
        route += suffix

    if api:
        route = "/api/v1%s" % route

    params = dict(id=task.id, _query=_query)
    if _anchor is not None:
        params["_anchor"] = _anchor

    if absolute:
        method = request.route_url
    else:
        method = request.route_path
    return method(route, **params)


def task_pdf_link(request, titleTasktype="ce document", task=None, link_options={}):
    """
    Return the route_name associated to the given Task

    :param request: Pyramid request
    :param task: Task instance
    """
    options = {
        "css": "btn icon only",
        "label": "",
        "title": f"Voir le PDF de {titleTasktype}",
        "icon": "file-pdf",
    }
    options.update(link_options)
    if task is None:
        task = request.context
    type_ = get_task_view_type(task)
    route = "/%ss/{id}.pdf" % type_

    return Link(request.route_path(route, id=task.id), **options)


def get_field_definition(fieldname):
    logger.debug("Collecting def for {}".format(fieldname))
    field_def = FormFieldDefinition.get_definition(fieldname, "task")
    return field_def.form_config()


def collect_price_study_product_types():
    return [
        {"label": value, "value": key}
        for key, value in list(BasePriceStudyProduct.TYPE_LABELS.items())
    ]


def get_task_parent_url(request, task=None, business="____none"):
    """
    Returns a task parent url regarding its business type


    - all task doesn't have a business (estimations without invoices)
    - on deleting a single invoice with no estimation, the business is deleted too,
    during view execution, the task.business could point to a expired object
    """
    if task is None:
        task = request.context

    if business == "____none":
        business = task.business
    else:
        business = None

    if business and business.visible:
        return request.route_path(BUSINESS_ITEM_ROUTE, id=business.id)
    else:
        return request.route_path(PROJECT_ITEM_ROUTE, id=task.project_id)
