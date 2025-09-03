from dataclasses import dataclass
from typing import Optional

import schwifty

from caerp.exception import MissingConfigError


@dataclass
class Creditor:
    """
    Dataclass désignant le destinataire d'un virement SEPA

    BIC et country sont détectés/détectables directement depuis l'IBAN
    """

    name: str
    iban: str
    bic: Optional[str] = None
    country: str = "FR"
    address: Optional[str] = None
    zipcode: Optional[str] = None
    city: Optional[str] = None

    def __post_init__(self):
        if not self.iban:
            raise MissingConfigError(message="IBAN non configuré")
        iban = schwifty.IBAN(self.iban, validate_bban=True)
        if not self.bic:
            if iban.bic:
                self.bic = str(iban.bic)
                self.country = iban.bic.country_code
            else:
                raise KeyError("Missing BIC")
        else:
            bic = schwifty.BIC(self.bic)
            self.country = bic.country_code


@dataclass
class Debtor(Creditor):
    pass


@dataclass
class AbstractPayment:
    amount: int
    transfer_ref: str
    creditor: Creditor
