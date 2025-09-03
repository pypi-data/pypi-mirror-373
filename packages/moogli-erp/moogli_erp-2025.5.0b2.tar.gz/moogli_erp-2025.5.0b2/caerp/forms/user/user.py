"""
    User account handling form schemas
"""
import colander
import logging
import deform
import functools
import datetime
from colanderalchemy import SQLAlchemySchemaNode
import deform.widget

from caerp_base.consts import CIVILITE_OPTIONS
from caerp.models.user import User, Group
from caerp.models.expense.types import ExpenseKmType
from caerp import forms
from caerp.forms.company import (
    deferred_company_datas_select,
    deferred_company_datas_validator,
)
from caerp.forms.user import antenne_filter_node_factory, follower_filter_node_factory
from caerp.forms import files
from caerp.utils.image import ImageResizer

logger = log = logging.getLogger(__name__)

IMAGE_RESIZER = ImageResizer(400, 400)


@colander.deferred
def deferred_user_groups_datas_select(node, kw):
    values = Group.query("id", "label").all()
    values.insert(0, ("", "- Sélectionner un rôle"))
    return deform.widget.SelectWidget(values=values)


@colander.deferred
def deferred_user_groups_datas_validator(node, kw):
    ids = [entry[0] for entry in Group.query("id")]
    return colander.OneOf(ids)


@colander.deferred
def deferred_company_disable_description(node, kw):
    """
    Return the description for the company disabling checkbox
    """
    description = "Entraîne automatiquement la désactivation des employés."
    for company in kw["request"].context.companies:
        if len(company.employees) > 1:
            description += "Attention : Au moins l'une de ses enseignes a \
plusieurs employés"
            break
    return description


@colander.deferred
def deferred_company_disable_default(node, kw):
    """
    return False is one of the user's companies have some employees
    """
    for company in kw["request"].context.companies:
        if len(company.employees) > 1:
            return False
    return True


class UserDisableSchema(colander.MappingSchema):
    disable = colander.SchemaNode(
        colander.Boolean(),
        default=True,
        title="Désactiver cet utilisateur",
        description="""Désactiver un utilisateur l'empêche de se
connecter mais permet de conserver l'intégralité
des informations concernant son activité.""",
    )
    companies = colander.SchemaNode(
        colander.Boolean(),
        title="Désactiver ses enseignes",
        description=deferred_company_disable_description,
        default=deferred_company_disable_default,
    )


def set_widgets(schema):
    """
    Customize form widgets

    :param obj schema: The colander Schema to edit
    """
    customize = functools.partial(forms.customize_field, schema)
    if "vehicle" in schema:
        customize(
            "vehicle",
            widget=forms.get_deferred_select(
                ExpenseKmType,
                keys=(
                    lambda a: "%s-%s" % (a.label, a.code),
                    lambda a: "%s (%s)" % (a.label, a.code),
                ),
                filters=[("active", True)],
            ),
        )

    if "civilite" in schema:
        customize(
            "civilite",
            widget=forms.get_select(CIVILITE_OPTIONS),
            validator=forms.get_select_validator(CIVILITE_OPTIONS),
        )

    if "email" in schema:
        customize("email", validator=forms.mail_validator())

    if "bank_account_iban" in schema:
        schema["bank_account_iban"].validator = forms.iban_validator
    if "bank_account_bic" in schema:
        schema["bank_account_bic"].validator = forms.bic_validator

    return schema


def get_list_schema(admin: bool = False):
    """
    Return a schema for filtering the user list
    """
    schema = forms.lists.BaseListsSchema().clone()

    schema["search"].title = "Nom, enseigne, activité"
    schema["items_per_page"].default = 50

    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.String(),
            name="account_type",
            title="Type de compte",
            widget=deform.widget.SelectWidget(
                values=(
                    ("all", "Tous"),
                    ("entrepreneur", "Entrepreneur"),
                    ("equipe_appui", "Équipe d'appui"),
                    ("hybride", "Hybride (ES et EA)"),
                )
            ),
            default="all",
            missing="all",
            validator=colander.OneOf(
                ["all", "entrepreneur", "equipe_appui", "hybride"]
            ),
        ),
    )

    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.Integer(),
            name="activity_id",
            title="Type d'activité",
            missing=colander.drop,
            widget=deferred_company_datas_select,
            validator=deferred_company_datas_validator,
        ),
    )
    schema.add_before("items_per_page", antenne_filter_node_factory(name="antenne_id"))
    if admin:
        schema.add_before(
            "items_per_page", follower_filter_node_factory(name="follower_id")
        )
        schema.add_before(
            "items_per_page",
            colander.SchemaNode(
                colander.Integer(),
                name="group_id",
                title="Rôle",
                missing=colander.drop,
                widget=deferred_user_groups_datas_select,
                validator=deferred_user_groups_datas_validator,
            ),
        )
        schema.add_before(
            "items_per_page",
            colander.SchemaNode(
                colander.String(),
                name="login_filter",
                title="Comptes",
                widget=deform.widget.SelectWidget(
                    values=(
                        ("active_login", "Seulement les comptes actifs"),
                        ("unactive_login", "Seulement les comptes désactivés"),
                        ("with_login", "Tous les comptes avec identifiants"),
                    )
                ),
                default="active_login",
                missing=colander.drop,
            ),
        )
    return schema


def get_add_edit_schema(edit=False):
    """
    Return a user add schema
    """
    schema = SQLAlchemySchemaNode(
        User,
        includes=(
            "civilite",
            "firstname",
            "lastname",
            "email",
        ),
    )
    schema.add(
        files.ImageNode(
            name="photo",
            preparer=files.get_file_upload_preparer([IMAGE_RESIZER]),
            title="Choisir une photo",
            missing=colander.drop,
            show_delete_control=True,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="photo_is_publishable",
            title="Photo publiable dans l'annuaire",
        )
    )
    if not edit:
        schema.add(
            colander.SchemaNode(
                colander.Boolean(),
                name="add_login",
                title="Créer des identifiants pour ce compte ?",
                description="Les identifiants permettront au titulaire de ce "
                "compte de se connecter",
            )
        )
    set_widgets(schema)
    return schema


def get_edit_accounting_schema():
    """
    Return a schema for user accounting datas edition
    """
    schema = SQLAlchemySchemaNode(
        User,
        includes=(
            "vehicle",
            "vehicle_fiscal_power",
            "vehicle_registration",
            "compte_tiers",
            "bank_account_iban",
            "bank_account_bic",
            "bank_account_owner",
        ),
    )
    set_widgets(schema)
    return schema


def get_edit_account_schema():
    """
    Build a schema for user account schema edition

    Allow to edit email informations
    """
    schema = SQLAlchemySchemaNode(
        User,
        includes=(
            "firstname",
            "lastname",
            "email",
        ),
    )
    schema.add(
        files.ImageNode(
            name="photo",
            preparer=files.get_file_upload_preparer([IMAGE_RESIZER]),
            title="Choisir une photo",
            missing=colander.drop,
            show_delete_control=True,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="photo_is_publishable",
            title="Photo publiable dans l'annuaire",
        )
    )
    set_widgets(schema)
    return schema


def get_connections_years(kw):
    years = []
    current_year = datetime.date.today().year
    years.append(current_year - 1)
    years.append(current_year)
    return years


def get_connections_schema():
    """
    Return a schema for filtering the users connections list
    """
    schema = forms.lists.BaseListsSchema().clone()
    del schema["search"]
    schema["items_per_page"].default = 30
    today = datetime.date.today()
    schema.insert(
        0,
        forms.month_select_node(
            title="Mois",
            default=today.month,
            name="month",
        ),
    )
    schema.insert(
        0,
        forms.year_filter_node(
            name="year",
            title="Année",
            query_func=get_connections_years,
            default=today.year,
            widget_options={"default_val": None},
        ),
    )
    return schema
