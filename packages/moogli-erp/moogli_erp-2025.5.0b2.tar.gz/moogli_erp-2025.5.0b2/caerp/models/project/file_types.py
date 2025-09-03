"""
File types requirement models
"""
import typing
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Boolean,
)
from sqlalchemy.orm import (
    relationship,
    backref,
    load_only,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)


class BusinessTypeFileType(DBBASE):
    """
    Relationship table between

    :class:`caerp.models.project.types.BusinessType`
    and
    :class:`caerp.models.files.FileType`

    Describe the configured file requirements for a given business type
    """

    __tablename__ = "business_type_file_type"
    __table_args__ = default_table_args
    file_type_id = Column(ForeignKey("file_type.id"), primary_key=True)
    business_type_id = Column(ForeignKey("business_type.id"), primary_key=True)

    # estimation/invoice/cancelinvoice/business
    doctype = Column(String(14), primary_key=True)
    file_type = relationship(
        "FileType",
        backref=backref("business_type_rel", cascade="all, delete-orphan"),
    )
    business_type = relationship(
        "BusinessType",
        backref=backref("file_type_rel", cascade="all, delete-orphan"),
    )
    # project_mandatory / business_mandatory / mandatory / optionnal /
    # recommended
    requirement_type = Column(
        String(20),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Obligatoire ?",
            }
        },
    )
    validation = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Validation équipe d'appui ?",
                "description": "Ce document doit-il être validé par l'équipe "
                "d'appui ?",
            }
        },
    )
    PROJECT_MANDATORY = "project_mandatory"
    BUSINESS_MANDATORY = "business_mandatory"
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONNAL = "optionnal"

    # requirement qui implique un indicateur de statut
    STATUS_REQUIREMENT_TYPES = (
        PROJECT_MANDATORY,
        BUSINESS_MANDATORY,
        MANDATORY,
        RECOMMENDED,
    )

    @classmethod
    def get_file_requirements(cls, business_type_id, doctype, mandatory=False):
        """
        Collect file requirements related to a given business_type
        """
        query = cls.query().filter_by(business_type_id=business_type_id)
        query = query.filter_by(doctype=doctype)
        if mandatory:
            query = query.filter(cls.requirement_type.in_(cls.STATUS_REQUIREMENT_TYPES))
        return query

    @classmethod
    def get_file_type_options(
        cls,
        business_type_id: int,
        doctype: typing.Optional[str] = None,
        requirement_type: typing.Optional[str] = None,
    ):
        """
        Collect FileTypes associated to (business_type_id, doctype)

        :rtype: list
        """
        id_query = cls.query("file_type_id")
        id_query = id_query.filter_by(business_type_id=business_type_id)
        if doctype:
            id_query = id_query.filter_by(doctype=doctype)

        if requirement_type and requirement_type in cls.STATUS_REQUIREMENT_TYPES:
            id_query = id_query.filter_by(requirement_type=requirement_type)

        ids = [i[0] for i in id_query]

        result = []
        if ids is not None:
            from caerp.models.files import FileType

            query = (
                FileType.query()
                .options(load_only("id", "label"))
                .filter(FileType.id.in_(ids))
            )
            result = query.all()
        return result


class BusinessTypeFileTypeTemplate(DBBASE):
    __tablename__ = "business_type_file_type_template"
    __table_args__ = default_table_args
    business_type_id = Column(ForeignKey("business_type.id"), primary_key=True)
    file_type_id = Column(ForeignKey("file_type.id"), primary_key=True)
    file_id = Column(ForeignKey("file.id"))
    file_type = relationship("FileType", back_populates="business_file_template_rel")
    business_type = relationship("BusinessType", back_populates="file_template_rel")
    file = relationship(
        "File",
        primaryjoin="File.id==BusinessTypeFileTypeTemplate.file_id",
        backref=backref("template_backref", cascade="all, delete-orphan"),
    )

    def __json__(self, request):
        return {
            "business_type_id": self.business_type_id,
            "file_type_id": self.file_type_id,
            "file_id": self.file_id,
            "label": f"{self.file_type.label} - {self.file.name}",
            "file_type_label": self.file_type.label,
        }
