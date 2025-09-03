import logging
import colander
import deform
import deform_extensions
import functools

from colanderalchemy import SQLAlchemySchemaNode

from caerp.forms import customize_field
from caerp.models.tva import Tva, Product
from caerp.utils.html import clean_html
from caerp.forms.custom_types import AmountType


logger = logging.getLogger(__name__)


TVA_GRID = (
    (("active", 6),),
    (("name", 6), ("value", 6)),
    (("mention", 12),),
    (("compte_cg", 6), ("code", 6)),
    (("compte_a_payer", 6), ("compte_client", 6)),
    (("default", 12),),
    (("products", 12),),
)

PRODUCT_GRID = (
    (("name", 6), ("compte_cg", 6)),
    (("active", 12),),
    (("internal", 12),),
)


TVA_UNIQUE_VALUE_MSG = "Veillez à utiliser des valeurs différentes pour les \
différents taux de TVA. Pour les TVA de valeurs nulles, merci d’utiliser des \
valeurs négatives pour les distinguer (-1, -2...), elles seront ramenées à 0 \
pour toutes les opérations de calcul."


TVA_NO_DEFAULT_SET_MSG = "Veuillez définir au moins une TVA par défaut \
(aucune TVA par défaut n’a été configurée)."


PRODUCT_INTERNAL_MSG = (
    "Il existe déjà un produit dédié aux factures "
    "internes sur un autre taux de TVA : {0}."
)


def get_tva_value_validator(current):
    """
    Return a validator for tva entries

    :param int tva_id: The current configured tva
    :rtype: func
    """
    if isinstance(current, Tva):
        current_id = current.id
    else:
        current_id = None

    def validator(node, value):
        if not Tva.unique_value(value, current_id):
            raise colander.Invalid(node, TVA_UNIQUE_VALUE_MSG)

    return validator


@colander.deferred
def deferred_tva_value_validator(node, kw):
    """
    Ensure we've got a unique tva value and at least one default tva

    :param obj form: The deform.Form object
    :param dict tva_value: The value configured
    """
    context = kw["request"].context
    return get_tva_value_validator(context)


def has_tva_default_validator(node, value):
    """
    Validator for tva uniqueness
    """
    if Tva.get_default() is None and not value:
        raise colander.Invalid(node, TVA_NO_DEFAULT_SET_MSG)


@colander.deferred
def deferred_internal_validator(node, kw):
    """
    Ensure there is only internal products on the current TVA
    """
    current_tva = kw["request"].context

    def validator(node, value):
        """
        Check no other active tva has a product marked as internal
        """
        if value:
            query = (
                Tva.query().join(Product).filter(Product.internal == True)  # NOQA: E712
            )
            if isinstance(current_tva, Tva):
                # edit form
                query = query.filter(Tva.id != current_tva.id)
            if query.count() > 0:
                raise colander.Invalid(
                    node, PRODUCT_INTERNAL_MSG.format(query.first().name)
                )

    return validator


def customize_schema(schema):
    """
    Set the customization of the schema informations
    """
    schema.title = ""
    schema.widget = deform_extensions.GridFormWidget(named_grid=TVA_GRID)
    customize = functools.partial(customize_field, schema)
    customize("name", title="Libellé du taux de TVA")
    customize(
        "value",
        title="Valeur",
        typ=AmountType(),
        description="Le pourcentage associé (ex : 19.6)",
    )
    customize("compte_cg", title="Compte CG de Tva")
    customize("code", title="Code de Tva")
    customize(
        "compte_a_payer",
        title="Compte à payer",
        description="Utilisé dans les exports comptables des encaissements",
    )
    customize(
        "compte_client",
        title="Compte client",
        description="Compte comptable client propre à cette TVA",
    )
    customize(
        "mention",
        title="Mentions spécifiques à cette TVA",
        description="Si cette TVA est utilisée dans un devis/une facture, "
        "la mention apparaîtra dans la sortie PDF "
        "(ex: Mention pour la TVA liée aux formations ...)",
        widget=deform.widget.TextAreaWidget(rows=1),
        preparer=clean_html,
        missing="",
    )
    customize("default", title="Cette TVA doit-elle être proposée par défaut ?")
    customize(
        "products",
        title="Comptes produit associés",
        widget=deform.widget.SequenceWidget(
            add_subitem_text_template="Ajouter un compte produit", orderable=True
        ),
    )
    product_schema = schema["products"].children[0]
    product_schema.widget = deform_extensions.GridMappingWidget(named_grid=PRODUCT_GRID)
    product_schema.title = "Compte produit"
    customize_product = functools.partial(customize_field, product_schema)
    customize_product("id", widget=deform.widget.HiddenWidget())
    customize_product("name", title="Libellé")
    customize_product("compte_cg", title="Compte CG")
    customize_product(
        "active",
        title="Activer ce produit ?",
        description="Si ce produit est inactif, il ne sera plus proposé "
        "dans l’interface de configuration des produits",
    )
    customize_product(
        "internal",
        title="Facturation interne ?",
        description="Ce produit sera proposé dans les formulaires d’édition"
        " de factures internes",
        validator=deferred_internal_validator,
    )
    return schema


def get_tva_edit_schema():
    """
    Add a custom validation schema to the tva edition form
    :returns: :class:`colander.Schema` schema for single tva admin
    """
    from caerp.models.tva import Tva

    excludes = ("active", "id")
    schema = SQLAlchemySchemaNode(Tva, excludes=excludes)
    customize_schema(schema)
    schema["value"].validator = deferred_tva_value_validator
    schema["value"].missing = colander.required
    schema["default"].validator = has_tva_default_validator
    return schema
