"""
    File model
"""

import logging
import io
from datetime import datetime
from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    DateTime,
    String,
    Boolean,
    event,
    Text,
)

from sqlalchemy.orm import (
    relationship,
    backref,
    aliased,
    contains_eager,
    load_only,
)

from depot.fields.sqlalchemy import (
    UploadedFileField,
    _SQLAMutationTracker,
)

from caerp_base.models.base import (
    default_table_args,
    DBBASE,
    DBSESSION,
)
from caerp.models.node import Node
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)
from caerp.utils.datetimes import format_date
from caerp.utils.filedepot import _to_fieldstorage
from caerp.forms import EXCLUDED
from caerp.utils.strings import human_readable_filesize


logger = logging.getLogger(__name__)


class File(Node):
    """
    A file model
    """

    __tablename__ = "file"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "file"}
    id = Column(Integer, ForeignKey("node.id"), primary_key=True)
    description = Column(Text(), default="")
    data = Column(UploadedFileField)
    mimetype = Column(String(100))
    size = Column(Integer)
    file_type_id = Column(Integer, ForeignKey("file_type.id"), nullable=True)
    file_type = relationship("FileType")
    is_signed = Column(Boolean, default=False)

    sale_file_requirements = relationship(
        "SaleFileRequirement", back_populates="file_object"
    )
    company_logo_backref = relationship(
        "Company",
        foreign_keys="Company.logo_id",
        back_populates="logo_file",
        uselist=False,
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    company_header_backref = relationship(
        "Company",
        foreign_keys="Company.header_id",
        back_populates="header_file",
        uselist=False,
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    sepa_credit_transfer_backref = relationship(
        "SepaCreditTransfer",
        back_populates="file",
        uselist=False,
    )
    user_photo_backref = relationship(
        "User",
        back_populates="photo_file",
        uselist=False,
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )

    def getvalue(self):
        """
        Method making our file object compatible with the common file rendering
        utility
        """
        if self.data is not None:
            return self.data.file.read()
        else:
            return None

    @property
    def label(self):
        """
        Simple shortcut for getting a label for this file
        """
        return self.description or self.name

    @property
    def data_obj(self):
        try:
            return io.BytesIO(self.getvalue())
        except IOError:
            logger.exception("!!! Filestorage File is missing on disk !!!")
            return ""

    @classmethod
    def __declare_last__(cls):
        # Unconfigure the event set in _SQLAMutationTracker, we have _save_data
        mapper = cls._sa_class_manager.mapper
        args = (mapper.attrs["data"], "set", _SQLAMutationTracker._field_set)
        if event.contains(*args):
            event.remove(*args)

        # Declaring the event on the class attribute instead of mapper property
        # enables proper registration on its subclasses
        event.listen(cls.data, "set", cls._set_data, retval=True)

    @classmethod
    def _set_data(cls, target, value, oldvalue, initiator):
        # Ref #384 : enforce this method
        if hasattr(value, "seek"):
            value.seek(0)
            value = value.read()

        if isinstance(value, bytes):
            value = _to_fieldstorage(
                fp=io.BytesIO(value),
                filename=target.name,
                size=len(value),
                mimetype=target.mimetype,
            )
        newvalue = _SQLAMutationTracker._field_set(target, value, oldvalue, initiator)

        return newvalue

    @classmethod
    def query_for_filetable(cls):
        """
        Build a File query for filetable display

        Query only columns used for generic display

        :rtype: :class:`sqlalchemy.orm.Query`
        """
        query = cls.query().options(
            load_only("description", "name", "id", "updated_at", "size", "parent_id")
        )
        # On charge le nom du Node parent, comme File est également un Node, on
        # doit fournir un alias à sqlalchemy pour qu'il ajoute un as et sache
        # quelle action effectuer sur quel Node de sa query
        node_alias = aliased(Node)
        query = query.join(node_alias, cls.parent)
        query = query.outerjoin(cls.file_type)
        query = query.options(
            contains_eager(cls.parent, alias=node_alias).load_only(
                "id",
                "name",
                "type_",
            )
        )
        return query

    def duplicate(self):
        newone = self.__class__(
            name=self.name,
            description=self.description,
            size=self.size,
            mimetype=self.mimetype,
        )
        newone.data = self.data_obj
        DBSESSION().add(newone)
        DBSESSION().flush()
        return newone

    def __json__(self, request):
        return {
            "id": self.id,
            "label": self.label,
            "name": self.name,
            "size": self.size,
            "human_size": human_readable_filesize(self.size),
            "mimetype": self.mimetype,
            "description": self.description,
            "created_at": format_date(self.created_at),
            "updated_at": format_date(self.updated_at),
            "file_type_id": self.file_type_id,
            "parent_id": self.parent_id,
            "is_signed": self.is_signed,
        }

    def get_company_id(self):
        if self.parent:
            if hasattr(self.parent, "company_id"):
                return self.parent.company_id
            elif hasattr(self.parent, "get_company_id"):
                return self.parent.get_company_id()
        return None


class FileType(ConfigurableOption):
    __colanderalchemy_config__ = {
        "title": "Type de documents utilisés dans MoOGLi",
        "validation_msg": "Les types de documents ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")

    business_file_template_rel = relationship(
        "BusinessTypeFileTypeTemplate",
        cascade="all, delete-orphan",
        back_populates="file_type",
        lazy="dynamic",
    )

    @property
    def is_used(self):
        query = DBSESSION().query(File).filter_by(file_type_id=self.id)
        file_exists = DBSESSION().query(query.exists()).scalar()

        indicator_query = self.query_indicators()
        indicator_exists = DBSESSION().query(indicator_query.exists()).scalar()
        return file_exists or indicator_exists

    def query_indicators(self):
        """
        Query indicators attached to this FileType

        :rtype: A SqlAlchemy query
        """
        from caerp.models.indicators import SaleFileRequirement

        return DBSESSION().query(SaleFileRequirement).filter_by(file_type_id=self.id)

    def query_requirements(self):
        """
        Query indicators attached to this FileType

        :rtype: A SqlAlchemy query
        """
        from caerp.models.project.file_types import BusinessTypeFileType

        return DBSESSION().query(BusinessTypeFileType).filter_by(file_type_id=self.id)

    @classmethod
    def get_by_label(cls, label):
        return cls.query().filter_by(label=label).first()

    def get_template_id(self, business_type_id) -> int:
        """Find the File Template for this given file type and the associated business_type_id"""
        btype_file_type_template_rel = self.business_file_template_rel.filter_by(
            business_type_id=business_type_id
        ).first()
        if not btype_file_type_template_rel:
            return None
        else:
            return btype_file_type_template_rel.file_id


class Template(File):
    """
    A template model for odt templates
    """

    __tablename__ = "templates"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "template"}
    id = Column(ForeignKey("file.id"), primary_key=True)
    active = Column(Boolean(), default=True)

    @property
    def label(self):
        return self.name

    @classmethod
    def __declare_last__(cls):
        # Unconfigure the event set in _SQLAMutationTracker, we have _save_data
        mapper = cls._sa_class_manager.mapper
        args = (mapper.attrs["data"], "set", _SQLAMutationTracker._field_set)
        if event.contains(*args):
            event.remove(*args)

        # Declaring the event on the class attribute instead of mapper property
        # enables proper registration on its subclasses
        event.listen(cls.data, "set", cls._set_data, retval=True)


class TemplatingHistory(DBBASE):
    """
    Record all the templating fired for a given userdata account
    """

    __tablename__ = "template_history"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(),
        default=datetime.now,
        info={"colanderalchemy": {"title": "Date de génération"}},
    )
    user_id = Column(
        ForeignKey("accounts.id"),
        info={
            "colanderalchemy": EXCLUDED,
            "export": EXCLUDED,
        },
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id"),
        info={
            "colanderalchemy": EXCLUDED,
            "export": EXCLUDED,
        },
    )
    template_id = Column(
        ForeignKey("templates.id"),
        info={"colanderalchemy": {"title": "Type de document"}},
    )

    user = relationship(
        "User",
        info={
            "colanderalchemy": EXCLUDED,
            "export": EXCLUDED,
        },
    )
    userdatas = relationship(
        "UserDatas",
        backref=backref(
            "template_history",
            cascade="all, delete-orphan",
            info={
                "colanderalchemy": EXCLUDED,
                "export": {
                    "exclude": True,
                    "stats": {"label": "Génération de documents - ", "exclude": False},
                },
            },
        ),
        info={
            "colanderalchemy": EXCLUDED,
            "export": EXCLUDED,
        },
    )
    template = relationship(
        "Template",
        backref=backref(
            "templated",
            cascade="all, delete-orphan",
            info={
                "export": {"exclude": True},
            },
        ),
    )
