"""
Job related pages
"""
import io
import colander
from pyramid.httpexceptions import HTTPNotFound

from caerp.consts.permissions import PERMISSIONS
from caerp.export.utils import write_file_to_request
from caerp_celery.models import (
    Job,
)
from caerp.resources import job_js
from caerp.forms.job import get_list_schema

from caerp.utils.widgets import ViewLink
from caerp.views import BaseListView


def job_view(context, request):
    """
    :param obj context: The job we want to watch
    :param obj request: The pyramid request object
    """
    job_js.need()
    populate_actionmenu(request)

    return dict(
        title=context.label,
        url=request.route_path("job", id=context.id),
    )


def populate_actionmenu(request):
    request.actionmenu.add(ViewLink("Revenir en arrière", js="window.history.back()"))


class JobList(BaseListView):
    title = "Historique des tâches"
    schema = get_list_schema()
    sort_columns = dict(created_at=Job.created_at)
    default_sort = "created_at"
    default_direction = "desc"

    def query(self):
        query = Job.query()
        return query

    def filter_type(self, query, appstruct):
        type_ = appstruct.get("type_")
        if type_ not in (None, colander.null):
            query = query.filter(Job.type_ == type_)
        return query

    def filter_status(self, query, appstruct):
        status = appstruct.get("status")
        if status not in (None, colander.null):
            query = query.filter(Job.status == status)
        return query


def make_stream_csv_by_key(job_key, filename):
    """
    Build a view streaming the key attr of the current context as a csv file

    :param str job_key: an attribute of the associated context
    :param str filename: A filename used to stream the datas
    """

    def stream_csv(context, request):
        """
        Stream resulting csv datas resulting from an import

        :param context: The csv import job instance
        """
        csv_str_datas = getattr(context, job_key, {})
        if csv_str_datas is None or len(csv_str_datas) == 0:
            raise HTTPNotFound()

        f_buf = io.BytesIO()
        f_buf.write(csv_str_datas.encode("utf-8"))
        write_file_to_request(
            request,
            "%s.csv" % filename,
            f_buf,
            "text/csv",
        )
        return request.response

    return stream_csv


def job_json_model_view(context, request):
    """
    Return a job as json datas, check if the job should be cancelled or not
    """
    if context.timeout() and context.status in ("planned", "running"):
        request.dbsession.merge(context)
    return request.context


def includeme(config):
    config.add_route(
        "job",
        "/jobs/{id:\d+}",
        traverse="/jobs/{id}",
    )
    config.add_route(
        "jobs",
        "/jobs",
    )
    config.add_view(
        job_view,
        route_name="job",
        renderer="/celery/job.mako",
        permission="context.view_job",
    )
    config.add_view(
        JobList,
        route_name="jobs",
        renderer="/celery/jobs.mako",
        permission=PERMISSIONS["global.superadmin"],
    )
    config.add_view(
        make_stream_csv_by_key("in_error_csv", "fichier_erreur.csv"),
        route_name="job",
        request_param="action=errors.csv",
        permission=PERMISSIONS["global.authenticated"],
    )
    config.add_view(
        make_stream_csv_by_key("unhandled_datas_csv", "fichier_non_traitées.csv"),
        route_name="job",
        request_param="action=unhandled.csv",
        permission=PERMISSIONS["global.authenticated"],
    )
    config.add_view(
        job_json_model_view,
        route_name="job",
        renderer="json",
        request_method="GET",
        xhr=True,
        permission="context.view_job",
    )
