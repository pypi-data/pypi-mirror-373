from caerp.models.services.user import UserPrefsService


class NavigationHandler:
    """
    Class used to manage the navigation history of a user

    request

        Current pyramid request

    keyword

        The history keyword e.g: project

    Usage 1 : remember the current page

        >>> nav_handler = NavigationHandler(request, "project")
        >>> nav_handler.remember()

    Usage 2 : retrieve the last visited page

        >>> nav_handler = NavigationHandler(request, "project")
        >>> nav_handler.last()

    """

    def __init__(self, request, keyword):
        self.keyword = keyword
        self.request = request

        key_datas = UserPrefsService.get(request, self.keyword) or {}
        self.history = key_datas.get("history")

    def last(self):
        return self.history

    def remember(self):
        path = self.request.current_route_path()
        if path != self.history:
            self.history = path
            self._save()

    def _save(self):
        key_datas = UserPrefsService.get(self.request, self.keyword) or {}
        key_datas["history"] = self.history
        UserPrefsService.set(self.request, self.keyword, key_datas)
