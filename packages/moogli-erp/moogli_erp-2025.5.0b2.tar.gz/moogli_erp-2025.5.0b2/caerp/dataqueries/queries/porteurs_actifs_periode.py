from datetime import date

from caerp.dataqueries.base import BaseDataQuery
from caerp.models.user.userdatas import STATUS_OPTIONS
from caerp.models.user.utils import (
    get_active_custom_fields_labels,
    get_active_custom_fields_names,
    get_all_userdatas_active_on_period,
    get_custom_field_value_string,
    get_ongoing_parcours,
    get_social_statuses_label,
    get_tuple_option_label,
    get_user_analytical_accounts,
    get_userdatas_cae_situation,
    get_userdatas_seniority,
)
from caerp.utils.dataqueries import dataquery_class


@dataquery_class()
class ActiveESQuery(BaseDataQuery):
    name = "porteurs_actifs_periode"
    label = "Détail des porteurs actifs sur une période"
    description = """
    <p>Liste de tous les porteurs de projets actifs sur la période choisie avec un 
    maximum d'informations.</p>
    <br/>
    <p>Un porteur de projet est considéré comme actif si :<ul>
    <li>sa date d'entrée <em>(date de la première étape de parcours de type 
    "Entrée CAE", généralement un CAPE)</em> est avant la fin de la période</li>
    <li>sa date de sortie <em>(date de la dernière étape de parcours de type 
    "Sortie CAE")</em> n'existe pas ou est après la début de la période</li>
    </ul></p>
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "Identifiant interne",
            "Code(s) analytique(s)",
            "Civilité",
            "Nom",
            "Nom de naissance",
            "Prénom",
            "Situation actuelle dans la CAE",
            "Antenne de rattachement",
            "Accompagnateur",
            "Date info coll",
            "Date d'entrée dans la CAE",
            "Ancienneté (en mois)",
            "Date de contrat",
            "Date d'entrée au sociétariat",
            "Prescripteur",
            "Nom du prescripteur",
            "-----",
            "E-mail 1",
            "E-mail 2",
            "Tél. fixe",
            "Tél. mobile",
            "Adresse",
            "Code postal",
            "Ville",
            "Zone d'habitation",
            "Qualification de la zone d'habitation",
            "Sexe",
            "Date de naissance",
            "Age",
            "Lieu de naissance",
            "Code postal du lieu de naissance",
            "Nationalité",
            "Fin de validité de la carte de séjour",
            "-----",
            "Numéro de sécurité sociale",
            "Situation familiale",
            "Nombre d'enfants",
            "Niveau d'études",
            "Contact urgent : Nom",
            "Contact urgent : Téléphone",
            "Statut social à l'entrée",
            "Statut social actuel",
            "Date de fin de droit",
            "Allocation adulte handicapé - échéance",
            "Date de la visite médicale",
            "Date limite de la visite médicale",
            "Résultat de la visite médicale",
            "Objectifs",
            "Typologie d'activité",
            "-----",
        ]
        for custom_field_label in get_active_custom_fields_labels():
            headers.append(custom_field_label)
        headers += [
            "-----",
            "Motif de non admission en CAE",
            "Date de sortie",
            "Type de sortie",
            "Motif de sortie",
            "-----",
            "ID Utilisateur",
            "ID Gestion sociale",
            "Créé(e) le",
            "Mis(e) à jour le",
        ]
        return headers

    def data(self):
        data = []
        active_users = get_all_userdatas_active_on_period(
            self.start_date, self.end_date
        )
        for u in active_users:
            cae_situation = get_userdatas_cae_situation(u.id, self.end_date)
            parcours = get_ongoing_parcours(u.id, self.end_date)
            user_data = [
                u.coordonnees_identifiant_interne,
                get_user_analytical_accounts(u.user_id),
                u.coordonnees_civilite,
                u.coordonnees_lastname,
                u.coordonnees_ladies_lastname,
                u.coordonnees_firstname,
                cae_situation.label if cae_situation else "",
                u.situation_antenne.label if u.situation_antenne else "",
                u.situation_follower.label if u.situation_follower else "",
                self.date_tools.format_date(u.parcours_date_info_coll),
                self.date_tools.format_date(parcours.entry_date),
                get_userdatas_seniority(u.id, date.today()),
                self.date_tools.format_date(parcours.contract_date),
                self.date_tools.format_date(u.situation_societariat_entrance),
                u.parcours_prescripteur.label if u.parcours_prescripteur else "",
                u.parcours_prescripteur_name,
                "",
                u.coordonnees_email1,
                u.coordonnees_email2,
                u.coordonnees_tel,
                u.coordonnees_mobile,
                u.coordonnees_address,
                u.coordonnees_zipcode,
                u.coordonnees_city,
                u.coordonnees_zone.label if u.coordonnees_zone else "",
                u.coordonnees_zone_qual.label if u.coordonnees_zone_qual else "",
                u.coordonnees_sex,
                self.date_tools.format_date(u.coordonnees_birthday),
                self.date_tools.age(u.coordonnees_birthday, self.end_date),
                u.coordonnees_birthplace,
                u.coordonnees_birthplace_zipcode,
                u.coordonnees_nationality,
                self.date_tools.format_date(u.coordonnees_resident),
                "",
                u.coordonnees_secu,
                get_tuple_option_label(STATUS_OPTIONS, u.coordonnees_family_status),
                u.coordonnees_children,
                u.coordonnees_study_level.label if u.coordonnees_study_level else "",
                u.coordonnees_emergency_name,
                u.coordonnees_emergency_phone,
                get_social_statuses_label(u.social_statuses),
                get_social_statuses_label(u.today_social_statuses),
                self.date_tools.format_date(u.statut_end_rights_date),
                self.date_tools.format_date(u.statut_handicap_allocation_expiration),
                self.date_tools.format_date(u.parcours_medical_visit),
                self.date_tools.format_date(u.parcours_medical_visit_limit),
                u.parcours_status.label if u.parcours_status else "",
                u.parcours_goals,
                u.activity_typologie.label if u.activity_typologie else "",
                "",
            ]
            # Champs complémentaires
            for field in get_active_custom_fields_names():
                user_data.append(get_custom_field_value_string(u, field))
            # Sortie
            user_data += [
                "",
                u.parcours_non_admission.label if u.parcours_non_admission else "",
            ]
            exit = parcours.exit
            if exit:
                user_data += [
                    self.date_tools.format_date(exit.start_date),
                    exit.type_sortie.label if exit.type_sortie else "",
                    exit.motif_sortie.label if exit.motif_sortie else "",
                ]
            else:
                user_data += [
                    "",
                    "",
                    "",
                ]
            # Création / modification
            user_data += [
                "",
                u.user_id,
                u.id,
                self.date_tools.format_date(u.created_at),
                self.date_tools.format_date(u.updated_at),
            ]
            data.append(user_data)
        return data
