"""
Expense sheet serializers used for expense sheet related views
"""

from caerp.compute.math_utils import integer_to_amount
from caerp.consts.permissions import PERMISSIONS
from caerp.services.serializers.base import BaseSerializer
from caerp.utils.strings import month_name


class ExpenseSheetSerializer(BaseSerializer):
    acl = {
        "__all__": PERMISSIONS["global.manage_accounting"],
        "user": PERMISSIONS["global.manage_accounting"],
        "company": PERMISSIONS["global.manage_accounting"],
    }
    exclude_from_children = ("node", "expense_sheet", "expense", "expense_sheets")

    def get_total_label(self, request, item, field_name):
        value = item.total
        return integer_to_amount(value)

    def get_label(self, request, item, field_name):
        if item:
            return month_name(item.month).capitalize() + " " + str(item.year)
