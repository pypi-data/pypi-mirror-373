import logging
from datetime import datetime
from typing import (
    Union,
    List,
)
import requests

"""
Ligth library to talk with URSSAFF tiers de paiement API

This library is not dependent at all from caerp codebase.
It could be shipped separately at a certain point if relevant.
"""


logger = logging.getLogger(__name__)

CLIENT_ID_SETTING_KEY = "caerp_sap_urssaf3p.client_id"
CLIENT_SECRET_SETTING_KEY = "caerp_sap_urssaf3p.client_secret"
API_URL_SETTING_KEY = "caerp_sap_urssaf3p.api_url"


class APIError(Exception):
    pass


class PermanentError(APIError):
    """
    An API error that is unlikely to succeed without code/config change.
    """


class TemporaryError(APIError):
    """
    An API error that may worth a retry
    """

    pass


class HTTPBadRequest(PermanentError):
    """
    400 error, specialized for URSSAF way of returning structured errors
    """

    FALLBACK_ERROR = {
        "code": "ERR_UNKNOWN",
        "description": "L'URSSAF n'a pas fourni de détail d'erreur",
        "message": "Erreur inconnue",
    }

    def __init__(self, errors: Union[List[dict], None]):
        # FIXME: is that required to handle multi-errors ?
        # I don't have the impression that urssaf actually issue them.

        if not errors:
            # spec says empty error payload should not happen. But in fact it does…
            errors = [self.FALLBACK_ERROR]

        err = errors[0]

        self.code = err["code"]
        self.description = err["description"]
        self.message = err["message"]
        self.errors = errors

    def __str__(self):
        return f"HTTP 400 error: {self.errors}"


StructuredData = Union[dict, list]


def serialize_datetime(dt: Union[datetime, None]) -> Union[str, None]:
    if dt:
        return dt.isoformat()
    else:
        return None


class URSSAF3PClient:
    """
    Thin API client for API "tiers de paiement" from URSSAF

    https://portailapi.urssaf.fr/fr/?option=com_apiportal&view=apitester&usage=api&apitab=tests&apiName=API+Tiers+de+prestations&apiId=0c533e48-daa7-4e50-ae5a-c0afe41cc061

    Are handled :
    - statefull auth (oauth)
    - systematic logging of requests and responses (at debug loglevel, except for auth requests)
    - catching of network and API errors

    Are not handled :
    - Bearer token expiration (qui dure 1h)
    - Multiple error returned (in case of 400 error)
    """

    def __init__(self, api_url):
        self.api_url = api_url
        self.oauth_url = f"{api_url}/api/oauth/v1/token"
        self.inscription_url = f"{api_url}/atp/v1/tiersPrestations/particulier"
        self.recherche_url = (
            f"{api_url}/atp/v1/tiersPrestations/demandePaiement/rechercher"
        )
        self.demande_paiement_url = f"{api_url}/atp/v1/tiersPrestations/demandePaiement"

        self.bearer_token = None

    def authorize(self, client_id, client_secret) -> Union[str, None]:
        """

        :param client_id:
        :param client_secret:
        :return: None if the auth was unsuccessful
        """
        try:
            logger.info(f"Requesting OAuth bearer token from {self.oauth_url}")
            response = requests.post(
                self.oauth_url,
                data=dict(
                    grant_type="client_credentials",
                    scope="homeplus.tiersprestations",
                    client_id=client_id,
                    client_secret=client_secret,
                ),
            )
            response.raise_for_status()

        except requests.ConnectionError as e:
            logger.error(e)
            raise TemporaryError(e)

        except requests.HTTPError:
            msg = f"OAuth failed : HTTP:{response.status_code} {response.content}"
            if response.status_code >= 500:
                raise TemporaryError(msg)
            else:
                raise PermanentError(msg)
        else:
            logger.info("OAuth bearer token received")
            received_token = response.json()["access_token"]
            self.bearer_token = received_token
            return received_token

    def request(self, url, payload: StructuredData) -> StructuredData:
        """
        Wraps the request, handling auth headers, error handling and parsing.

        May raise APIError subclasses or requests.JSONDecodeError
        """
        if not self.bearer_token:
            raise PermanentError(
                "You should authenticate with .authorize() prior to issuing a request"
            )
        logger.info(f"> Sent POST {url}")
        logger.debug(f"POST {url},  data: {payload}")
        try:
            headers = dict(Authorization=f"Bearer {self.bearer_token}")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

        except requests.ConnectionError as e:
            logger.error(e)
            raise TemporaryError(e)

        except requests.HTTPError as e:
            logger.error(e)
            msg = f"Received HTTP {response.status_code} {response.content}"
            logger.warning(msg)
            if response.status_code >= 500:
                raise TemporaryError(msg)
            elif response.status_code == 400:
                # We are pretty much sure of having a structured response
                # … but actually, despite the spec, there are cases where no payload or
                # empty payload is present.
                if response.content:
                    raise HTTPBadRequest(response.json())
                else:
                    raise HTTPBadRequest(None)
            else:
                raise PermanentError(response.content)
        else:
            logger.info(f"< Received HTTP {response.status_code} (to POST {url})")
            logger.info(f"  Response content : {response.content}")

            return response.json()

    def consulter_demandes(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        id_demandes: list = None,
    ) -> dict:
        """
        Ce service permet, pour un tiers de prestation authentifié, de récupérer les informations des
        demandes de paiement qui ont été enregistrées.

        La recherche s'effectue par les identifiants de demandes de paiement ou par la période de
        facturation. Dans le cas où les identifiants de demandes de paiement et la période sont
        renseignées, la recherche ne s’effectuera que sur les identifiants.
        Ce service permet de récupérer un maximum de 10 statuts de demandes de paiement par appel.

        (description source: URSSAF, Documentation-API-TiersPrestation_v1-1-7.pdf)

        :param start_date: min *invoice* date
        :param end_date: max *invoice* date
        :param id_demandes: max 10 of urssaf-generated IDs we want to query
        :return:
        """
        if id_demandes:
            if len(id_demandes) > 10:
                raise PermanentError(
                    f"Too many id_demandes at once : {len(id_demandes)}"
                )
            elif start_date or end_date:
                raise PermanentError("date or ids parameters are exclusive")
            else:
                payload = dict(idDemandePaiements=id_demandes)
        elif start_date or end_date:
            payload = dict(
                dateDebut=serialize_datetime(start_date),
                dateFin=serialize_datetime(end_date),
            )
        else:
            raise PermanentError("Require at least one of the args")

        return self.request(self.recherche_url, payload)

    def inscrire_client(self, payload: dict) -> str:
        """
        If sucessful, returns the id, else raise an error

        :returns: the URSSAF ID of the client.
        """
        response = self.request(self.inscription_url, payload)
        return response["idClient"]

    def transmettre_demande_paiement(self, payload: dict) -> str:
        """
        Transmits a single demande

        (the API support doing several at once)

        If sucessful, returns the id, else raise an error

        :returns: the URSSAF ID of the payment request.
        """
        payload_list = [payload]
        response_list = self.request(self.demande_paiement_url, payload_list)
        response = response_list[0]

        if response.get("errors"):
            raise HTTPBadRequest(response["errors"])
        else:
            assert (
                response["statut"] == "10"
            ), "Unexpected status, state-machine does not have other option !"
            return response["idDemandePaiement"]


def get_urssaf_api_client(registry_settings: dict) -> URSSAF3PClient:
    """
    Renvoie une instance du client d'api connectée

    :param registry_settings: La configuration de l'instance (fichier .ini),
    habituellement récupérée par : request.registry.settings

    >>> client = get_urssaf_api_client(registry_settings)
    >>> id_client = client.inscrire_client(client_au_format_urssaf)
    """
    client_id = registry_settings.get(CLIENT_ID_SETTING_KEY)
    client_secret = registry_settings.get(CLIENT_SECRET_SETTING_KEY)
    url = registry_settings.get(API_URL_SETTING_KEY)

    client = URSSAF3PClient(url)
    if client_id is None or client_secret is None:
        raise Exception(
            f"Configuration manquante : {CLIENT_ID_SETTING_KEY} ou "
            f"{CLIENT_SECRET_SETTING_KEY} ne sont pas définis dans "
            f"le fichier de configuration de l’application"
        )
    client.authorize(client_id, client_secret)
    return client
