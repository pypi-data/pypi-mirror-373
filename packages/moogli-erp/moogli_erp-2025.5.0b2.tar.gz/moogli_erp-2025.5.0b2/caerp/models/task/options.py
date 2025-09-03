from sqlalchemy import (
    Column,
    Boolean,
)
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)


class PaymentConditions(ConfigurableOption):
    __colanderalchemy_config__ = {
        "title": "Conditions de paiement",
        "description": "",
        "help_msg": "Configurer les conditions de paiement prédéfinies que \
les entrepreneurs pourront sélectionner lors de la création de leur devis. \
\n Vous pouvez les réordonner par glisser-déposer.",
        "validation_msg": "Les conditions de paiement ont bien \
été configurées",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter des conditions de paiement",
            "min_len": 1,
        },
    }
    id = get_id_foreignkey_col("configurable_option.id")
    default = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Valeur par défaut",
                "description": "Utiliser cette condition pour pré-remplir \
le champ 'Conditions de paiement' du formulaire de création de devis ?",
            }
        },
    )

    def __json__(self, request):
        result = ConfigurableOption.__json__(self, request)
        result["default"] = self.default
        return result
