from caerp_base.models.base import DBSESSION


class PhaseService:
    @classmethod
    def query_for_select(cls, phase_class, project_id):
        query = DBSESSION().query(phase_class.id, phase_class.name)
        return query.filter_by(project_id=project_id)
