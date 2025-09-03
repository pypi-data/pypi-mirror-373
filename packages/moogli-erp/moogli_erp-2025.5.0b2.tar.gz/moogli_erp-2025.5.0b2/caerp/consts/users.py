from caerp.consts.access_rights import ACCESS_RIGHTS

ACCOUNT_TYPES = {
    "equipe_appui": "equipe_appui",
    "entrepreneur": "entrepreneur",
    "hybride": "hybride",
}
ACCOUNT_TYPES_LABELS = {
    "equipe_appui": "Équipe d'appui",
    "entrepreneur": "Entrepreneur",
    "hybride": "Hybride",
}

PREDEFINED_GROUPS = (
    {
        "name": "admin",
        "label": "Administrateur de l’application",
        "account_type": ACCOUNT_TYPES["equipe_appui"],
        "access_rights": [
            access_right
            for access_right in ACCESS_RIGHTS.values()
            if access_right["account_type"] == "equipe_appui"
        ],
        "editable": False,
    },
    {
        "name": "rgpd",
        "label": "Responsable du RGPD",
        "account_type": ACCOUNT_TYPES["equipe_appui"],
        "access_rights": [
            ACCESS_RIGHTS["global_rgpd_management"],
            ACCESS_RIGHTS["global_userdata_details"],
            ACCESS_RIGHTS["global_company_supervisor"],
        ],
        "editable": True,
    },
    {
        "name": "accounting",
        "label": "Comptable",
        "account_type": ACCOUNT_TYPES["equipe_appui"],
        "access_rights": [
            ACCESS_RIGHTS["global_config_accounting"],
            ACCESS_RIGHTS["global_config_sale"],
            ACCESS_RIGHTS["global_config_supply"],
            ACCESS_RIGHTS["global_accountant"],
            ACCESS_RIGHTS["global_validate_invoice"],
            ACCESS_RIGHTS["global_validate_cancelinvoice"],
            ACCESS_RIGHTS["global_validate_estimation"],
            ACCESS_RIGHTS["global_validate_supplier_order"],
            ACCESS_RIGHTS["global_validate_supplier_invoice"],
            ACCESS_RIGHTS["global_validate_expensesheet"],
            ACCESS_RIGHTS["global_record_payment_invoice"],
            ACCESS_RIGHTS["global_record_payment_supplier_invoice"],
            ACCESS_RIGHTS["global_record_payment_expensesheet"],
            ACCESS_RIGHTS["global_company_supervisor"],
            ACCESS_RIGHTS["global_company_access_accounting"],
            ACCESS_RIGHTS["global_supervisor_salary"],
        ],
        "editable": True,
    },
    {
        "name": "contractor",
        "label": "Entrepreneur",
        "default_for_account_type": True,
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [],
        "editable": True,
    },
    {
        "name": "estimation_validation",
        "label": "Entrepreneur pouvant valider ses propres devis",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_validate_estimation"],
        ],
        "editable": True,
    },
    {
        "name": "invoice_validation",
        "label": "Entrepreneur pouvant valider ses propres factures",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_validate_invoice"],
        ],
        "editable": True,
    },
    {
        "name": "cancelinvoice_validation",
        "label": "Entrepreneur pouvant valider ses propres factures d'avoir",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_validate_cancelinvoice"],
        ],
        "editable": True,
    },
    {
        "name": "estimation_only",
        "label": "Entrepreneur ne pouvant pas créer de factures sans devis",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_no_invoice_without_estimation"],
        ],
        "editable": True,
    },
    {
        "name": "supplier_order_validation",
        "label": "Entrepreneur pouvant valider ses propres commandes fournisseur",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_validate_supplier_order"],
        ],
        "editable": True,
    },
    {
        "name": "supplier_invoice_validation",
        "label": "Entrepreneur pouvant valider ses propres factures fournisseur",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_validate_supplier_invoice"],
        ],
        "editable": True,
    },
    {
        "name": "payment_admin",
        "label": "Entrepreneur pouvant saisir/modifier/supprimer les paiements de ses factures",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_record_payment_invoice"],
        ],
        "editable": True,
    },
    {
        "name": "trainer",
        "label": "Formateur",
        "account_type": "all",
        "access_rights": [ACCESS_RIGHTS["es_trainer"]],
        "editable": True,
    },
    {
        "name": "constructor",
        "label": "Entrepreneur pouvant initier des chantiers",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_constructor"],
        ],
        "editable": True,
    },
    {
        "name": "cancel_resulted_invoice",
        "label": "Entrepreneur pouvant faire des avoirs sur des factures soldées",
        "account_type": ACCOUNT_TYPES["entrepreneur"],
        "access_rights": [
            ACCESS_RIGHTS["es_cancel_resulted_invoice"],
        ],
        "editable": True,
    },
)
