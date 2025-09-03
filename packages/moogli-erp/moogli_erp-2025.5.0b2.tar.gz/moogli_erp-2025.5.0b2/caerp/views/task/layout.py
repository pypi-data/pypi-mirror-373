import logging
from caerp.consts.permissions import PERMISSIONS
from caerp.models.task.task import Task

from caerp.utils.menu import (
    MenuItem,
    Menu,
)
from caerp.default_layouts import DefaultLayout


logger = logging.getLogger(__name__)


def get_task_menu(general_route, preview_route, files_route):
    menu = Menu(name="taskmenu")
    menu.add(
        MenuItem(
            name="task_general",
            label="Informations",
            route_name=general_route,
            icon="info-circle",
            perm=PERMISSIONS["company.view"],
        )
    )
    menu.add(
        MenuItem(
            name="task_preview",
            label="Prévisualisation",
            route_name=preview_route,
            icon="eye",
            perm=PERMISSIONS["company.view"],
        )
    )
    menu.add(
        MenuItem(
            name="task_files",
            label="Fichiers",
            route_name=files_route,
            icon="paperclip",
            perm=PERMISSIONS["company.view"],
        )
    )
    return menu


class TaskLayout(DefaultLayout):
    """
    Layout for business related pages

    Provide the main page structure for project view
    """

    menu_factory = get_task_menu

    def __init__(self, context, request):
        DefaultLayout.__init__(self, context, request)
        self.current_task_object = None
        if isinstance(context, Task):
            self.current_task_object = context
        elif hasattr(context, "business"):
            self.current_task_object = context.task
        else:
            raise Exception(
                "Can't retrieve the current task used in the "
                "task layout, context is : %s" % context
            )

    @property
    def menu(self):
        TaskMenu = self.menu_factory()
        TaskMenu.set_current(self.current_task_object)
        return TaskMenu

    def stream_main_actions(self):
        return []

    def stream_more_actions(self):
        return []
