"""
Userdatas related form informations
"""
import colander
import logging
import deform
import deform_extensions
import functools
import json
from sqlalchemy import select, distinct

from colanderalchemy import SQLAlchemySchemaNode

from caerp_base.consts import (
    SEX_OPTIONS,
    CIVILITE_OPTIONS,
)
from caerp.consts.permissions import PERMISSIONS
from caerp.models.config import Config
from caerp.models.user.login import ACCOUNT_TYPES
from caerp.models.user.userdatas import (
    CaeSituationOption,
    UserDatas,
    AntenneOption,
    ZoneOption,
    ZoneQualificationOption,
    StudyLevelOption,
    SocialStatusOption,
    ActivityTypeOption,
    PcsOption,
    PrescripteurOption,
    NonAdmissionOption,
    ParcoursStatusOption,
    STATUS_OPTIONS,
    CONTRACT_OPTIONS,
    UserDatasSocialDocTypes,
    CareContractOption,
    AidOrganismOption,
    UserDatasCustomFields,
)
from caerp.models.company import CompanyActivity
from caerp.forms.widgets import CleanMappingWidget
from caerp.forms.lists import BaseListsSchema
from caerp.forms.user import (
    conseiller_filter_node_factory,
    get_deferred_user_choice,
)
from caerp.forms import (
    customize_field,
    get_deferred_select,
    get_deferred_select_validator,
    get_select,
    get_select_validator,
    mail_validator,
    iban_validator,
    bic_validator,
)
from caerp.utils.colanderalchemy import (
    get_model_columns_list,
    get_colanderalchemy_model_sections,
    get_model_columns_by_colanderalchemy_section,
)

logger = logging.getLogger(__name__)

USERDATAS_FORM_GRIDS = {
    "Synthèse": (
        (
            ("situation_follower_id", 6),
            ("situation_antenne_id", 6),
        ),
        (
            ("parcours_prescripteur_id", 6),
            ("parcours_prescripteur_name", 6),
        ),
        (
            ("parcours_date_info_coll", 3),
            ("situation_societariat_entrance", 3),
            ("parcours_non_admission_id", 6),
        ),
    ),
    "Coordonnées": (
        (
            ("coordonnees_civilite", 3),
            ("coordonnees_lastname", 3),
            ("coordonnees_firstname", 3),
            ("coordonnees_ladies_lastname", 3),
        ),
        (
            ("coordonnees_email1", 6),
            ("coordonnees_email2", 6),
        ),
        (
            ("coordonnees_tel", 3),
            ("coordonnees_mobile", 3),
        ),
        (("coordonnees_address", 12),),
        (
            ("coordonnees_zipcode", 3),
            ("coordonnees_city", 9),
        ),
        (
            ("coordonnees_zone_id", 6),
            ("coordonnees_zone_qual_id", 6),
        ),
        (("coordonnees_sex", 3),),
        (
            ("coordonnees_birthday", 3),
            ("coordonnees_birthplace", 6),
            ("coordonnees_birthplace_zipcode", 3),
        ),
        (
            ("coordonnees_nationality", 3),
            ("coordonnees_resident", 3),
        ),
        (("coordonnees_secu", 6),),
        (
            ("coordonnees_family_status", 4),
            ("coordonnees_children", 4),
            ("coordonnees_study_level_id", 4),
        ),
        (
            ("coordonnees_emergency_name", 6),
            ("coordonnees_emergency_phone", 6),
        ),
        (("coordonnees_identifiant_interne", 6),),
    ),
    "Statut": (
        (("social_statuses", 12),),
        (("today_social_statuses", 12),),
        (("statut_end_rights_date", 6),),
        (("statut_handicap_allocation_expiration", 6),),
        (("statut_external_activity", 12),),
        (("statut_bank_accounts", 12),),
        (("statut_aid_organisms", 12),),
    ),
    "Activité": (
        (
            ("activity_typologie_id", 6),
            ("activity_pcs_id", 6),
        ),
        (("activity_companydatas", 12),),
        (("parcours_goals", 12),),
        (
            ("parcours_medical_visit", 3),
            ("parcours_medical_visit_limit", 3),
            ("parcours_status_id", 6),
        ),
        (("activity_care_contracts", 12),),
    ),
}


def get_custom_fields_schema_grid():
    """
    Build a colander schema grid for UserDatasCustomFields
    """
    schema_grid = {}
    for section in get_colanderalchemy_model_sections(UserDatasCustomFields):
        section_grid = ()
        for field in get_model_columns_by_colanderalchemy_section(
            UserDatasCustomFields, section
        ):
            section_grid += (((field.name, 12),),)
        schema_grid[section] = section_grid
    return schema_grid


def get_deferred_userdatas_custom_field_widget(field):
    column = getattr(UserDatasCustomFields, field.name)

    @colander.deferred
    def deferred_userdatas_custom_field_widget(node, kw):
        """Build an autocomplete widget using field name as options"""
        query = select(distinct(column)).where(column.isnot(None))
        values = kw["request"].dbsession.execute(query).scalars().all()
        return deform.widget.AutocompleteInputWidget(values=values)


def add_custom_fields_to_schema(schema):
    """
    Add autorized custom fields the form schema
    :param obj schema: A UserDatas schema
    """
    custom_fields_to_exclude = ()
    custom_fields_to_display = json.loads(
        Config.get_value("userdatas_active_custom_fields", "[]")
    )

    for field in get_model_columns_list(UserDatasCustomFields):
        if not field.name in custom_fields_to_display:
            custom_fields_to_exclude += (field.name,)

    schema.children.append(
        SQLAlchemySchemaNode(
            UserDatasCustomFields,
            name="custom_fields",
            title="",
            excludes=custom_fields_to_exclude,
            widget=deform_extensions.AccordionFormWidget(
                named_grids=get_custom_fields_schema_grid(),
                template="caerp:templates/deform/accordions_mapping.pt",
                default_open=False,
            ),
            missing=colander.drop,
        )
    )
    return schema


def customize_schema(schema):
    """
    Customize the form schema
    :param obj schema: A UserDatas schema
    """
    customize = functools.partial(customize_field, schema)

    customize("situation_antenne_id", get_deferred_select(AntenneOption))

    customize(
        "situation_follower_id",
        get_deferred_user_choice(
            account_type=ACCOUNT_TYPES["equipe_appui"],
            widget_options={
                "default_option": ("", ""),
            },
        ),
    )

    customize("coordonnees_civilite", get_select(CIVILITE_OPTIONS))

    customize("coordonnees_email1", validator=mail_validator())
    customize("coordonnees_email2", validator=mail_validator())

    customize(
        "coordonnees_address",
        deform.widget.TextAreaWidget(),
    )

    customize(
        "coordonnees_zone_id",
        get_deferred_select(ZoneOption),
    )

    customize(
        "coordonnees_zone_qual_id",
        get_deferred_select(ZoneQualificationOption),
    )

    customize(
        "coordonnees_sex", get_select(SEX_OPTIONS), get_select_validator(SEX_OPTIONS)
    )

    customize(
        "coordonnees_family_status",
        get_select(STATUS_OPTIONS),
        get_select_validator(STATUS_OPTIONS),
    )

    customize(
        "coordonnees_children", get_select(list(zip(list(range(20)), list(range(20)))))
    )

    customize(
        "coordonnees_study_level_id",
        get_deferred_select(StudyLevelOption),
    )

    customize(
        "statut_social_status_id",
        get_deferred_select(SocialStatusOption),
    )

    customize(
        "statut_social_status_today_id",
        get_deferred_select(SocialStatusOption),
    )

    customize("activity_typologie_id", get_deferred_select(ActivityTypeOption))

    customize("activity_pcs_id", get_deferred_select(PcsOption))

    customize(
        "parcours_prescripteur_id",
        get_deferred_select(PrescripteurOption),
    )

    customize(
        "parcours_non_admission_id",
        get_deferred_select(NonAdmissionOption),
    )

    if "social_statuses" in schema:
        child_schema = schema["social_statuses"].children[0]
        child_schema.widget = CleanMappingWidget()
        customize_field(
            child_schema,
            "social_status_id",
            widget=get_deferred_select(SocialStatusOption),
        )
        customize_field(
            child_schema, "step", widget=deform.widget.HiddenWidget(), default="entry"
        )

    if "today_social_statuses" in schema:
        child_schema = schema["today_social_statuses"].children[0]
        child_schema.widget = CleanMappingWidget()
        customize_field(
            child_schema,
            "social_status_id",
            widget=get_deferred_select(SocialStatusOption),
        )
        customize_field(
            child_schema, "step", widget=deform.widget.HiddenWidget(), default="today"
        )

    if "statut_external_activity" in schema:
        child_schema = schema["statut_external_activity"].children[0]
        child_schema.widget = CleanMappingWidget()
        customize_field(
            child_schema,
            "type",
            widget=get_select(CONTRACT_OPTIONS),
        )

    if "statut_bank_accounts" in schema:
        child_schema = schema["statut_bank_accounts"].children[0]
        child_schema.widget = CleanMappingWidget()
        customize_field(child_schema, "bic", validator=iban_validator)
        customize_field(child_schema, "iban", validator=bic_validator)

    if "statut_aid_organisms" in schema:
        schema["statut_aid_organisms"].missing = colander.drop
        child_schema = schema["statut_aid_organisms"].children[0]
        child_schema.widget = CleanMappingWidget()
        customize_field(
            child_schema,
            "aid_organism_id",
            widget=get_deferred_select(AidOrganismOption),
        )
        customize_field(child_schema, "details", widget=deform.widget.TextAreaWidget())

    if "activity_companydatas" in schema:
        child_schema = schema["activity_companydatas"].children[0]
        child_schema.widget = CleanMappingWidget()
        customize_field(
            child_schema, "activity_id", widget=get_deferred_select(CompanyActivity)
        )

    if "activity_care_contracts" in schema:
        schema["activity_care_contracts"].missing = colander.drop
        child_schema = schema["activity_care_contracts"].children[0]
        child_schema.widget = CleanMappingWidget()
        customize_field(
            child_schema,
            "care_contract_id",
            widget=get_deferred_select(CareContractOption),
        )
        customize_field(child_schema, "details", widget=deform.widget.TextAreaWidget())

    customize("parcours_goals", deform.widget.TextAreaWidget())
    customize("parcours_status_id", get_deferred_select(ParcoursStatusOption))

    # CHAMPS COMPLÉMENTAIRES
    if "custom_fields" in schema:
        for field in schema["custom_fields"]:
            """
            All custom fields are not required et text inputs are
            autocompleted with db values
            """
            field.missing = colander.drop
            if isinstance(field.typ, colander.String):
                customize_field(
                    schema["custom_fields"],
                    f"{field.name}",
                    widget=get_deferred_userdatas_custom_field_widget(field),
                )
        customize_field(
            schema["custom_fields"],
            "exp__annee_diplome",
            typ=colander.Int(),
            validator=colander.Range(1900, 3999),
        )
        customize_field(
            schema["custom_fields"],
            "exp__nb_annees",
            typ=colander.Int(),
            validator=colander.Range(0, 99),
        )
        customize_field(
            schema["custom_fields"],
            "exp__competences",
            widget=deform.widget.TextAreaWidget(),
        )


def get_add_edit_schema(request):
    """
    Build a colander schema for UserDatas add edit
    :returns: A colander schema
    """
    logger.debug("Building The userdatas add/edit schema")
    excludes = ("name", "_acl", "user_id", "custom_fields")

    if not request.has_permission(PERMISSIONS["global.view_userdata_details"]):
        logger.debug("Not allowed to view userdatas details")

        excludes += (
            "coordonnees_birthday",
            "coordonnees_birthplace",
            "coordonnees_birthplace_zipcode",
            "coordonnees_nationality",
            "coordonnees_resident",
            "coordonnees_secu",
            "coordonnees_family_status",
            "coordonnees_children",
            "coordonnees_study_level_id",
            "social_statuses",
            "today_social_statuses",
            "statut_end_rights_date",
            "statut_handicap_allocation_expiration",
            "statut_bank_accounts",
            "statut_aid_organisms",
            "parcours_medical_visit",
            "parcours_medical_visit_limit",
        )

    schema = SQLAlchemySchemaNode(UserDatas, excludes=excludes)
    schema = add_custom_fields_to_schema(schema)
    customize_schema(schema)
    return schema


def get_list_schema():
    """
    Return a list schema for user datas
    """
    schema = BaseListsSchema().clone()

    schema["search"].title = "Nom, prénom, nom de l'activité"

    schema.insert(
        1,
        colander.SchemaNode(
            colander.Integer(),
            name="situation_antenne_id",
            title="Antenne",
            widget=get_deferred_select(AntenneOption, empty_filter_msg="Toutes"),
            validator=get_deferred_select_validator(AntenneOption),
            missing=colander.drop,
        ),
    )

    schema.insert(
        1,
        conseiller_filter_node_factory(
            name="situation_follower_id",
            title="Accompagnateur",
        ),
    )

    schema.insert(
        1,
        colander.SchemaNode(
            colander.Integer(),
            name="situation_situation",
            title="Statut",
            widget=get_deferred_select(CaeSituationOption, empty_filter_msg="Tous"),
            validator=get_deferred_select_validator(CaeSituationOption),
            missing=colander.drop,
        ),
    )

    return schema


def get_doctypes_schema(userdatas_model):
    """
    Build a form schema for doctypes registration

    :param obj userdatas_model: An instance of userdatas we're building
    the form for
    """
    registered = userdatas_model.doctypes_registrations
    node_schema = SQLAlchemySchemaNode(UserDatasSocialDocTypes)
    node_schema.widget = deform.widget.MappingWidget(template="clean_mapping.pt")
    node_schema["status"].widget = deform.widget.CheckboxWidget(toggle=False)

    form_schema = colander.Schema()
    for index, entry in enumerate(registered):
        node = node_schema.clone()
        name = "node_%s" % index
        node.name = name
        node.title = ""
        node["status"].title = ""
        node["status"].label = entry.doctype.label
        node["status"].arialabel = ""
        form_schema.add(node)

    return form_schema
