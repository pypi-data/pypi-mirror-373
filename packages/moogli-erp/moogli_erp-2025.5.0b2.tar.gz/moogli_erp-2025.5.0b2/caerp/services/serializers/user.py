from caerp.consts.permissions import PERMISSIONS
from caerp.services.sepa import is_valid_bic, is_valid_iban
from caerp.services.serializers.base import BaseSerializer


class UserSerializer(BaseSerializer):
    acl = {"__all__": PERMISSIONS["global.manage_accounting"]}
    exclude_from_children = (
        "node",
        "user",
        "owner",
        "users",
    )

    def get_has_bank_account(self, request, item, field_name):
        return (
            item is not None
            and is_valid_bic(item.bank_account_bic)
            and is_valid_iban(item.bank_account_iban)
        )
