"""
ThirdParty query service
"""
import logging
import requests

from sqlalchemy import func
from sqlalchemy.orm import load_only

from caerp.utils.strings import format_civilite


logger = logging.getLogger(__name__)

API_GOUV_ENTREPRISE_URL = "https://recherche-entreprises.api.gouv.fr/search"


class ThirdPartyService:
    @classmethod
    def format_name(cls, instance):
        """
        Format the name of a third_party regarding the available datas
        :param obj instance: A ThirdParty instance
        :rtype: str
        """
        res = ""
        if instance.lastname:
            res = instance.lastname
            if instance.civilite:
                res = "{0} {1}".format(format_civilite(instance.civilite), res)

            if instance.firstname:
                res += " {0}".format(instance.firstname)
        return res

    @classmethod
    def get_label(cls, instance):
        """
        Return the label suitable for the given instance
        :param obj instance: A ThirdParty instance
        :returns: The label
        :rtype: str
        """
        if instance.type in ("company", "internal"):
            return instance.company_name
        else:
            return cls.format_name(instance)

    @classmethod
    def get_address(cls, instance):
        """
        Return the address suitable for the given instance
        :param obj instance: A ThirdParty instance
        :returns: The address
        :rtype: str
        """
        address = ""
        if instance.type in ("company", "internal"):
            address += "{0}\n".format(instance.company_name)
        name = cls.format_name(instance)
        if name:
            address += "{0}\n".format(name)
        if instance.address:
            address += "{0}\n".format(instance.address)
        if instance.additional_address:
            address += "{0}\n".format(instance.additional_address)

        address += "{0} {1}".format(instance.zip_code, instance.city)
        country = instance.country
        if country is not None and country.lower() != "france":
            address += "\n{0}".format(country)
        return address

    @classmethod
    def label_query(cls, third_party_class):
        """
        Return a query loading datas needed to compile ThirdParty label
        """
        query = third_party_class.query()
        query = query.options(
            load_only(
                "id",
                "label",
                "code",
                "company_id",
            )
        )
        return query

    @staticmethod
    def get_by_label(cls, label: str, company: "Company", case_sensitive: bool = False):
        """
        Even if case_sensitive == True, exact match is preferred.
        """
        query = cls.query().filter(
            cls.archived == False,  # noqa: E712
            cls.company == company,
        )
        exact_match = query.filter(cls.label == label).one_or_none()

        if exact_match or case_sensitive:
            return exact_match
        else:
            insensitive_match = query.filter(
                func.lower(cls.label) == func.lower(label)
            ).one_or_none()
            return insensitive_match

    @classmethod
    def get_third_party_account(cls, third_party_instance):
        raise NotImplementedError("get_third_party_account")

    @classmethod
    def get_general_account(cls, third_party_instance):
        raise NotImplementedError("get_general_account")

    def find_company_infos(
        search: str, with_etablissements: bool = False, page_number: int = 1
    ) -> list:
        """
        Interroge l'API du gouvernement pour essayer de récupérer les informations
        de base sur une entreprise à partir de son SIREN, son SIRET, ou son nom

        :param string search: The SIREN, SIRET, or name of the company we're looking for
        :param bool with_etablissements: Whether we want the details of the establishments or not
        :param bool page_number: The number of the result page we want

        :returns: A list of dicts with company results data
        """
        company_results = []
        optional_infos = "siege"
        if with_etablissements:
            optional_infos += ",matching_etablissements"
        query_url = API_GOUV_ENTREPRISE_URL
        query_params = {
            "q": search,
            "page": page_number,
            "per_page": 25,
            "minimal": True,
            "include": optional_infos,
        }
        try:
            logger.info(f">  Send request : GET {query_url}, params={query_params}")
            response = requests.get(query_url, params=query_params)
        except requests.ConnectionError as e:
            logger.error(f"Unable to connect to {query_url}")
            logger.error(e)
        except requests.HTTPError as e:
            logger.error(f"Error code {response.status_code} : {response.content}")
            logger.error(e)
        else:
            logger.info(f"< Received HTTP {response.status_code} from {query_url}")
            logger.debug("  Response content :")
            logger.debug(response.content)
            if response.json()["total_results"] > 0:
                for result in response.json()["results"]:
                    company_data = {
                        "siren": result["siren"],
                        "name": result["nom_raison_sociale"],
                        "address": "{} {} {}".format(
                            result["siege"]["numero_voie"],
                            result["siege"]["type_voie"],
                            result["siege"]["libelle_voie"],
                        ),
                        "additional_address": result["siege"]["complement_adresse"],
                        "zip_code": result["siege"]["code_postal"],
                        "city": result["siege"]["libelle_commune"],
                        "city_code": result["siege"]["commune"],
                        "country": result["siege"]["libelle_pays_etranger"],
                        "country_code": result["siege"]["code_pays_etranger"],
                    }
                    if not company_data["country"]:
                        company_data["country"] = "FRANCE"
                        company_data["country_code"] = "99100"
                    company_results.append(company_data)
        return company_results
