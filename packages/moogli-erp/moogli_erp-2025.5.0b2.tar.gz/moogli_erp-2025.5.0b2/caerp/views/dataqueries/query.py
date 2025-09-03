import logging

from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPNotFound

from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import export_dataquery_to_file

from caerp.utils.strings import convert_to_string
from caerp.views import BaseView, AsyncJobMixin


logger = logging.getLogger(__name__)


class DataQueryView(BaseView, AsyncJobMixin):
    """
    Vue traitant la génération des requêtes statistiques

    Affiche un formulaire permettant de choisir la période (à l'instant T, à une
    date donnée, ou entre 2 dates - selon les attributs définis sur la requête),
    ainsi que le format de sortie (type d'export ou affichage).

    Si le format est défini, génère les données de la requête et traite leur sortie
    en fonction du format demandé par l'utilisateur.
    """

    def _get_dataquery_object(self):
        dataquery_name = self.request.matchdict["dqname"]
        dataquery_obj = self.request.get_dataquery(dataquery_name)
        if dataquery_obj is None:
            logger.error(f"DataQuery '{dataquery_name}' doesn't exist")
            raise HTTPNotFound()
        else:
            return dataquery_obj

    def _stringify_dataquery_data(self, dataquery_data):
        for y, result in enumerate(dataquery_data):
            for x, value in enumerate(result):
                dataquery_data[y][x] = convert_to_string(value)
        return dataquery_data

    def __call__(self):
        dataquery_headers = []
        dataquery_data = []
        dataquery_obj = self._get_dataquery_object()
        dataquery_obj.set_dates(
            self.request.GET["start"] if "start" in self.request.GET else None,
            self.request.GET["end"] if "end" in self.request.GET else None,
        )
        if "format" in self.request.GET:
            format = self.request.GET["format"]
            if format == "display":
                dataquery_headers = dataquery_obj.headers()
                dataquery_data = self._stringify_dataquery_data(dataquery_obj.data())
            else:
                celery_error_resp = self.is_celery_alive()
                if celery_error_resp:
                    return celery_error_resp
                else:
                    job_result = self.initialize_job_result(FileGenerationJob)
                    celery_job = export_dataquery_to_file.delay(
                        job_result.id,
                        dataquery_obj.name,
                        format,
                        start=dataquery_obj.start_date,
                        end=dataquery_obj.end_date,
                    )
                    return self.redirect_to_job_watch(celery_job, job_result)
        return dict(
            title="Requête statistique",
            name=dataquery_obj.name,
            label=dataquery_obj.label,
            description=dataquery_obj.description,
            start_date=dataquery_obj.start_date,
            end_date=dataquery_obj.end_date,
            headers=dataquery_headers,
            data=dataquery_data,
        )


def includeme(config):
    config.add_route("dataquery", "dataqueries/{dqname}")
    config.add_view(
        DataQueryView,
        route_name="dataquery",
        renderer="dataqueries/query.mako",
        permission=PERMISSIONS["global.view_dataquery"],
    )
