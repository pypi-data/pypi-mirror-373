class StatusChangedEvent:
    """
    Event fired when a document changes its status
    """

    def __init__(self, request, node, status, comment=None):
        self.request = request
        self.node = node
        self.comment = comment
        self.status = status
        self.node_type = getattr(node, "type_", node.__table__.name)

    def get_settings(self):
        return self.request.registry.settings
