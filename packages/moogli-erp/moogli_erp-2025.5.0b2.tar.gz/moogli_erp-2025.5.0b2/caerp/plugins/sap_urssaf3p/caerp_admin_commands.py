from argparse import ArgumentParser
import datetime
import logging
import json
import csv
from typing import List


from sqlalchemy.orm import joinedload

from caerp_base.models import DBSESSION
from caerp.utils.datetimes import parse_date
from caerp.consts.insee_countries import find_country_insee_code
from caerp.consts.insee_departments import find_departement_insee_code
from caerp.models.tva import (
    Product,
    Tva,
)
from caerp.models.third_party import Customer
from caerp.plugins.sap_urssaf3p import api_client
from caerp.plugins.sap_urssaf3p.api_client import (
    URSSAF3PClient,
    get_urssaf_api_client,
)

from caerp.scripts.caerp_admin import (
    CaerpAdminCommandsRegistry,
    AbstractCommand,
)

logger = logging.getLogger(__name__)


class CheckUrssaf3pCommand(AbstractCommand):
    """Checks that URSSAF tiers de paiement feature is well configured"""

    name = "check_urssaf3p"

    @classmethod
    def check_oauth(cls, client, client_id, client_secret):
        try:
            client.authorize(client_id, client_secret)
        except api_client.APIError as e:
            logger.error(f"❌ OAuth failed")
        else:
            logger.info("✅ OAuth auth works.")

    @classmethod
    def check_test_request(cls, client):
        check_ok = False
        response = None
        caught_e = None

        try:
            response = client.consulter_demandes(
                start_date=datetime.datetime(2053, 1, 1)
            )

        except api_client.HTTPBadRequest as e:
            caught_e = e
            if e.code == "ERR_RECHERCHE_VIDE":
                check_ok = True
        except api_client.APIError as e:
            caught_e = e

        finally:
            if check_ok:
                logger.info("✅ Réponse à la requête de test conforme.")
            elif caught_e:
                logger.error(f"❌ Requête de test en erreur : {caught_e}")
            elif response:
                logger.error(
                    f"❌ Requête de test en erreur : HTTP: {response.status_code}, contenu: {response.content}"
                )

    @classmethod
    def check_config(cls, ini_settings):
        required_settings = [
            "caerp_sap_urssaf3p.api_url",
            "caerp_sap_urssaf3p.client_id",
            "caerp_sap_urssaf3p.client_secret",
        ]

        logger.debug("Checking .ini config...")

        config_ok = True
        for s in required_settings:
            if s not in ini_settings:
                logger.error(f"❌ missing setting {s} in .ini ; see doc")
                config_ok = False

        if config_ok:
            logger.info("✅ .ini config is OK")

    @classmethod
    def check_products(cls):
        """
        Checks that at least one product is offered with a code_nature urssaf
        """
        query = (
            Product.query()
            .options(joinedload(Product.tva))
            .filter(
                Tva.active == True,
                Product.active == True,
            )
        )
        configured_count = query.filter(Product.urssaf_code_nature != "").count()
        unconfigured_count = query.filter(Product.urssaf_code_nature == "").count()

        if configured_count < 1:
            logger.error(
                f"❌ No enabled product with a urssaf code, you must configure it in config panel."
            )
        else:
            logger.info(
                f"✅ There are {configured_count} enabled products with an URSSAF code "
                f"({unconfigured_count} unconfigured)."
            )

    def __call__(cls, arguments, env):
        ini_settings = env["registry"].settings

        cls.check_config(ini_settings)

        client = URSSAF3PClient(ini_settings["caerp_sap_urssaf3p.api_url"])

        cls.check_oauth(
            client=client,
            client_id=ini_settings["caerp_sap_urssaf3p.client_id"],
            client_secret=ini_settings["caerp_sap_urssaf3p.client_secret"],
        )
        cls.check_test_request(client)
        cls.check_products()


class InitializeURSSAFProducts(AbstractCommand):
    """
    Initialize all products from the URSSAF SAP nomenclature

    May be useful for newcommers to enDi.

    Sources:
        - https://www.urssaf.fr/portail/files/live/sites/urssaf/files/documents/SAP-Documentation-API-TiersPrestation.pdf
        - https://entreprendre.service-public.fr/vosdroits/F31596 (taux TVA)

    Pour les natures, colone 1 : code nature, colone 2 : libellé court

    """

    name = "initialize_urssaf_products"

    URSSAF_NOMENCLATURE = [
        {
            "tva": 550,
            "natures": [
                ("10", "Garde d’enfant handicapé"),
                ("20", "Accompagnement d’enfant handicapé"),
                ("30", "Aide humaine"),
                ("40", "Conduite du véhicule personnel"),
                ("50", "Accompagnement pour les sorties"),
                ("220", "Interprétariat et codage"),
            ],
        },
        {
            "tva": 1000,
            "natures": [
                ("60", "Ménage- repassage"),
                ("80", "Petit bricolage"),
                ("90", "Garde d’enfant + 6 ans"),
                ("100", "Soutien scolaire"),
                ("110", "Coiffure – esthétique"),
                ("120", "Préparation de repas"),
                ("130", "Livraison de repas"),
                ("140", "Collecte et livraison de linge"),
                ("170", "Soins et promenades d’animaux"),
                ("150", "Livraison de course"),
                ("190", "Assistance administrative"),
                ("200", "Accompagnement d’enfant + 6 ans"),
                ("230", "Conduite du véhicule personnel – temporaire"),
                ("240", "Accompagnement pour les sorties – temporaire"),
                ("250", "Aide humaine – temporaire"),
            ],
        },
        {
            "tva": 2000,
            "natures": [
                ("70", "Jardinage"),
                ("160", "Assistance informatique"),
                ("180", "Gardiennage"),
                ("210", "Téléassistance"),
                ("260", "Plateforme de coordination"),
                ("270", "Divers – Non eligible"),
            ],
        },
    ]

    @classmethod
    def __call__(cls, arguments, env):
        """
        Populate a product for each code nature in URSSAF referential

        Skip populating if a product with a given code nature already exists.
        Even if it seems misled about tva rate
        (just warn, it may be enDi not beaing up to date…)
        """
        session = DBSESSION()
        query = session.query(Product).options(joinedload(Product.tva))
        for tva_block in cls.URSSAF_NOMENCLATURE:
            tva_value = tva_block["tva"]
            tva = session.query(Tva).filter_by(value=tva_value).first()

            # Should not happen
            assert tva is not None, f"TVA manquante : {tva_value}%"

            for nature in tva_block["natures"]:
                code, label = nature

                existing_products_for_nature = query.filter_by(urssaf_code_nature=code)

                if existing_products_for_nature.first() is None:
                    logger.info(f'Ajoute le produit "{label}" (URSSAF {code}).')
                    # Created products are disabled at first
                    p = Product(
                        tva=tva, name=label, urssaf_code_nature=code, active=False
                    )
                    session.add(p)
                else:
                    for p in existing_products_for_nature:
                        if p.tva.active and p.active and p.tva != tva:
                            logger.warning(
                                f"Product {p.name} is on tva {p.tva} at"
                                " {p.tva.value}% (should be {tva_value}%)."
                            )

            session.flush()


class GetCustomerPayload(AbstractCommand):
    """Return serialized data for given customer"""

    name = "get_urssaf3p_customer_payload"

    @classmethod
    def add_arguments(cls, parser) -> None:
        parser.add_argument("customer_id")

    def __call__(cls, arguments, env):
        from caerp.plugins.sap_urssaf3p.serializers import serialize_customer

        customer = Customer.get(arguments.customer_id)
        if customer:
            logger.info(json.dumps(serialize_customer(customer), indent=4))
        else:
            logger.error(f"❌ Le client {arguments.customer_id} n'existe pas")


class GetInvoicePayload(AbstractCommand):
    """Return serialized data for given invoice"""

    name = "get_urssaf3p_invoice_payload"

    @classmethod
    def add_arguments(cls, parser) -> None:
        parser.add_argument("invoice_id")

    def __call__(cls, arguments, env):
        from caerp.plugins.sap_urssaf3p.serializers import serialize_invoice
        from caerp.models.task import Invoice

        invoice = Invoice.get(arguments.invoice_id)
        if invoice:
            logger.info(json.dumps(serialize_invoice(invoice), indent=4))
        else:
            logger.error(f"❌ La facture {arguments.invoice_id} n'existe pas")


class GetUrssafPaymentRequestsByPeriod(AbstractCommand):
    """Get all payment requests registred by Urssaf"""

    name = "get_urssaf3p_payment_requests_by_period"

    @classmethod
    def add_arguments(cls, parser) -> None:
        parser.add_argument("--start", help="Format : YYYY-MM-DD")
        parser.add_argument("--end", help="Format : YYYY-MM-DD")

    def __call__(cls, arguments, env):
        ini_settings = env["registry"].settings
        client = URSSAF3PClient(ini_settings["caerp_sap_urssaf3p.api_url"])
        client = get_urssaf_api_client(ini_settings)
        try:
            response = client.consulter_demandes(
                start_date=datetime.datetime.strptime(arguments.start, "%Y-%m-%d"),
                end_date=datetime.datetime.strptime(arguments.end, "%Y-%m-%d"),
            )
        except Exception as e:
            logger.error(f"❌ Requête en erreur : {e}")

        else:
            logger.info(json.dumps(response, indent=4))


class GetUrssafPaymentRequestById(AbstractCommand):
    """Get specific payment request registred by Urssaf from its id"""

    name = "get_urssaf3p_payment_request"

    @classmethod
    def add_arguments(cls, parser) -> None:
        parser.add_argument("request_id")

    def __call__(cls, arguments, env):
        ini_settings = env["registry"].settings
        client = URSSAF3PClient(ini_settings["caerp_sap_urssaf3p.api_url"])
        client = get_urssaf_api_client(ini_settings)
        try:
            response = client.consulter_demandes(id_demandes=[arguments.request_id])
        except Exception as e:
            logger.error(f"❌ Requête en erreur : {e}")

        else:
            logger.info(json.dumps(response, indent=4))


class ImportFromAis(AbstractCommand):
    """
    Import Urssaf customer data from AIS export file.

    File is supposed to be converted in CSV format first.

    caerp-admin /config/caerp.ini urssaf3p_import_from_ais /config/client_sap.csv
    """

    name = "urssaf3p_import_from_ais"

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")

    @classmethod
    def find_customers(cls, session, ais_data_dict) -> List[Customer]:
        email = ais_data_dict["Email"]
        query = session.query(Customer).filter(Customer.email == email)
        if query.count() > 0:
            return query.all()

        lastname = ais_data_dict["Nom d'usage"]
        query = session.query(Customer).filter(Customer.lastname == lastname)
        if query.count() == 1:
            return query.all()
        firstnames = ais_data_dict["Prénoms"]
        query = query.filter(Customer.firstname.in_(firstnames.split(" ")))
        if query.count() > 0:
            return query.all()
        return []

    @classmethod
    def _find_department_code(cls, departement_name):
        departement_name = "".join(departement_name.split("-")[1:])
        return find_departement_insee_code(departement_name)

    @classmethod
    def _split_address(cls, address):
        """Splitte une adresse en 3 parties : adresse, zip_code, city
        :param address: Addresse   Ville Code
        Addresse et ville sont séparés de 3 espaces
        Code est composé des 5 derniers caractères
        """
        address = address.strip()
        address_parts = address.split("   ")
        if len(address_parts) == 2:
            street_address = address_parts[0]
            subsplit = address_parts[1].split(" ")
            if len(subsplit) >= 2:
                zip_code = address_parts[1].split(" ")[-1]
                city = " ".join(address_parts[1].split(" ")[0:-1])
                return street_address, zip_code, city
            else:
                return "", address_parts[0], address_parts[1]
        else:
            return address, "", ""

    @classmethod
    def _get_urssaf_status(cls, status):
        if status == "Compte Validé":
            return "valid"
        elif status == "Compte en cours de validation":
            return "wait"

    @classmethod
    def _add_urssaf3p_data(cls, session, row, customer):
        from caerp.plugins.sap_urssaf3p.models.customer import (
            UrssafCustomerData,
            UrssafCustomerRegistrationStatus,
        )

        customer.firstname = row["Prénoms"]
        customer.email = row["Email"]
        customer.mobile = row["Téléphone"]

        if not customer.address:
            customer.address, customer.zip_code, customer.city = cls._split_address(
                row["Adresse"]
            )
            customer.bank_account_iban = "FR2414508000307364971564Q72"
            customer.bank_account_bic = "EBATFRPPEB1"
            customer.bank_account_owner = "informations bancaires à receuillir"
        # Crée une instance de UrssafCustomerData associé au customer.id
        urssaf3p_data = UrssafCustomerData(
            customer=customer,
            client_id=row["idClient"],
            birth_name=row["Nom de Naissance"],
            birthdate=parse_date(row["Date de Naissance"], format_="%d/%m/%Y"),
            birthplace_city=row["Commune de Naissance"],
            birthplace_department_code=cls._find_department_code(
                row["Département de Naissance"]
            ),
            birthplace_country_code=find_country_insee_code(row["Pays de Naissance"]),
        )  # type: ignore
        session.add(urssaf3p_data)
        session.flush()
        # Crée une instance de UrssafCustomerRegistrationStatus avec l'id 0
        # Commentaire "Créé automatiquement par la migration depuis AIS"
        urssaf3p_registration_status = UrssafCustomerRegistrationStatus(
            data_id=urssaf3p_data.id,
            user_id=0,
            status_date=parse_date(row["Date inscription"], format_="%d/%m/%Y"),
            status=cls._get_urssaf_status(row["Statut du compte Urssaf"]),
        )  # type: ignore
        session.add(urssaf3p_registration_status)
        session.flush()

    def __call__(cls, arguments, env):
        dbsession = env["request"].dbsession
        cache = []
        with open(arguments.filepath, "r"):
            reader = csv.DictReader(
                open(arguments.filepath, "r"), delimiter=";", quotechar='"'
            )
            for row in reader:
                if "Email" not in row:
                    logger.error(f"❌ L’adresse mail est manquante : {row}")
                    continue
                customers = cls.find_customers(dbsession, row)
                if customers == []:
                    logger.error(f"❌ Ce client n’existe pas dans la base {row}")
                for customer in customers:
                    if customer.urssaf_data is not None or customer.id in cache:
                        client = row["Client"]
                        logger.error(
                            f"❌ Ce client a déjà des informations urssaf3p de "
                            f"renseigné {client}"
                        )
                    else:
                        logger.info(
                            f"✅ Update du client {customer.label} d’id : {customer.id}"
                        )
                        logger.debug(row)
                        cache.append(customer.id)
                        cls._add_urssaf3p_data(dbsession, row, customer)


def includeme(config):
    CaerpAdminCommandsRegistry.add_function(CheckUrssaf3pCommand)
    CaerpAdminCommandsRegistry.add_function(InitializeURSSAFProducts)
    CaerpAdminCommandsRegistry.add_function(GetCustomerPayload)
    CaerpAdminCommandsRegistry.add_function(GetInvoicePayload)
    CaerpAdminCommandsRegistry.add_function(GetUrssafPaymentRequestsByPeriod)
    CaerpAdminCommandsRegistry.add_function(GetUrssafPaymentRequestById)
    CaerpAdminCommandsRegistry.add_function(ImportFromAis)
