from .permissions import PERMISSIONS

CATEGORIES = {
    "Général": "Général",
    "Comptabilité": "Comptabilité",
    "Gestion commerciale": "Gestion commerciale",
    "Gestion sociale": "Gestion sociale",
    "Accompagnement": "Accompagnement",
    "Formation": "Formation",
}

ACCESS_RIGHTS = {
    # PAGE CONFIGURATION
    "global_config_accounting": {
        "label": "Configurer la comptabilité",
        "description": (
            "Configurer les comptes comptables, la numérotation des documents, "
            "les options d’exports d’écritures, "
            "les états de gestion… "
        ),
        "name": "global_config_accounting",
        "global_permissions": [
            PERMISSIONS["global.config_accounting"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["comptabilité", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
    },
    "global_config_sale": {
        "label": "Configurer les ventes",
        "description": (
            "Configurer les mentions des devis et factures, les unités de "
            "vente, la sortie PDF des documents (Devis, Factures, Avoirs), "
            "le cycle d’affaires… "
        ),
        "name": "global_config_sale",
        "global_permissions": [
            PERMISSIONS["global.config_sale"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["ventes", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_config_supply": {
        "label": "Configurer les fournisseurs",
        "description": ("Configurer les différentes options d’achats fournisseur. "),
        "name": "global_config_supply",
        "global_permissions": [
            PERMISSIONS["global.config_supply"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["fournisseurs", "achats", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_config_userdatas": {
        "label": "Configurer la Gestion sociale",
        "description": ("Configurer le module de Gestion sociale. "),
        "name": "global_config_userdatas",
        "global_permissions": [
            PERMISSIONS["global.config_userdatas"],
            PERMISSIONS["global.access_admin"],
        ],
        "rgpd": True,
        "tags": ["gestion sociale", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_rgpd_management": {
        "name": "global_rgpd_management",
        "label": "Responsable RGPD",
        "description": "Configurer les alertes RGPD et anonymiser les Clients",
        "global_permissions": [
            PERMISSIONS["global.rgpd_management"],
            PERMISSIONS["global.access_admin"],
        ],
        "rgpd": True,
        "tags": ["rgpd", "configuration", "gestion sociale", "ventes"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_config_accounting_measure": {
        "label": "Configurer les états de gestion",
        "description": (
            "Configurer les différents états de gestion "
            "(Trésorerie, Comptes de résultats, Balances). "
        ),
        "name": "global_config_accounting_measure",
        "global_permissions": [
            PERMISSIONS["global.config_accounting_measure"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["états de gestion", "configuration", "comptabilité"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
    },
    "global_config_cae": {
        "label": "Configurer les informations générales",
        "description": ("Configurer les informations générales relatives à la CAE. "),
        "name": "global_config_cae",
        "global_permissions": [
            PERMISSIONS["global.config_cae"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["CAE", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Général"],
    },
    "global_config_company": {
        "label": "Configurer les enseignes",
        "description": (
            "Configurer les informations relatives aux enseignes "
            "(libellé, enseigne interne). "
        ),
        "name": "global_config_company",
        "global_permissions": [
            PERMISSIONS["global.config_company"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["enseignes", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Général"],
    },
    "global_config_user": {
        "label": "Configurer les rôles utilisateurs",
        "description": (
            "Configurer les rôles utilisés dans l’application. "
            "Créer des comptes administrateurs. "
        ),
        "name": "global_config_user",
        "global_permissions": [
            PERMISSIONS["global.config_user"],
            PERMISSIONS["global.add_admin"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["enseignes", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Général"],
    },
    "global_config_workshop": {
        "label": "Configurer les ateliers",
        "description": ("Configurer les données relatives aux ateliers. "),
        "name": "global_config_workshop",
        "global_permissions": [
            PERMISSIONS["global.config_accompagnement"],
            PERMISSIONS["global.config_workshop"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["ateliers", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Accompagnement"],
    },
    "global_config_activity": {
        "label": "Configurer les rendez-vous",
        "description": (
            "Configurer les données relatives aux rendez-vous d’accompagnement. "
        ),
        "name": "global_config_activity",
        "global_permissions": [
            PERMISSIONS["global.config_accompagnement"],
            PERMISSIONS["global.config_activity"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["rendez-vous", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Accompagnement"],
    },
    "global_config_competence": {
        "label": "Configurer les compétences",
        "description": ("Configurer le module de compétences. "),
        "name": "global_config_competence",
        "global_permissions": [
            PERMISSIONS["global.config_accompagnement"],
            PERMISSIONS["global.config_competence"],
            PERMISSIONS["global.access_admin"],
        ],
        "tags": ["compétences", "configuration"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Accompagnement"],
    },
    "global_config_sap": {
        "label": "Configurer le module SAP",
        "description": ("Configurer les informations spécifiques au module SAP. "),
        "name": "global_config_sap",
        "global_permissions": [
            PERMISSIONS["global.config_sap"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["sap", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_validate_invoice": {
        "label": "Valider les factures",
        "description": "Valider les factures des entrepreneurs. ",
        "name": "global_validate_invoice",
        "global_permissions": [
            PERMISSIONS["global.list_invoices"],
            PERMISSIONS["global.validate_invoice"],
            PERMISSIONS["global.access_ea"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.validate_file"],
        ],
        "tags": ["factures", "validation", "ventes"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_validate_cancelinvoice": {
        "label": "Valider les avoirs",
        "description": "Valider les avoirs des entrepreneurs. ",
        "name": "global_validate_cancelinvoice",
        "global_permissions": [
            PERMISSIONS["global.list_invoices"],
            PERMISSIONS["global.validate_cancelinvoice"],
            PERMISSIONS["global.access_ea"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.validate_file"],
        ],
        "tags": ["avoirs", "validation", "ventes"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_validate_estimation": {
        "label": "Valider les devis",
        "description": "Valider les devis des entrepreneurs. ",
        "name": "global_validate_estimation",
        "global_permissions": [
            PERMISSIONS["global.list_estimations"],
            PERMISSIONS["global.validate_estimation"],
            PERMISSIONS["global.access_ea"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.validate_file"],
        ],
        "tags": ["devis", "validation", "ventes"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_validate_supplier_invoice": {
        "label": "Valider les factures fournisseurs",
        "description": "Valider les factures fournisseurs. ",
        "name": "global_validate_supplier_invoice",
        "global_permissions": [
            PERMISSIONS["global.list_supplier_invoices"],
            PERMISSIONS["global.validate_supplier_invoice"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": [
            "factures fournisseurs",
            "validation",
            "achats",
        ],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_validate_supplier_order": {
        "label": "Valider les commandes fournisseurs",
        "description": "Valider les commandes fournisseurs. ",
        "name": "global_validate_supplier_order",
        "global_permissions": [
            PERMISSIONS["global.list_supplier_orders"],
            PERMISSIONS["global.validate_supplier_order"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["commandes fournisseurs", "validation", "achats"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_validate_expensesheet": {
        "label": "Valider les notes de dépenses",
        "description": "Valider les note de dépenses. ",
        "name": "global_validate_expensesheet",
        "global_permissions": [
            PERMISSIONS["global.list_expenses"],
            PERMISSIONS["global.validate_expensesheet"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": [
            "notes de dépenses",
            "validation",
            "frais",
            "achats",
        ],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_create_user": {
        "label": "Gérer les comptes utilisateurs",
        "description": (
            "Créer, modifier, désactiver les utilisateurs dans la CAE. "
            "Consulter les connexions des utilisateurs à l’interface. "
        ),
        "name": "global_create_user",
        "global_permissions": [
            PERMISSIONS["global.create_user"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["comptes utilisateurs", "gestion"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Général"],
    },
    "global_create_company": {
        "label": "Gérer les enseignes",
        "desription": (
            "Créer, modifier, désactiver les enseignes dans la CAE. "
            "Définir l’enseigne interne de la CAE. "
        ),
        "name": "global_create_company",
        "global_permissions": [
            PERMISSIONS["global.create_company"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["enseignes", "gestion"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Général"],
    },
    "global_company_supervisor": {
        "label": "Accéder aux informations commerciales des enseignes",
        "description": "Accéder aux informations commerciales des enseignes.",
        "name": "global_company_supervisor",
        "global_permissions": [
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["enseignes", "consultation"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_company_access_accounting": {
        "label": "Accéder aux informations comptables des enseignes",
        "description": (
            "Accéder aux états de gestion des enseignes (Compte de résultat, états de trésorerie) "
            "ainsi qu'au bulletin de salaire. "
        ),
        "name": "global_company_access_accounting",
        "tags": ["enseignes", "consultation", "comptabilité"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
        "global_permissions": [
            PERMISSIONS["global.company_view_accounting"],
            PERMISSIONS["global.company_view_salarysheet"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.access_ea"],
        ],
    },
    "global_record_payment_invoice": {
        "label": "Saisir des encaissements",
        "description": "Saisir les encaissements. ",
        "name": "global_record_payment_invoice",
        "global_permissions": [
            PERMISSIONS["global.list_payments_invoice"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["encaissements", "paiements", "ventes"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
    },
    "global_record_payment_supplier_invoice": {
        "label": "Saisir les décaissements fournisseurs",
        "description": "Saisir des décaissements sur les factures fournisseurs. ",
        "name": "global_record_payment_supplier_invoice",
        "global_permissions": [
            PERMISSIONS["global.list_payments_supplier_invoice"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["décaissements fournisseurs", "paiements", "achats"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
    },
    "global_record_payment_expensesheet": {
        "label": "Saisir les décaissements des notes de dépenses",
        "description": "Saisir des décaissements sur les notes de dépenses. ",
        "name": "global_record_payment_expensesheet",
        "global_permissions": [
            PERMISSIONS["global.list_payments_expensesheet"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": [
            "décaissements notes de dépenses",
            "paiements",
            "frais",
            "achats",
        ],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
    },
    "global_accountant": {
        "label": "Exporter les écritures comptables",
        "description": (
            "Exporter les écritures comptables, saisir "
            "les comptes produits manquant sur les documents. "
            "Personnaliser les informations comptables des enseignes. "
            "Consulter les remontées comptables, "
            "générer les états comptables. "
        ),
        "name": "global_accountant",
        "global_permissions": [
            PERMISSIONS["global.manage_accounting"],
            PERMISSIONS["global.company_view"],
            PERMISSIONS["global.generate_accounting_measures"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["écritures comptables", "export", "comptabilité", "états de gestion"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
    },
    "global_supervisor_salary": {
        "label": "Gérer les bulletin de paie déposés",
        "description": (
            "Lister les bulletins de paie déposés dans l’application. "
            "Envoyer les bulletins par mail aux entrepreneurs. "
        ),
        "name": "global_supervisor_salary",
        "global_permissions": [
            PERMISSIONS["global.view_salarysheet"],
            PERMISSIONS["global.mail_salarysheet"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["salaire", "gestion", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Comptabilité"],
    },
    "global_userdata_details": {
        "label": "Gérer la Gestion sociale",
        "description": (
            "Consulter, sans restriction, les fiches de Gestion sociale. "
            "Créer, modifier, supprimer les fiches de Gestion sociale. "
            "Créer, modifier, supprimer les documents associés à une fiche de gestion "
            "sociale. "
            "Créer, modifier, supprimer les étapes de parcours. "
        ),
        "name": "global_userdata_details",
        "global_permissions": [
            PERMISSIONS["global.view_userdata"],
            PERMISSIONS["global.view_userdata_details"],
            PERMISSIONS["global.view_userdata_files"],
            PERMISSIONS["global.edit_userdata_career"],
            PERMISSIONS["global.py3o_userdata"],
            PERMISSIONS["global.access_ea"],
        ],
        "rgpd": True,
        "tags": ["gestion sociale", "gestion", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_userdata_restricted": {
        "label": "Gérer les informations générales de la Gestion sociale",
        "description": (
            "Consulter et saisir les informations de Synthèse et les coordonnées "
            "de contact (Nom, Prénom, Adresse, Email, Numéro de téléphone) "
            "des fiches de Gestion sociale. "
            "Consulter les étapes de parcours. "
        ),
        "name": "global_userdata_restricted",
        "global_permissions": [
            PERMISSIONS["global.view_userdata"],
            PERMISSIONS["global.access_ea"],
        ],
        "rgpd": True,
        "tags": ["gestion sociale", "gestion", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_userdata_career": {
        "label": "Gérer les étapes de parcours de la Gestion sociale",
        "description": (
            "Consulter et saisir les étapes de parcours d’une fiche de la "
            "Gestion sociale. "
        ),
        "name": "global_userdata_career",
        "global_permissions": [
            PERMISSIONS["global.view_userdata"],
            PERMISSIONS["global.edit_userdata_career"],
            PERMISSIONS["global.access_ea"],
        ],
        "rgpd": True,
        "tags": ["gestion sociale", "gestion", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_userdata_py3o": {
        "label": "Générer des documents depuis une fiche de Gestion sociale",
        "description": (
            "Générer les documents depuis les fiches de Gestion sociale à "
            "l’aide de la fusion documentaire. "
            "Consulter les informations générales de la Gestion sociale. "
        ),
        "name": "global_userdata_py3o",
        "global_permissions": [
            PERMISSIONS["global.view_userdata"],
            PERMISSIONS["global.py3o_userdata"],
            PERMISSIONS["global.access_ea"],
        ],
        "rgpd": True,
        "tags": ["gestion sociale", "gestion", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_accompagnement": {
        "label": "Gérer les rendez-vous, les ateliers et les compétences",
        "description": (
            "Consulter et créer des rendez-vous entrepreneurs. "
            "Consulter et créer des ateliers au sein de la CAE. "
            "Saisir les compétences entreprenariales. "
        ),
        "name": "global_accompagnement",
        "global_permissions": [
            PERMISSIONS["global.manage_activity"],
            PERMISSIONS["global.manage_workshop"],
            PERMISSIONS["global.manage_competence"],
            PERMISSIONS["global.manage_accompagnement"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["rendez-vous", "ateliers", "compétences", "accompagnement"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Accompagnement"],
    },
    "global_dataqueries": {
        "label": "Utiliser le module de requêtes statistiques",
        "description": (
            "Utiliser le module de requêtes statistiques et aux données de "
            "Gestion sociale extraites par ces requêtes. "
        ),
        "name": "global_dataqueries",
        "global_permissions": [
            PERMISSIONS["global.view_dataquery"],
            PERMISSIONS["global.access_ea"],
        ],
        "rgpd": True,
        "tags": ["statistiques", "export", "gestion sociale"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_supervisor_training": {
        "label": "Gérer l’activité de formation",
        "description": (
            "Gérer le statut formateur d’un entrepreneur. "
            "Gérer les fiches formateurs. "
            "Exporter les informations liées aux formations (BPF). "
            "Consulter les formations de la CAE. "
        ),
        "name": "global_supervisor_training",
        "global_permissions": [
            PERMISSIONS["global.view_training"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["formation"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "global_view_holidays": {
        "label": "Gérer les congés des entrepreneurs",
        "description": "Consulter et gérer les congés des entrepreneurs. ",
        "name": "global_view_holidays",
        "global_permissions": [
            PERMISSIONS["global.view_holidays"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["congés", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion sociale"],
    },
    "global_supervisor_sap": {
        "label": "Gérer le service à la personne (SAP)",
        "description": (
            "Consulter et générer les attestations. Consulter les stats Nova. "
        ),
        "name": "global_supervisor_sap",
        "global_permissions": [
            PERMISSIONS["global.view_sap"],
            PERMISSIONS["global.access_ea"],
        ],
        "tags": ["sap", "rh"],
        "account_type": "equipe_appui",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_validate_estimation": {
        "label": "Auto-valider ses devis",
        "description": (
            "L’entrepreneur peut auto-valider ses devis "
            "(Un montant maximum peut être spécifié). "
        ),
        "name": "es_validate_estimation",
        "global_permissions": [],
        "tags": ["validation", "devis", "ventes"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_validate_invoice": {
        "label": "Auto-valider ses factures",
        "description": (
            "L’entrepreneur peut auto-valider ses factures "
            "(Un montant maximum peut être spécifié). "
        ),
        "name": "es_validate_invoice",
        "global_permissions": [],
        "tags": ["validation", "factures", "ventes"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_validate_cancelinvoice": {
        "label": "Auto-valider ses avoirs",
        "description": ("L’entrepreneur peut auto-valider ses avoirs. "),
        "name": "es_validate_cancelinvoice",
        "global_permissions": [],
        "tags": ["validation", "avoirs", "ventes"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_validate_supplier_order": {
        "label": "Auto-valider ses commandes fournisseurs",
        "description": (
            "L’entrepreneur peut auto-valider ses commandes fournisseurs "
            "(Un montant maximum peut être spécifié)."
        ),
        "name": "es_validate_supplier_order",
        "global_permissions": [],
        "tags": ["validation", "commandes fournisseurs", "achats"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_validate_supplier_invoice": {
        "label": "Auto-valider ses factures fournisseurs",
        "description": (
            "L’entrepreneur peut auto-valider ses factures fournisseurs "
            "(Un montant maximum peut être spécifié)."
        ),
        "name": "es_validate_supplier_invoice",
        "global_permissions": [],
        "tags": ["validation", "factures fournisseurs", "achats"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_record_payment_invoice": {
        "label": "Gérer ses propres encaissements",
        "description": (
            "L’entrepreneur peut saisir, modifier ou supprimer "
            "les encaissements de ses factures de ventes."
        ),
        "name": "es_record_payment_invoice",
        "global_permissions": [],
        "tags": ["paiements", "factures", "ventes"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_trainer": {
        "label": "Gérer des formations",
        "description": (
            "Créer des affaires de type formation. "
            "Saisir des BPFs. "
            "Gérer ses propres ateliers. "
            "Renseigner sa fiche formateur."
        ),
        "name": "es_trainer",
        "global_permissions": [],
        "tags": ["formations"],
        "account_type": "all",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_constructor": {
        "label": "Gérer des chantiers",
        "description": ("Créer des affaires de type chantier."),
        "name": "es_constructor",
        "global_permissions": [],
        "tags": ["chantiers", "bâtiment"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_cancel_resulted_invoice": {
        "label": "Créer des avoirs sur des factures soldées",
        "description": ("Créer des avoirs sur des factures soldées. "),
        "name": "es_cancel_resulted_invoice",
        "global_permissions": [],
        "tags": ["avoirs", "ventes"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
    "es_no_invoice_without_estimation": {
        "label": "Ne peut pas créer de factures sans devis",
        "description": (
            "Les factures peuvent uniquement être créées depuis un devis validé. "
        ),
        "name": "es_no_invoice_without_estimation",
        "global_permissions": [],
        "tags": ["devis", "ventes"],
        "account_type": "entrepreneur",
        "category": CATEGORIES["Gestion commerciale"],
    },
}
