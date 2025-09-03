"""
Modèle pour les mentions dans les devis et factures
"""
import sqlalchemy as sa

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)


TASK_MENTION = sa.Table(
    "task_mention_rel",
    DBBASE.metadata,
    sa.Column("task_id", sa.Integer, sa.ForeignKey("task.id", ondelete="cascade")),
    sa.Column("mention_id", sa.Integer, sa.ForeignKey("task_mention.id")),
    sa.UniqueConstraint("task_id", "mention_id"),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)
MANDATORY_TASK_MENTION = sa.Table(
    "mandatory_task_mention_rel",
    DBBASE.metadata,
    sa.Column("task_id", sa.Integer, sa.ForeignKey("task.id")),
    sa.Column("mention_id", sa.Integer, sa.ForeignKey("task_mention.id")),
    sa.UniqueConstraint("task_id", "mention_id"),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class TaskMention(ConfigurableOption):
    __colanderalchemy_config__ = {
        "title": "Mentions facultatives des devis/factures",
        "description": (
            "Configurer les mentions que les entrepreneurs peuvent faire"
            " figurer dans leurs devis/factures"
        ),
    }
    id = get_id_foreignkey_col("configurable_option.id")
    title = sa.Column(
        sa.String(255),
        default="",
        info={
            "colanderalchemy": {
                "title": "Titre à afficher dans les PDF",
                "description": (
                    "Texte apparaissant sous forme de titre dans la sortie PDF"
                    " (facultatif)"
                ),
            }
        },
    )
    full_text = sa.Column(
        sa.Text(),
        info={
            "colanderalchemy": {
                "title": "Texte à afficher dans les PDF",
                "description": (
                    "Si cette mention a été ajoutée à un devis/facture, ce"
                    " texte apparaitra dans la sortie PDF"
                ),
            }
        },
    )
    help_text = sa.Column(
        sa.String(255),
        info={
            "colanderalchemy": {
                "title": "Texte d'aide à l'utilisation",
                "description": "Aide fournie à l'entrepreneur dans l'interface",
            }
        },
    )

    def __json__(self, request):
        dic = super(TaskMention, self).__json__(request)
        dic.update(
            dict(
                help_text=self.help_text,
            )
        )
        return dic

    @property
    def is_used(self):
        task_query = (
            DBSESSION()
            .query(TASK_MENTION.c.task_id)
            .filter(TASK_MENTION.c.mention_id == self.id)
        )

        mandatory_query = (
            DBSESSION()
            .query(MANDATORY_TASK_MENTION.c.task_id)
            .filter(MANDATORY_TASK_MENTION.c.mention_id == self.id)
        )

        return (
            DBSESSION().query(task_query.exists()).scalar()
            or DBSESSION().query(mandatory_query.exists()).scalar()
        )
