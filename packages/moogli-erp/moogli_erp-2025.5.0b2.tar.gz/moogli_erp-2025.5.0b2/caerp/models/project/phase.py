from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    default_table_args,
    DBBASE,
)
from .services.phase import PhaseService


class Phase(DBBASE):
    """
    Phase d'un dossier
    """

    __tablename__ = "phase"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    project_id = Column(
        ForeignKey("project.id"),
        info={"colanderalchemy": {"exclude": True}},
    )

    name = Column("name", String(150), default="Dossier par défaut")

    project = relationship(
        "Project",
        back_populates="phases",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )

    _caerp_service = PhaseService

    def is_default(self):
        """
        return True if this phase is a default one
        """
        return self.name in (
            "Phase par défaut",
            "default",
            "défaut",
            "Dossier par défaut",
        )

    @property
    def estimations(self):
        return self.get_tasks_by_type("estimation")

    @property
    def invoices(self):
        return self.get_tasks_by_type("invoice")

    @property
    def cancelinvoices(self):
        return self.get_tasks_by_type("cancelinvoice")

    def get_tasks_by_type(self, type_):
        """
        return the tasks of the passed type
        """
        return [doc for doc in self.tasks if doc.type_ == type_]

    def __json__(self, request):
        """
        return a dict version of this object
        """
        return dict(id=self.id, name=self.name)

    def label(self):
        """
        Return a label representing this phase
        """
        if self.is_default():
            return "Dossier par défaut"
        else:
            return self.name

    @classmethod
    def query_for_select(cls, project_id):
        """
        Build a sqla query suitable for a select widget

        :param int project_id: The project the phases are attached to
        """
        return cls._caerp_service.query_for_select(cls, project_id)
