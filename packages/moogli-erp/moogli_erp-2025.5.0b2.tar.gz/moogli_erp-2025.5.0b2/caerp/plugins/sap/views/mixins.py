class SAPTaskRestViewMixin:
    """
    force fields to True
    """

    def post_format(self, entry, edit, attributes):
        ret = super().post_format(entry, edit, attributes)
        entry.display_ttc = True
        entry.display_units = True
        return ret
