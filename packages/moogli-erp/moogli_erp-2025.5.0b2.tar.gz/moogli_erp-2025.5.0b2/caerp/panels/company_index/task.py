import logging

from paginate_sqlalchemy import SqlalchemyOrmPage
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from caerp.models.task import (
    Task,
)
from caerp.models.project import Project

from caerp import resources
from caerp.panels.company_index import utils
from caerp.views.task.utils import task_pdf_link

_p1 = aliased(Project)
_p2 = aliased(Project)
_p3 = aliased(Project)

log = logging.getLogger(__name__)


class RecentTaskPanel:
    """
    Panel returning the company's tasklist
    Parameters to be supplied as a cookie or in request.POST

    pseudo params: tasks_per_page, see _get_tasks_per_page()
    tasks_page_nb: -only in POST- the page we display
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def query(self):
        """
        Build sqlalchemy query to all tasks of a company, in reverse
        status_date order.
        """
        return self.context.get_tasks().order_by(desc(Task.status_date))

    def _stream_actions(self, task):
        yield task_pdf_link(self.request, "ce document", task)

    def __call__(self):
        if not self.request.is_xhr:
            # javascript engine for the panel
            resources.task_list_js.need()

        query = self.query()
        page_nb = utils.get_page_number(self.request, "tasks_page_nb")
        items_per_page = utils.get_items_per_page(self.request, "tasks_per_page")

        paginated_tasks = SqlalchemyOrmPage(
            query,
            page_nb,
            items_per_page=items_per_page,
            url_maker=utils.make_get_list_url("tasklist"),
        )

        return {"tasks": paginated_tasks, "stream_actions": self._stream_actions}


def includeme(config):
    """
    Add all panels to our main config object
    """
    config.add_panel(
        RecentTaskPanel,
        "company_recent_tasks",
        renderer="panels/company_index/recent_tasks.mako",
    )
