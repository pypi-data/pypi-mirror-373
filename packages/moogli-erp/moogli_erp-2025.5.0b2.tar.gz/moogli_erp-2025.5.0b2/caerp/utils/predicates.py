import time
from hashlib import md5
import logging


class SettingHasValuePredicate:
    """
    Custom view predicate allowing to declare views only if a setting is set
    """

    def __init__(self, val, config):
        self.name, self.value = val
        if not isinstance(self.value, bool):
            raise ValueError("Only boolean values supported")

    def text(self):
        return "if_setting_has_value = {0} == {1}".format(self.name, self.value)

    phash = text

    def __call__(self, context, request):
        settings = request.registry.settings

        isin = self.name in settings
        return isin == self.value
