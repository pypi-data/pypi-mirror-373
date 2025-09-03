"""
    Form schemes for administration
"""

import colander
import logging
from typing import Type
import simplejson as json
import deform

from colanderalchemy import SQLAlchemySchemaNode

from caerp.consts.rgpd import (
    RGPD_DEFAULT_CUSTOMER_RETENTION_DAYS,
    RGPD_DEFAULT_LOGIN_RETENTION_DAYS,
    RGPD_DEFAULT_USERDATA_RETENTION_DAYS,
)
from caerp.models.config import Config
from caerp.models.competence import (
    CompetenceScale,
)
from caerp.models.options import ConfigurableOption
from caerp.models.accounting.treasury_measures import TreasuryMeasureType
from caerp.models.sale_product import SaleProductTraining
from caerp.models.sale_product.training import SaleProductVAE
from caerp.models.task.services.invoice_official_number import (
    InvoiceNumberService,
)
from caerp.models.task.estimation import PAYMENTDISPLAYCHOICES
from caerp.models.expense.services import (
    ExpenseSheetNumberService,
)
from caerp.models.supply.services.supplierinvoice_official_number import (
    SupplierInvoiceNumberService,
    InternalSupplierInvoiceNumberService,
)
from caerp import consts, forms
from caerp.forms.files import ImageNode, get_file_upload_preparer
from caerp.forms.widgets import CleanMappingWidget, CleanSequenceWidget
from caerp.utils.accounting import ACCOUNTING_SOFTWARES
from caerp.utils.image import ImageResizer
from caerp.utils.strings import (
    get_keys_from_template,
    safe_ascii_str,
)


log = logging.getLogger(__name__)


FILE_RESIZER = ImageResizer(1000, 1000)


def get_number_template_validator(number_service):
    def validator(node, value):
        try:
            number_service.validate_template(value)
        except ValueError as e:
            raise colander.Invalid(node, str(e))

    return validator


def get_injectable_fields_validator(model_class):
    """
    :param model_class: an object having a __injectable_fields__  attr containing a list of string
    """
    try:
        valid_keys = set(model_class.__injectable_fields__)
    except AttributeError:
        raise ValueError("klass arg must have an __injectable_fields attr")

    def validator(node, value):
        try:
            template_keys = set(get_keys_from_template(value))
        except ValueError as e:
            raise colander.Invalid(
                node,
                f'Erreur dans la syntaxe du gabarit (accolade non refermée ?). Erreur brute : "{str(e)}" ',
            )
        else:
            invalid_keys = template_keys - valid_keys
            if invalid_keys:
                raise colander.Invalid(
                    node,
                    "Clefs non valides dans le gabarit : {}".format(
                        ", ".join(f"{{{k}}}" for k in invalid_keys)
                    ),
                )

    return validator


def get_help_for_injectable_fields(model_class) -> str:
    """
    Formats a nice fold-able <details> with all valid keys

    Given a class defining a __injectable_fields__ str list, formats a nice HTML
    :param model_class: : a class
    :returns: HTML code
    """

    injectable_fields = getattr(model_class, "__injectable_fields__", [])

    return """
    <details>
      <summary>
        Cliquer pour voir les champs injectables dans le gabarit 
      </summary>
      <ul>
        {}
      </ul>
    </details>
    """.format(
        "\n".join(f"<li><code>{{{field}}}</code></li>" for field in injectable_fields)
    )


@colander.deferred
def help_text_libelle_comptable(*args):
    """
    Hack to allow dynamic content in a description field description.
    """
    base = (
        "Les variables disponibles pour la génération des écritures sont décrites en"
        " haut de page."
    )
    maxlength = Config.get_value("accounting_label_maxlength", None)
    if maxlength:
        return (
            "{} NB : les libellés sont tronqués à ".format(base)
            + "{} caractères au moment de l'export.".format(maxlength)
            + "Il est possible de changer cette taille dans  "
            + "Configuration → Logiciel de comptabilité."
        )
    else:
        return base


def validate_pdf_filename_template(node, value):
    if "{numero}" not in value:
        raise colander.Invalid(node, "Le nom doit contenir le {numero} du document")


CONFIGURATION_KEYS = {
    "sale_pdf_filename_template": {
        "title": "Nom du fichier PDF",
        "description": (
            "Nom du fichier PDF qui sera téléchargé par l'utilisateur (sans le .pdf)"
        ),
        "validator": validate_pdf_filename_template,
    },
    "coop_cgv": {
        "title": "Conditions générales de vente",
        "description": (
            "Les conditions générales sont placées en dernière page des documents"
            " (devis/factures/avoirs). <br /> "
            "Il est possible de définir des CGV spécifiques à un type d'affaire, qui prendront le pas sur celles-ci, dans "
            "<a href='/admin/sales/business_cycle/business_types'>"
            "Module Ventes ➡ Cycle d'affaires ➡ Types d'affaire"
            "</a>"
        ),
        "widget": forms.richtext_widget(admin=True),
    },
    "coop_pdffootertitle": {
        "title": "Titre du pied de page",
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    "coop_pdffootertext": {
        "title": "Contenu du pied de page",
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    "coop_pdffootercourse": {
        "title": "Pied de page spécifique aux formations",
        "description": (
            "Ce contenu ne s'affiche que sur les documents liés à des formations"
        ),
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    "coop_estimationheader": {
        "title": "Cadre d’information spécifique (en en-tête des devis)",
        "description": (
            "Permet d’afficher un texte avant la description des prestations ex : <span"
            " color='red'>Le RIB a changé</span>"
        ),
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    "coop_invoiceheader": {
        "title": "Cadre d’information spécifique (en en-tête des factures)",
        "description": (
            "Permet d’afficher un texte avant la description des prestations ex : <span"
            " color='red'>Le RIB a changé</span>"
        ),
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    "cae_admin_mail": {
        "title": "Adresse e-mail de contact pour les notifications MoOGLi",
        "description": (
            "Les e-mails de notifications (par ex : retour "
            "sur le traitement de fichiers de trésorerie "
            ") sont envoyés à cette adresse"
        ),
        "validator": forms.mail_validator(),
    },
    "rgpd_manager_email": {
        "title": "Adresse e-mail du responsable RGPD",
        "description": (
            "Les e-mails de notification RGPD sont envoyés " "à cette adresse"
        ),
        "validator": forms.mail_validator(),
    },
    "rgpd_userdatas_retention_days": {
        "title": "Durée de conservation des données de gestion sociale (en jours)",
        "description": (
            "Durée en jours de conservation des données de gestion sociale "
            "après le départ de l'entrepreneur. <b>"
            f"{RGPD_DEFAULT_USERDATA_RETENTION_DAYS} jours par défaut</b>"
        ),
        "type": colander.Int(),
        "validator": colander.Range(min=0),
        "default": RGPD_DEFAULT_USERDATA_RETENTION_DAYS,
    },
    "rgpd_accounts_retention_days": {
        "title": "Durée de conservation d'un compte inutilisé (en jours)",
        "description": (
            "Durée en jours après laquelle un compte est considéré comme inutilisé. "
            f"<b>{RGPD_DEFAULT_LOGIN_RETENTION_DAYS} jours par défaut.</b>"
        ),
        "type": colander.Int(),
        "validator": colander.Range(min=0),
        "default": RGPD_DEFAULT_LOGIN_RETENTION_DAYS,
    },
    "rgpd_customers_retention_days": {
        "title": "Durée de conservation des données des clients particuliers (en jours)",
        "description": (
            "Durée en jours de conservation des données des clients particuliers "
            "après la fin de la relation commerciale. <b>"
            f"{RGPD_DEFAULT_CUSTOMER_RETENTION_DAYS} jours par défaut</b>"
        ),
        "type": colander.Int(),
        "validator": colander.Range(min=0),
        "default": RGPD_DEFAULT_CUSTOMER_RETENTION_DAYS,
    },
    "receipts_active_tva_module": {
        "title": "",
        "label": "Activer le module TVA pour les encaissements",
        "description": (
            "Inclue les écritures pour le paiement de la TVA sur encaissement"
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "receipts_grouping_strategy": {
        "title": "Grouper les écritures d'encaissement par n° de remise en banque",
        "widget": deform.widget.RadioChoiceWidget(
            values=(
                ("", "Non"),
                ("remittance_id", "Grouper par n° de remise identique"),
                (
                    "remittance_id+code_analytique",
                    "Grouper par n° de remise identique ET code analytique identique",
                ),
            )
        ),
        "description": (
            "Groupe en une écriture les encaissements (débit banque) d'une "
            "même remise en banque, en préservant ou non des écritures "
            "différentes par code analytique."
        ),
    },
    "companies_label_add_user_name": {
        "title": "",
        "label": "Ajouter le nom des entrepreneurs à la suite du nom des enseignes ?",
        "description": (
            "Si activé, affichera automatiquement le nom de l'entrepreneur à la suite "
            "du nom de l'enseigne dans les pages à destination de l'équipe d'appui."
            "<br /><br /><strong>NB : </strong><br /> "
            "- Si le nom de l'entrepreneur est déjà présent dans le nom de l'enseigne "
            "il ne sera pas ajouté.<br />"
            "- Si plusieurs entrepreneurs sont associés à l'enseigne le nombre "
            "d'entrepreneurs sera affiché plutôt que les noms.<br />"
            "- Cette option ne modifie pas l'affichage dans les documents.<br />"
            "- Cette option ne modifie pas l'affichage pour les entrepreneurs."
        ),
        "section": "Désignation des enseignes",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    # Configuration comptables ventes
    "code_journal": {
        "title": "Code journal ventes",
        "description": "Le code du journal dans votre logiciel de comptabilité",
    },
    "numero_analytique": {
        "title": "Numéro analytique de la CAE",
    },
    "compte_frais_annexes": {
        "title": "Compte de frais annexes",
    },
    "compte_cg_banque": {
        "title": "Compte banque de l'entrepreneur",
    },
    "compte_rrr": {
        "title": "Compte RRR",
        "description": "Compte Rabais, Remises et Ristournes",
        "section": "Configuration des comptes RRR",
    },
    "compte_cg_tva_rrr": {
        "title": "Compte CG de TVA spécifique aux RRR",
        "description": "",
        "section": "Configuration des comptes RRR",
    },
    "code_tva_rrr": {
        "title": "Code de TVA spécifique aux RRR",
        "description": "",
        "section": "Configuration des comptes RRR",
    },
    "bookentry_facturation_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Module Facturation",
    },
    "compte_rg_interne": {
        "title": "Compte CG RG Interne",
        "description": "",
        "section": "Module RG Interne",
    },
    "compte_rg_externe": {
        "title": "Compte CG RG Client",
        "description": "",
        "section": "Module RG Client",
    },
    "taux_rg_interne": {
        "title": "Taux RG Interne",
        "description": "(nombre entre 0 et 100) Requis pour les écritures RG Interne",
        "section": "Module RG Interne",
    },
    "taux_rg_client": {
        "title": "Taux RG Client",
        "description": (
            "(nombre entre 0 et 100) Requis pour le module d'écriture RG Client"
        ),
        "section": "Module RG Client",
    },
    "cae_general_customer_account": {
        "title": "Compte client général de la CAE",
        "description": (
            "Pour tous les clients de toutes les enseignes. une "
            "valeur spécifique pour une enseigne peut être paramétrée au niveau "
            "de l'enseigne. une valeur spécifique à un client peut être paramétrée"
            " dans chaque fiche client"
        ),
        "section": "Configuration des comptes clients",
    },
    "cae_third_party_customer_account": {
        "title": "Compte client tiers de la CAE",
        "description": (
            "Pour tous les clients de toutes les enseignes. "
            "une valeur spécifique pour une enseigne peut être paramétrée au "
            "niveau de l'enseigne. une valeur spécifique à un client peut être "
            "paramétrée dans chaque fiche client"
        ),
        "section": "Configuration des comptes clients",
    },
    # Commun facturation / facturation interne
    "bookentry_sales_group_customer_entries": {
        "title": "",
        "label": "Grouper les écritures client d'une même facture",
        "description": "Une ligne unique de débit client (typiquement 411XX) facture.",
        "section": "Groupage des lignes d'export",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "bookentry_sales_customer_account_by_tva": {
        "title": "",
        "label": "Utiliser des comptes clients par taux de TVA dans les exports",
        "description": "ATTENTION : si activé les comptes clients utilisés dans les \
            exports seront uniquement ceux configurés au niveau des taux de TVA \
            (ceux configurés au niveau de la structure, des enseignes, ou des clients \
            seront ignorées) ; si désactivé ceux configurés au niveau des taux de TVA \
            seront ignorées.",
        "section": "Paramétrage des comptes",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    # Comptes de résultats
    "income_statement_default_show_decimals": {
        "title": "",
        "label": "Afficher les décimales",
        "description": (
            "Afficher par défaut les décimales des montants du compte de résultat."
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "income_statement_default_show_zero_rows": {
        "title": "",
        "label": "Afficher les lignes à zéro",
        "description": (
            "Afficher par défaut les lignes ne contenant que des zéros dans le compte"
            "de résultat."
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    # Facturation interne
    "internalcode_journal": {
        "title": "Code journal ventes",
        "description": "Le code du journal dans votre logiciel de comptabilité",
    },
    "internalcode_journal_encaissement": {
        "title": "Code journal pour les encaissements des factures internes",
        "description": "Le code du journal dans votre logiciel de comptabilité",
        "section": "Facturation interne",
    },
    "internalbank_general_account": {
        "title": (
            "Compte général de banque à utiliser pour les encaissements "
            "des factures internes (ventes et fournisseurs)"
        ),
        "description": "Le code du journal dans votre logiciel de comptabilité",
        "section": "Facturation interne",
    },
    "internalnumero_analytique": {
        "title": "Numéro analytique de la CAE",
    },
    "internalcompte_frais_annexes": {
        "title": "Compte de frais annexes",
    },
    "internalcompte_cg_banque": {
        "title": "Compte banque de l'entrepreneur",
    },
    "internalbookentry_facturation_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Module Facturation",
    },
    "internalcompte_rrr": {
        "title": "Compte RRR",
        "description": "Compte Rabais, Remises et Ristournes",
        "section": "Configuration des comptes RRR",
    },
    "internalcae_general_customer_account": {
        "title": "Compte client général de la CAE pour les clients internes",
        "description": (
            "Pour tous les clients internes de toutes les enseignes. une valeur"
            " spécifique pour une enseigne peut être paramétrée au niveau de"
            " l'enseigne. une valeur spécifique à un client peut être"
            " paramétrée dans chaque fiche client"
        ),
        "section": "Configuration des comptes clients internes",
    },
    "internalcae_third_party_customer_account": {
        "title": "Compte client tiers de la CAE pour les clients internes",
        "description": (
            "Pour tous les clients internes de toutes les "
            "enseignes. "
            "une valeur spécifique pour une enseigne peut être paramétrée au "
            "niveau de l'enseigne. une valeur spécifique à un client peut être "
            "paramétrée dans chaque fiche client"
        ),
        "section": "Configuration des comptes clients internes",
    },
    "sale_catalog_notva_mode": {
        "title": "",
        "label": "Catalogue sans produit ni TVA ?",
        "description": (
            "Permet de désactiver la configuration de la TVA et des produits "
            "comptables dans les catalogues produits (Ceux-ci sont configurés"
            " directement dans le devis/la facture)."
        ),
        "section": "Mode de saisie",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "sale_catalog_sale_product_training_taskline_template": {
        "title": "Gabarit pour les lignes de devis/facture issues des formations du catalogue",
        "description": (
            "Lorsqu'un produit du catalogue est inséré dans un devis/facture, il est possible"
            "d'injecter les champs issus du catalogue dans la description."
            + get_help_for_injectable_fields(SaleProductTraining)
        ),
        "section": "Injection des produits catalogue dans les devis/factures",
        "widget": forms.richtext_widget(admin=True),
        "validator": get_injectable_fields_validator(SaleProductTraining),
    },
    "sale_catalog_sale_product_vae_taskline_template": {
        "title": "Gabarit pour les lignes de devis/facture issues des VAEs du catalogue",
        "description": (
            "Lorsqu'un produit du catalogue est inséré dans un devis/facture, il est possible "
            "d'injecter les champs issus du catalogue dans la description."
            + get_help_for_injectable_fields(SaleProductVAE)
        ),
        "section": "Injection des produits catalogue dans les devis/factures",
        "widget": forms.richtext_widget(admin=True),
        "validator": get_injectable_fields_validator(SaleProductVAE),
    },
    "price_study_uses_contribution": {
        "title": "",
        "label": "La contribution CAE est utilisée dans les calculs",
        "description": (
            "Permet de définir si la contribution à la CAE est utilisée dans le calcul "
            "du prix HT depuis le coût d'achat"
        ),
        "section": "Mode de saisie",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "price_study_uses_insurance": {
        "title": "",
        "label": "L'assurance est utilisée dans les calculs",
        "description": (
            "Permet de définir si le taux d'assurance est utilisé dans le calcul "
            "du prix HT depuis le coût d'achat"
        ),
        "section": "Mode de saisie",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "estimation_validity_duration_default": {
        "title": "Limite de validité des devis par défaut",
        "description": (
            "Limite de validité qui sera reprise automatiquement         dans les"
            " mentions des devis si l'entrepreneur ne la modifie pas        "
            " manuellement"
        ),
        "section": "Devis",
    },
    "task_display_units_default": {
        "title": "",
        "label": (
            "Afficher le détail (prix unitaire et quantité)          des produits dans"
            " le PDF"
        ),
        "description": (
            "Cette valeur sera reprise automatiquement         dans les devis et"
            " factures si l'entrepreneur ne la modifie pas         manuellement"
        ),
        "section": "Devis et factures",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "task_display_ttc_default": {
        "title": "",
        "label": "Afficher les prix TTC dans le PDF)",
        "description": (
            "Cette valeur sera reprise automatiquement         dans les devis et"
            " factures si l'entrepreneur ne la modifie pas         manuellement"
        ),
        "section": "Devis et factures",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "estimation_payment_display_default": {
        "title": "Choix par défaut pour l'affichage des plans de paiement",
        "section": "Devis et factures",
        "widget": deform.widget.SelectWidget(values=PAYMENTDISPLAYCHOICES),
    },
    "bookentry_payment_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Encaissements",
    },
    "internalbookentry_payment_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Facturation interne",
    },
    "bookentry_rg_client_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Module RG Client",
    },
    "bookentry_rg_interne_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Module RG Interne",
    },
    "bookentry_expense_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
    },
    "bookentry_expense_payment_main_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Paiement des notes de dépenses",
    },
    "bookentry_expense_payment_waiver_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Abandon de créance",
    },
    "sage_rginterne": {
        "label": "Module RG Interne",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
        "section": "Activation des modules d’export Sage",
    },
    "sage_rgclient": {
        "label": "Module RG Client",
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
        "section": "Activation des modules d’export Sage",
    },
    "sage_facturation_not_used": {
        "label": "Module facturation",
        "description": "Activé par défaut",
        "widget": deform.widget.CheckboxWidget(template="checkbox_readonly.pt"),
        "section": "Activation des modules d’export Sage",
    },
    # NDF
    "code_journal_ndf": {
        "title": "Code journal utilisé pour les notes de dépenses",
    },
    "compte_cg_ndf": {
        "title": "Compte général (classe 4) pour les dépenses dues aux entrepreneurs",
        "description": (
            "Notes de dépense et part entrepreneur des factures fournisseur. Une valeur"
            " spécifique pour une enseigne peut être paramétrée au niveau de"
            " l'enseigne."
        ),
    },
    "ungroup_expenses_ndf": {
        "label": "Ne pas grouper les écritures dans les exports des notes de dépenses",
        "description": (
            "Si cette fonction est activée, "
            "lors de l’export comptable des notes de dépenses, pour "
            "chaque entrepreneur, une écriture par dépense sera affichée "
            "(et non pas un total par types de dépense)."
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "code_journal_waiver_ndf": {
        "title": "Code journal spécifique aux abandons de créance",
        "description": (
            "Code journal utilisé pour l'export des abandons de créance, si ce champ"
            " n'est pas rempli, le code journal d'export des notes de dépense est"
            " utilisé. Les autres exports de décaissement utilisent     le code journal"
            " de la banque concernée."
        ),
        "section": "Abandon de créance",
    },
    "compte_cg_waiver_ndf": {
        "title": "Compte abandons de créance",
        "description": (
            "Compte de comptabilité générale spécifique aux abandons de créance dans"
            " les notes de dépenses"
        ),
        "section": "Abandon de créance",
    },
    "code_tva_ndf": {
        "title": "Code TVA utilisé pour les décaissements",
        "description": "Le code TVA utilisé pour l'export des décaissements",
        "section": "Paiement des notes de dépenses",
    },
    "expensesheet_number_template": {
        "title": "Gabarit du numéro de note de dépense",
        "description": (
            "Peut contenir des caractères (préfixes, "
            "séparateurs… etc), ainsi que des variables et séquences. Ex: "
            "{YYYY}-{SEQYEAR}."
        ),
        "missing": colander.required,
        "validator": get_number_template_validator(ExpenseSheetNumberService),
    },
    "global_expensesheet_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence globale",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence globale (SEQGLOBAL)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_expensesheet_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence annuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence annuelle (SEQYEAR)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_expensesheet_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence annuelle",
        "section": "Séquence annuelle (SEQYEAR)",
        "widget": deform.widget.DateInputWidget(),
    },
    "month_expensesheet_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence mensuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence mensuelle (SEQMONTH)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "month_expensesheet_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence mensuelle",
        "section": "Séquence mensuelle (SEQMONTH)",
        "widget": deform.widget.DateInputWidget(),
    },
    "supplierinvoice_number_template": {
        "title": "Gabarit du numéro de facture fournisseur",
        "description": (
            "Peut contenir des caractères (préfixes, "
            "séparateurs… etc), ainsi que des variables et séquences. Ex: "
            "{YYYY}-{SEQYEAR}."
        ),
        "missing": colander.required,
        "validator": get_number_template_validator(SupplierInvoiceNumberService),
    },
    "global_supplierinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence globale",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence globale (SEQGLOBAL)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_supplierinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence annuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence annuelle (SEQYEAR)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_supplierinvoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence annuelle",
        "section": "Séquence annuelle (SEQYEAR)",
        "widget": deform.widget.DateInputWidget(),
    },
    "month_supplierinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence mensuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence mensuelle (SEQMONTH)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "month_supplierinvoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence mensuelle",
        "section": "Séquence mensuelle (SEQMONTH)",
        "widget": deform.widget.DateInputWidget(),
    },
    "internalsupplierinvoice_number_template": {
        "title": "Gabarit du numéro de facture fournisseur interne",
        "description": (
            "Peut contenir des caractères (préfixes, "
            "séparateurs… etc), ainsi que des variables et séquences. Ex: "
            "{YYYY}-{SEQYEAR}."
        ),
        "missing": colander.required,
        "validator": get_number_template_validator(
            InternalSupplierInvoiceNumberService
        ),
    },
    "global_internalsupplierinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence globale",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence globale (SEQGLOBAL)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_internalsupplierinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence annuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence annuelle (SEQYEAR)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_internalsupplierinvoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence annuelle",
        "section": "Séquence annuelle (SEQYEAR)",
        "widget": deform.widget.DateInputWidget(),
    },
    "month_internalsupplierinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence mensuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence mensuelle (SEQMONTH)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "month_internalsupplierinvoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence mensuelle",
        "section": "Séquence mensuelle (SEQMONTH)",
        "widget": deform.widget.DateInputWidget(),
    },
    "treasury_measure_ui": {
        "title": "Indicateur à mettre en évidence",
        "description": (
            "Indicateur qui sera mis en évidence dans l'interface entrepreneur"
        ),
        "widget": forms.get_deferred_model_select(
            TreasuryMeasureType,
            mandatory=True,
            widget_class=deform.widget.RadioChoiceWidget,
        ),
    },
    "invoice_number_template": {
        "title": "Gabarit du numéro de facture",
        "description": (
            "Peut contenir des caractères (préfixes, "
            "séparateurs… etc), ainsi que des variables et séquences. Ex: "
            "{YYYY}-{SEQYEAR}."
        ),
        "missing": colander.required,
        "validator": get_number_template_validator(InvoiceNumberService),
    },
    "allow_unchronological_invoice_sequence": {
        "label": "Autoriser une numérotation non chronologique des factures",
        "description": (
            "<strong>Attention : </strong>Si activé il sera possible de valider les "
            "factures avec une date autre que celle du jour, au risque de ne pas "
            "respecter la chronologie de la numérotation (qui est <a href='https://"
            "www.economie.gouv.fr/entreprises/factures-mentions-obligatoires#factures-"
            "quelles-sont-les-mentio_1' target='_blank'>une obligation légale</a>)."
            "<br/><br/>La CAE est pleinement responsable des conséquences de "
            "l'activation de cette option."
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "global_invoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence globale",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence globale (SEQGLOBAL)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_invoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence annuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence annuelle (SEQYEAR)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_invoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence annuelle",
        "section": "Séquence annuelle (SEQYEAR)",
        "widget": deform.widget.DateInputWidget(),
    },
    "month_invoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence mensuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence mensuelle (SEQMONTH)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "month_invoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence mensuelle",
        "section": "Séquence mensuelle (SEQMONTH)",
        "widget": deform.widget.DateInputWidget(),
    },
    "internalinvoice_number_template": {
        "title": "Gabarit du numéro de facture",
        "description": (
            "Peut contenir des caractères (préfixes, "
            "séparateurs… etc), ainsi que des variables et séquences. Ex: "
            "{YYYY}-{SEQYEAR}."
        ),
        "missing": colander.required,
        "validator": get_number_template_validator(InvoiceNumberService),
    },
    "global_internalinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence globale",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence globale (SEQGLOBAL)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_internalinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence annuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence annuelle (SEQYEAR)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_internalinvoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence annuelle",
        "section": "Séquence annuelle (SEQYEAR)",
        "widget": deform.widget.DateInputWidget(),
    },
    "month_internalinvoice_sequence_init_value": {
        "title": "Valeur à laquelle on initialise la séquence mensuelle",
        "description": "La numérotation reprendra au numéro suivant",
        "section": "Séquence mensuelle (SEQMONTH)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "month_internalinvoice_sequence_init_date": {
        "title": "Date à laquelle on initialise la séquence mensuelle",
        "section": "Séquence mensuelle (SEQMONTH)",
        "widget": deform.widget.DateInputWidget(),
    },
    "accounting_software": {
        "title": "Logiciel de comptabilité de la coopérative",
        "widget": deform.widget.SelectWidget(values=ACCOUNTING_SOFTWARES),
    },
    "accounting_label_maxlength": {
        "title": "Taille maximum des libellés d'écriture (troncature)",
        "description": (
            "MoOGLi tronquera les libellés d'écriture comptable "
            "exportés à cette longueur. Dépend de votre logiciel de comptabilité. "
            "Ex :  30 pour quadra, 35 pour sage, 25 pour ciel. Mettre à zéro "
            "pour désactiver la troncature."
        ),
        "type": colander.Int(),
    },
    "thirdparty_account_mandatory_user": {
        "label": "Activer le contrôle des comptes tiers entrepreneurs",
        "description": (
            "Les exports de notes de frais ou de paiement seronts interdits "
            "si un compte tiers n'est pas configuré pour l'entrepreneur"
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "thirdparty_account_mandatory_customer": {
        "label": "Activer le contrôle des comptes tiers clients",
        "description": (
            "Les exports de notes de frais ou de paiement seronts interdits "
            "si un compte tiers n'est pas configuré pour un client"
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "thirdparty_account_mandatory_supplier": {
        "label": "Activer le contrôle des comptes tiers fournisseurs",
        "description": (
            "Les exports de notes de frais ou de paiement seronts interdits "
            "si un compte tiers n'est pas configuré pour un fournisseur"
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
    },
    "accounting_closure_day": {
        "title": "Jour de la clôture comptable (1-31)",
        "section": "Date de la clôture comptable",
        "type": colander.Int(),
        "validator": colander.Range(1, 31),
        "missing": 31,
    },
    "accounting_closure_month": {
        "title": "Mois de la clôture comptable (1-12)",
        "section": "Date de la clôture comptable",
        "type": colander.Int(),
        "validator": colander.Range(1, 12),
        "missing": 12,
    },
    "cae_business_name": {
        "title": "Raison sociale",
        "description": "Le nom par lequel est désignée votre CAE",
    },
    "cae_legal_status": {
        "title": "Statut juridique",
    },
    "cae_address": {
        "title": "Adresse",
        "widget": deform.widget.TextAreaWidget(rows=2),
    },
    "cae_zipcode": {
        "title": "Code postal",
    },
    "cae_city": {
        "title": "Ville",
    },
    "cae_tel": {
        "title": "Téléphone",
    },
    "cae_contact_email": {
        "title": "Adresse e-mail de contact",
        "description": (
            "Adresse e-mail de contact de la CAE (sera "
            "renseignée à titre informatif dans les métadonnées des factures PDF)"
        ),
        "validator": forms.mail_validator(),
    },
    "cae_business_identification": {
        "title": "Numéro de SIRET",
        "description": (
            "Utilisé pour la génération de métadonnées Factur-X et le module avance immédiate pour le service à la personne."
        ),
    },
    "cae_intercommunity_vat": {
        "title": "Numéro de TVA intracommunautaire",
    },
    "cae_vat_collect_mode": {
        "title": "Mode de gestion de la TVA",
        "widget": deform.widget.SelectWidget(
            values=(
                ("debit", "Sur les débits"),
                ("encaissement", "Sur les encaissements"),
            )
        ),
    },
    # Facture fournisseur
    "cae_general_supplier_account": {
        "title": "Compte fournisseur général de la CAE",
        "section": "Configuration des comptes fournisseurs",
    },
    "cae_third_party_supplier_account": {
        "title": "Compte fournisseur tiers de la CAE",
        "description": (
            "Pour tous les fournissseurs de toutes les enseignes. "
            "une valeur spécifique pour une enseigne peut être paramétrée au "
            "niveau de l'enseigne. une valeur spécifique à un fournisseur "
            "peut être paramétrée dans chaque fiche fournisseur"
        ),
        "section": "Configuration des comptes fournisseurs",
    },
    "code_journal_frns": {
        "title": "Code journal utilisé pour les factures fournisseur",
        "section": "Factures fournisseur",
    },
    "ungroup_supplier_invoices_export": {
        "label": (
            "Ne pas grouper les écritures dans les exports de factures fournisseurs"
        ),
        "description": (
            "Si cette fonction est activée, lors de l’export comptable des"
            " factures fournisseurs, une écriture par ligne de la facture"
            " sera affichée (et non pas un total par types de dépense)."
        ),
        "widget": deform.widget.CheckboxWidget(true_val="1", false_val="0"),
        "section": "Factures fournisseur",
    },
    "bookentry_supplier_invoice_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "section": "Paiements des factures fournisseur",
    },
    "bookentry_supplier_payment_label_template": {
        "title": "Gabarit pour les libellés d'écriture (paiements direct fournisseur)",
        "section": "Paiements des factures fournisseur",
    },
    "bookentry_supplier_invoice_user_payment_label_template": {
        "title": "Gabarit pour les libellés d'écriture (remboursements entrepreneurs)",
        "section": "Paiements des factures fournisseur",
    },
    "bookentry_supplier_invoice_user_payment_waiver_label_template": {
        "title": (
            "Gabarit pour les libellés d'écriture (abandon de créance entrepreneur)"
        ),
        "description": help_text_libelle_comptable,
        "section": "Paiements des factures fournisseur",
    },
    # Factures fournisseur internes
    "internalcae_general_supplier_account": {
        "title": "Compte fournisseur général de la CAE",
        "section": "Configuration des comptes fournisseurs",
    },
    "internalcae_third_party_supplier_account": {
        "title": "Compte fournisseur tiers de la CAE",
        "description": (
            "Pour tous les fournissseurs de toutes les enseignes. "
            "une valeur spécifique pour une enseigne peut être paramétrée au "
            "niveau de l'enseigne. une valeur spécifique à un fournisseur "
            "peut être paramétrée dans chaque fiche fournisseur"
        ),
        "section": "Configuration des comptes fournisseurs",
    },
    "internalcode_journal_frns": {
        "title": ("Code journal utilisé pour les factures fournisseur internes"),
        "section": "Factures fournisseur",
    },
    "internalbookentry_supplier_invoice_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Factures fournisseur",
    },
    "internalcode_journal_paiements_frns": {
        "title": ("Code journal utilisé pour les paiements fournisseur internes"),
        "section": "Paiements des factures fournisseur",
    },
    "internalbookentry_supplier_payment_label_template": {
        "title": "Gabarit pour les libellés d'écriture",
        "description": help_text_libelle_comptable,
        "section": "Paiements des factures fournisseur",
    },
    "company_general_ledger_accounts_filter": {
        "title": "Liste des comptes à afficher ou cacher "
    },
    "smtp_cae_estimation_subject_template": {
        "title": "Gabarit de l’objet des e-mails pour les devis",
        "description": (
            "Les variables disponibles dans ce gabarit sont disponibles en haut "
            "de cette page."
        ),
    },
    "smtp_cae_estimation_body_template": {
        "title": "Gabarit du contenu des e-mails pour les devis",
        "description": (
            "Les variables disponibles pour la génération des écritures sont décrites "
            "en haut de page."
        ),
        "widget": deform.widget.TextAreaWidget(rows=20),
    },
    "smtp_cae_invoice_subject_template": {
        "title": "Gabarit de l’objet des e-mails pour les factures",
        "description": (
            "Les variables disponibles dans ce gabarit sont disponibles en haut "
            "de cette page."
        ),
    },
    "smtp_cae_invoice_body_template": {
        "title": "Gabarit du contenu des e-mails pour les factures",
        "description": (
            "Les variables disponibles pour la génération des écritures sont décrites "
            "en haut de page."
        ),
        "widget": deform.widget.TextAreaWidget(rows=20),
    },
}


def get_config_key_schemanode(key, ui_conf):
    """
    Returns a schema node to configure the config 'key'
    This key should appear in the dict here above CONFIGURATION_KEYS
    """
    return colander.SchemaNode(
        ui_conf.get("type", colander.String()),
        title=ui_conf.get("title", key),
        label=ui_conf.get("label", None),
        description=ui_conf.get("description"),
        missing=ui_conf.get("missing", ""),
        name=key,
        widget=ui_conf.get("widget"),
        validator=ui_conf.get("validator", None),
        default=ui_conf.get("default", colander.null),
    )


def get_config_schema(keys):
    """
    Returns a schema to configure Config objects

    :param list keys: The list of keys we want to configure (ui informations
    should be provided in the CONFIGURATION_KEYS dict

    :results: A colander Schema to configure the given keys
    :rtype: object colander Schema
    """
    schema = colander.Schema()
    mappings = {}
    index = 0
    for key in keys:
        ui_conf = CONFIGURATION_KEYS.get(key, {})
        node = get_config_key_schemanode(key, ui_conf)

        if "section" in ui_conf:  # This element should be shown in a mapping
            section_title = ui_conf["section"]
            section_name = safe_ascii_str(section_title)
            if section_name not in mappings:
                mappings[section_name] = mapping = colander.Schema(
                    title=section_title,
                    name=section_name,
                )
                schema.add(mapping)
            else:
                mapping = mappings[section_name]
            mapping.add(node)
        else:
            schema.insert(index, node)
            index += 1

    #    for mapping in mappings.values():
    #        schema.add(mapping)
    return schema


def build_config_appstruct(request, keys):
    """
    Build the configuration appstruct regarding the config keys we want to edit

    :param obj request: The pyramid request object (with a config attribute)
    :param list keys: the keys we want to edit
    :returns: A dict storing the configuration values adapted to a schema
    generated by get_config_schema
    """
    appstruct = {}
    for key in keys:
        value = request.config.get(key, "")
        if value:
            ui_conf = CONFIGURATION_KEYS[key]

            if "section" in ui_conf:
                appstruct.setdefault(safe_ascii_str(ui_conf["section"]), {})[
                    key
                ] = value
            else:
                appstruct[key] = value
    return appstruct


class ActionConfig(colander.MappingSchema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title="Sous-titre",
        description="Sous-titre dans la sortie pdf",
        validator=colander.Length(max=100),
    )


class ActivitySubActionSeq(colander.SequenceSchema):
    subaction = ActionConfig(
        title="",
        widget=CleanMappingWidget(),
    )


class ActivityActionConfig(colander.Schema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title="Titre",
        description="Titre dans la sortie pdf",
        validator=colander.Length(max=255),
    )
    children = ActivitySubActionSeq(
        title="",
        widget=CleanSequenceWidget(
            add_subitem_text_template="Ajouter un sous-titre",
        ),
    )


class ActivityActionSeq(colander.SequenceSchema):
    action = ActivityActionConfig(
        title="Titre",
        widget=CleanMappingWidget(),
    )


class WorkshopInfo3(colander.MappingSchema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title="Sous-titre 2",
        description="Sous-titre 2 dans la sortie pdf",
        validator=colander.Length(max=100),
    )


class WorkshopInfo3Seq(colander.SequenceSchema):
    child = WorkshopInfo3(
        title="Sous-titre 2",
        widget=CleanMappingWidget(),
    )


class WorkshopInfo2(colander.Schema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title="Sous-titre",
        description="Sous-titre dans la sortie pdf",
        validator=colander.Length(max=255),
    )
    children = WorkshopInfo3Seq(
        title="",
        widget=CleanSequenceWidget(
            add_subitem_text_template="Ajouter un sous-titre 2",
            orderable=True,
        ),
    )


class WorkshopInfo2Seq(colander.SequenceSchema):
    child = WorkshopInfo2(
        title="Sous-titre",
        widget=CleanMappingWidget(),
    )


class WorkshopInfo1(colander.Schema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title="Titre",
        description="Titre dans la sortie pdf",
        validator=colander.Length(max=255),
    )
    children = WorkshopInfo2Seq(
        title="",
        widget=CleanSequenceWidget(
            add_subitem_text_template="Ajouter un sous-titre",
            orderable=True,
        ),
    )


class WorkshopInfo1Seq(colander.SequenceSchema):
    actions = WorkshopInfo1(
        title="Titre",
        widget=CleanMappingWidget(),
    )


class ActivityConfigActionSchema(colander.Schema):
    """
    The schema for activity recursive actions
    """

    actions = ActivityActionSeq(
        title="Configuration des titres d'actions disponibles pour la sortie PDF",
        widget=CleanSequenceWidget(
            add_subitem_text_template="Ajouter un titre d'action",
            orderable=True,
        ),
    )


class WorkshopConfigActionSchema(colander.Schema):
    """
    The schema for workshop recursive actions
    """

    actions = WorkshopInfo1Seq(
        title="Configuration des titres disponibles pour la sortie PDF",
        widget=CleanSequenceWidget(
            add_subitem_text_template="Ajouter une titre",
            orderable=True,
        ),
    )


class AccompagnementConfigPDFSchema(colander.Schema):
    """
    The schema for activity types configuration
    """

    header_img = ImageNode(
        title="En-tête des sortie PDF",
        missing=colander.drop,
        preparer=get_file_upload_preparer([FILE_RESIZER]),
    )
    footer_img = ImageNode(
        title="Image du pied de page des sorties PDF",
        description="Vient se placer au-dessus du texte du pied de page",
        missing=colander.drop,
        preparer=get_file_upload_preparer([FILE_RESIZER]),
    )
    footer = forms.textarea_node(
        title="Texte du pied de page des sorties PDF",
        missing="",
    )


def load_filetypes_from_config(config):
    """
    Return filetypes configured in databas
    """
    attached_filetypes = json.loads(config.get("attached_filetypes", "[]"))
    if not isinstance(attached_filetypes, list):
        attached_filetypes = []
    return attached_filetypes


def get_element_by_name(list_, name):
    """
    Return an element from list_ which has the name "name"
    """
    found = None
    for element in list_:
        if element.name == name:
            found = element
    return found


def merge_config_datas(dbdatas, appstruct):
    """
    Merge the datas returned by form validation and the original dbdatas
    """
    flat_appstruct = forms.flatten_appstruct(appstruct)
    for name, value in list(flat_appstruct.items()):
        dbdata = get_element_by_name(dbdatas, name)
        if not dbdata:
            # The key 'name' doesn't exist in the database, adding new one
            dbdata = Config(name=name, value=value)
            dbdatas.append(dbdata)
        else:
            dbdata.value = value
    return dbdatas


def get_sequence_model_admin(model, title="", excludes=(), **kw):
    """
    Return a schema for configuring sequence of models

        model

            The SQLAlchemy model to configure
    """
    node_schema = SQLAlchemySchemaNode(
        model,
        widget=CleanMappingWidget(),
        excludes=excludes,
    )
    node_schema.name = "data"

    colanderalchemy_config = getattr(model, "__colanderalchemy_config__", {})

    default_widget_options = dict(
        orderable=True,
        min_len=1,
    )
    widget_options = colanderalchemy_config.get("seq_widget_options", {})
    widget_options.update(kw.get("widget_options", {}))

    for key, value in list(widget_options.items()):
        default_widget_options[key] = value

    schema = colander.SchemaNode(colander.Mapping())
    schema.add(
        colander.SchemaNode(
            colander.Sequence(),
            node_schema,
            widget=CleanSequenceWidget(**default_widget_options),
            title=title,
            name="datas",
        )
    )

    def dictify(models):
        return {"datas": [node_schema.dictify(model) for model in models]}

    def objectify(datas):
        return [node_schema.objectify(data) for data in datas]

    schema.dictify = dictify
    schema.objectify = objectify
    return schema


class SubCompetenceConfigSchema(colander.MappingSchema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title="Libellé",
    )


class SubCompetencesConfigSchema(colander.SequenceSchema):
    subcompetence = SubCompetenceConfigSchema(
        widget=CleanMappingWidget(),
    )


class CompetenceRequirement(colander.MappingSchema):
    deadline_id = forms.id_node()
    deadline_label = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(readonly=True),
        title="Pour l'échéance",
        missing=colander.drop,
    )
    scale_id = colander.SchemaNode(
        colander.Integer(),
        title="Niveau requis",
        description="Sera mis en évidence dans l'interface",
        widget=forms.get_deferred_select(CompetenceScale),
    )


class CompetenceRequirementSeq(colander.SequenceSchema):
    requirement = CompetenceRequirement(
        title="",
        widget=CleanMappingWidget(),
    )


@colander.deferred
def deferred_seq_widget(nodex, kw):
    elements = kw["deadlines"]
    return CleanSequenceWidget(
        add_subitem_text_template="-",
        min_len=len(elements),
        max_len=len(elements),
    )


@colander.deferred
def deferred_deadlines_default(node, kw):
    """
    Return the defaults to ensure there is a requirement for each configured
    deadline
    """
    return [
        {
            "deadline_label": deadline.label,
            "deadline_id": deadline.id,
        }
        for deadline in kw["deadlines"]
    ]


class CompetencePrintConfigSchema(colander.Schema):
    header_img = ImageNode(
        title="En-tête de la sortie imprimable",
        preparer=get_file_upload_preparer([FILE_RESIZER]),
    )


def get_admin_schema(factory):
    """
    Return an edit schema for the given factory

    :param obj factory: A SQLAlchemy model
    :returns: A SQLAlchemySchemaNode schema
    :rtype: class:`SQLAlchemySchemaNode`
    """
    schema = SQLAlchemySchemaNode(factory)
    return schema


def get_admin_configurable_option_schema(
    factory: Type[ConfigurableOption],
) -> SQLAlchemySchemaNode:
    """
    Return an add/edit schema for a factory that is a subclass of the
    ConfigurableOption model
    """
    schema = SQLAlchemySchemaNode(factory, includes=("label",))
    forms.customize_field(schema, "label", title="Libellé")
    return schema
