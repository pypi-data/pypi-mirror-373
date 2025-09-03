"""
    render api, usefull functions usable inside templates
"""
import logging
from webhelpers2.html import literal
from caerp.consts.permissions import PERMISSIONS
from caerp.models.node import Node
from caerp.utils.datetimes import format_long_date
from caerp.utils.datetimes import (
    format_long_date as format_long_date_with_name,
    format_long_datetime,
    format_short_date,
    format_datetime,
    format_date,
    format_duration,
)
from caerp.utils.status_rendering import (
    INDICATOR_MAIN_STATUS_CSS,
    INDICATOR_MAIN_STATUS_ICON,
    SALE_DOCTYPE_ICON,
    SIGNED_STATUS_ICON,
    STATUS_ICON,
    SUPPLIER_ORDER_STATUS_ICON,
    ESTIMATION_STATUS_ICON,
    INVOICE_STATUS_ICON,
    EXPENSE_STATUS_ICON,
    STATUS_CSS_CLASS,
    EXPENSE_STATUS_CSS_CLASS,
    JUSTIFIED_STATUS_ICON,
    JUSTIFIED_STATUS_CSS_CLASS,
)
from caerp.utils.strings import (
    format_amount,
    format_float,
    format_indicator_main_status,
    format_indicator_status,
    format_status,
    format_sent_by_email_status,
    format_status_sentence,
    format_activity_status,
    format_expense_status,
    format_supplier_invoice_status,
    format_account,
    format_civilite,
    format_name,
    format_paymentmode,
    format_task_type,
    format_status_string,
    format_estimation_status,
    format_invoice_status,
    format_cancelinvoice_status,
    estimation_get_major_status,
    invoice_get_major_status,
    cancelinvoice_get_major_status,
    major_status,
    pluralize,
    human_readable_filesize,
    month_name,
    short_month_name,
    compile_template_str,
    remove_kms_training_zeros,
    format_quantity,
)
from caerp.utils.iteration import groupby
from caerp.utils.html import clean_html
from caerp.models.task import (
    Estimation,
    Invoice,
    CancelInvoice,
)
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.supply import (
    SupplierOrder,
    SupplierInvoice,
)
from caerp.models.status import StatusLogEntry
from caerp.views.files.routes import FILE_ITEM, FILE_PNG_ITEM
from caerp.views.task.utils import get_task_url
from caerp.utils.modules import route_exists


logger = logging.getLogger(__name__)


def estimation_status_icon(estimation):
    """
    Return the name of the icon matching the status
    """
    if estimation.geninv:
        return ESTIMATION_STATUS_ICON.get("geninv")
    elif estimation.signed_status != "waiting":
        return ESTIMATION_STATUS_ICON.get(estimation.signed_status)
    else:
        return STATUS_ICON.get(estimation.status)


def invoice_status_icon(invoice):
    """
    Return the name of the icon matching the status
    """
    if invoice.status == "valid":
        return INVOICE_STATUS_ICON.get(invoice.paid_status)
    else:
        return STATUS_ICON.get(invoice.status)


def cancelinvoice_status_icon(cinvoice):
    """
    Return the name of the icon matching the status
    """
    return STATUS_ICON.get(cinvoice.status)


def expense_status_icon(expense):
    """
    Return the name of the icon matching the status
    """
    if expense.paid_status != "waiting":
        return EXPENSE_STATUS_ICON.get(expense.paid_status)
    elif expense.justified:
        return EXPENSE_STATUS_ICON.get("justified")
    else:
        return STATUS_ICON.get(expense.status)


def sale_doctype_icon(node):
    return SALE_DOCTYPE_ICON.get(node.type_, "Inconnu")


def expense_status_css_class(expense):
    if expense.paid_status != "waiting":
        return EXPENSE_STATUS_CSS_CLASS.get(expense.paid_status)
    else:
        return STATUS_CSS_CLASS.get(expense.status)


def status_log_entry_icon(status_log_entry):
    codename = status_log_entry.status

    if status_log_entry.pinned:
        # Special case : pinned override icons
        return "thumbtack-active"
    elif status_log_entry.state_manager_key == "signed_status":
        return SIGNED_STATUS_ICON.get(codename)
    elif status_log_entry.state_manager_key == "justified_status":
        return JUSTIFIED_STATUS_ICON.get(codename)
    elif status_log_entry.state_manager_key == "wait_for_payment":
        return "clock"
    else:
        return STATUS_ICON.get(codename)


def supplier_order_status_icon(supplier_order):
    return SUPPLIER_ORDER_STATUS_ICON.get(supplier_order.global_status)


def supplier_invoice_status_icon(supplier_invoice):
    # Similar logic to expense
    if supplier_invoice.paid_status != "waiting":
        return EXPENSE_STATUS_ICON.get(supplier_invoice.paid_status)
    else:
        return STATUS_ICON.get(supplier_invoice.status)


def indicator_status_icon(indicator) -> str:
    """Return an icon representing the indicator status"""
    status = indicator
    if not isinstance(indicator, str):
        status = indicator.main_status
    return INDICATOR_MAIN_STATUS_ICON.get(status, "")


def indicator_status_css(indicator) -> str:
    """Return an icon representing the indicator status"""
    status = indicator
    if not isinstance(indicator, str):
        status = indicator.main_status
    return INDICATOR_MAIN_STATUS_CSS.get(status, "")


def build_icon_str(request, icon_name: str, css_classes: str = "") -> str:
    """
    Crafts the HTML to include the named icon.
    :param icon_name: see https://endi.sophieweb.com/html/icones.html
    """
    return '<svg class="{}"><use href="{}#{}"></use></svg>'.format(
        css_classes,
        request.static_path("caerp:static/icons/icones.svg"),
        icon_name,
    )


def status_icon(element, status=None):
    if isinstance(element, StatusLogEntry):
        return status_log_entry_icon(element)
    elif isinstance(element, Estimation):
        return estimation_status_icon(element)
    elif isinstance(element, Invoice):
        return invoice_status_icon(element)
    elif isinstance(element, CancelInvoice):
        return cancelinvoice_status_icon(element)
    elif isinstance(element, ExpenseSheet):
        return expense_status_icon(element)
    elif isinstance(element, SupplierOrder):
        return supplier_order_status_icon(element)
    elif isinstance(element, SupplierInvoice):
        return supplier_invoice_status_icon(element)


def status_css_class(element):
    """
    Return a status css class for the element

    :param obj element: An instance of a SQLA model
    """
    if isinstance(element, ExpenseSheet):
        return expense_status_css_class(element)
    elif isinstance(element, StatusLogEntry):
        if element.pinned:  # pinned overrides css class
            return "neutral"
        elif element.state_manager_key == "justified_status":
            return JUSTIFIED_STATUS_CSS_CLASS.get(element.status, "")

    return STATUS_CSS_CLASS.get(element.status, "")


def custom_indicator_icon(indicator_name: str) -> str:
    """
    Returns an icon identifier representing the type of the custom indicator
    """
    if indicator_name == "invoiced":
        return "file-invoice-euro"  # invoice level indicator
    elif indicator_name == "bpf_filled":
        return "list-alt"  # business level indicator
    else:
        logger.warning(
            f"Unknown indicator name {indicator_name}, using fallback icon, fix that."
        )
        return "question-circle"


class Api:
    """
    Api object passed to the templates hosting all commands we will use
    """

    format_amount = staticmethod(format_amount)
    format_float = staticmethod(format_float)
    format_date = staticmethod(format_date)
    format_status = staticmethod(format_status)
    format_status_sentence = staticmethod(format_status_sentence)
    format_expense_status = staticmethod(format_expense_status)
    format_supplier_invoice_status = staticmethod(format_supplier_invoice_status)
    format_activity_status = staticmethod(format_activity_status)
    format_account = staticmethod(format_account)
    format_civilite = staticmethod(format_civilite)
    format_name = staticmethod(format_name)
    format_paymentmode = staticmethod(format_paymentmode)
    format_short_date = staticmethod(format_short_date)
    format_long_date = staticmethod(format_long_date)
    format_long_date_with_name = staticmethod(format_long_date_with_name)
    format_long_datetime = staticmethod(format_long_datetime)
    format_quantity = staticmethod(format_quantity)
    format_datetime = staticmethod(format_datetime)
    format_duration = staticmethod(format_duration)
    format_task_type = staticmethod(format_task_type)
    compile_template_str = staticmethod(compile_template_str)

    format_status_string = staticmethod(format_status_string)
    format_estimation_status = staticmethod(format_estimation_status)
    format_invoice_status = staticmethod(format_invoice_status)
    format_cancelinvoice_status = staticmethod(format_cancelinvoice_status)
    format_sent_by_email_status = staticmethod(format_sent_by_email_status)
    estimation_status_icon = staticmethod(estimation_status_icon)
    estimation_get_major_status = staticmethod(estimation_get_major_status)
    invoice_status_icon = staticmethod(invoice_status_icon)
    invoice_get_major_status = staticmethod(invoice_get_major_status)
    cancelinvoice_status_icon = staticmethod(cancelinvoice_status_icon)
    cancelinvoice_get_major_status = staticmethod(cancelinvoice_get_major_status)
    major_status = staticmethod(major_status)
    doctype_icon = staticmethod(sale_doctype_icon)
    format_indicator_status = staticmethod(format_indicator_status)
    format_indicator_main_status = staticmethod(format_indicator_main_status)
    indicator_status_icon = staticmethod(indicator_status_icon)
    indicator_status_css = staticmethod(indicator_status_css)
    pluralize = staticmethod(pluralize)
    status_icon = staticmethod(status_icon)
    status_css_class = staticmethod(status_css_class)

    human_readable_filesize = staticmethod(human_readable_filesize)
    month_name = staticmethod(month_name)
    short_month_name = staticmethod(short_month_name)
    clean_html = staticmethod(clean_html)
    remove_kms_training_zeros = staticmethod(remove_kms_training_zeros)
    custom_indicator_icon = staticmethod(custom_indicator_icon)

    groupby = staticmethod(groupby)

    def __init__(self, context, request):
        self.request = request
        self.context = context

    def has_permission(self, perm_name, context=None):
        context = context or self.context
        # On s'assure ici que la permission existe
        perm = PERMISSIONS[perm_name]
        return self.request.has_permission(perm, context)

    def urlupdate(self, args_dict={}):
        """
        Return the current url with updated GET params
        It allows to keep url params when :
        * sorting
        * searching
        * moving from one page to another

        if current url ends with :
            <url>?foo=1&bar=2
        when passing {'foo':5}, we get :
            <url>?foo=5&bar=2
        """
        get_args = self.request.GET.copy()
        get_args.update(args_dict)
        path = self.request.current_route_path(_query=get_args)
        return path

    def file_url(self, fileobj):
        """
        Return the url to access the given fileobj
        """
        if fileobj is not None and fileobj.id is not None:
            return self.request.route_path(FILE_ITEM, id=fileobj.id)
        else:
            return ""

    def img_url(self, fileobj):
        """
        Return the url to access the given fileobj as an image
        """
        if fileobj is not None and fileobj.id is not None:
            return self.request.route_path(FILE_PNG_ITEM, id=fileobj.id)
        else:
            return ""

    def icon(self, icon_name, css_classes=""):
        """
        Crafts the HTML to include the named icon.
        :param icon_name: see https://endi.sophieweb.com/html/icones.html
        """
        out = build_icon_str(self.request, icon_name, css_classes)
        return literal(out)

    def overridable_label(self, label_key: str, context: Node) -> str:
        """
        Gets a label, possibly overriden by db setting and/or frozen setting
        """
        from caerp.models.services.naming import NamingService

        return NamingService.get_label_for_context(label_key, context)

    def route_exists(self, module_name):
        """
        Check if a route is enabled/exists

        :param str route_name: The route name (first argument of add_route)
        """
        return route_exists(self.request, module_name)

    def task_url(self, *args, **kwargs):
        """
        Build an url to access a task

        :param task: Task instance
        :param dict _query: Query parameters
        :param str suffix: Suffix to add after the id (.pdf or /move ...)
        :param bool api: Do we ask for api url
        """
        return get_task_url(self.request, *args, **kwargs)

    def write_js_app_option(self, option_key: str, option_value: any) -> str:
        """
        Build a js string for setting an AppOption key/value

        Handle different value types so that they be set in the right format in js

        >>> print(api.write_js_app_option("key", "value"))
        AppOption["key"] = "value";

        >>> print(api.write_js_app_option("key", 5))
        AppOption["key"] = 5;

        >>> print(api.write_js_app_option("key", True))
        AppOption["key"] = true;
        """
        left_operand = f"AppOption['{option_key}']"

        if isinstance(option_value, bool):
            if option_value:
                right_operand = "true"
            else:
                right_operand = "false"
        elif isinstance(option_value, (int, float)):
            right_operand = f"{option_value}"
        elif isinstance(option_value, (tuple, list)):
            right_operand = f"{list(option_value)}"
        elif isinstance(option_value, dict):
            right_operand = f"{option_value}"
        elif isinstance(option_value, str):
            right_operand = '"{}"'.format(option_value.replace('"', '\\"'))
        elif option_value == None:
            right_operand = "null"
        else:
            right_operand = f'"{option_value}"'
        return literal(f"{left_operand} = {right_operand};")
