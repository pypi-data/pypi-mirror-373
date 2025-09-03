"""
Form configuration related models
Labels / defaults / required ...
"""
from caerp_base.models.base import DBBASE
import sqlalchemy as sa


class FormFieldDefinition(DBBASE):
    """
    Custom definition for a form field
    inherits title/active/order
    """

    id = sa.Column(sa.Integer, primary_key=True)
    form = sa.Column(
        sa.String(50),
        default="task",
        info={"colanderalchemy": {"title": "Type de formulaire"}},
    )
    field_name = sa.Column(
        sa.String(50),
        nullable=False,
        info={"colanderalchemy": {"title": "Nom du champ"}},
    )
    title = sa.Column(
        sa.String(255),
        nullable=False,
        info={
            "colanderalchemy": {"title": "Libellé dans le formulaire et les documents"}
        },
    )
    required = sa.Column(
        sa.Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Champ obligatoire ?",
            }
        },
    )
    visible = sa.Column(
        sa.Boolean(),
        default=True,
        info={
            "colanderalchemy": {
                "title": "Champ proposé à l'utilisateur ?",
            }
        },
    )
    default = sa.Column(
        sa.String(255),
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Valeur par défaut",
            }
        },
    )

    @classmethod
    def get_definitions(cls, form_name: str = "task"):
        """
        Collect FormFieldDefinitions related to form_name
        """
        return cls.query().filter(cls.form == form_name).filter(cls.visible == 1)

    @classmethod
    def get_definition(cls, field_name: str, form_name: str = "task"):
        """
        Fin a form definition
        """
        return (
            cls.query()
            .filter(cls.form == form_name, cls.field_name == field_name)
            .first()
        )

    def form_config(self) -> dict:
        """
        Build a dict matching the form_config views representation
        """
        if self.visible:
            return {
                self.field_name: {
                    "title": self.title,
                    "required": self.required,
                    "visible": self.visible,
                    "edit": True,
                    "default": self.default,
                }
            }
        else:
            return {}

    @classmethod
    def get_default(cls, field_name: str, form_name: str = "task") -> str:
        field_def = cls.get_definition(field_name, form_name)
        res = None
        if field_def is not None:
            res = field_def.default
        return res

    @classmethod
    def get_form_labels(cls, form_name: str = "task"):
        result = {}
        for field_def in cls.get_definitions(form_name):
            result[field_def.field_name] = field_def.title
        return result
