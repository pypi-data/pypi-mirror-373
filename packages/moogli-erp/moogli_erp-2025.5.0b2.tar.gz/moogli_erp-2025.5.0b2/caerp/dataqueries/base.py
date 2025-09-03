from datetime import date
from typing import (
    Optional,
    Union,
    List,
)

from caerp.utils.datetimes import DateTools
from caerp.views import BaseView


class BaseDataQuery(BaseView):
    """
    Classe de base pour la génération des requêtes statistiques
    """

    name: str
    label: str
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    date_tools = DateTools()

    def __init__(self, *args, **kwargs):
        """
        Initialise la requête avec ses dates par défaut
        """
        super().__init__(*args, **kwargs)
        self.default_dates()

    def set_dates(
        self, start: Union[date, str, None] = None, end: Union[date, str, None] = None
    ):
        """
        Définit les dates de début et de fin de la requête si nécessaire

        Les dates peuvent être des chaines ou des objets 'datetime.date'
        """
        if start is not None:
            if isinstance(start, date):
                self.start_date = start
            else:
                try:
                    self.start_date = date.fromisoformat(start[:10])
                except:
                    self.start_date = date(2000, 1, 1)
        if end is not None:
            if isinstance(end, date):
                self.end_date = end
            else:
                try:
                    self.end_date = date.fromisoformat(end[:10])
                except:
                    self.end_date = date(2999, 12, 31)

    def default_dates(self):
        """
        Définit les dates par défaut (self.start_date et self.end_date) de la requête

        Doit être surchargée si la requête a besoin d'une date ou d'une période
        """
        pass

    def headers(self) -> List[str]:
        """
        Retourne la liste des colonnes de la requête
        au format  : ['header1', 'header2', 'header3']

        Doit être surchargée
        """
        raise NotImplementedError("Dataqueries must implement method 'headers()'")

    def data(self) -> List[List[str]]:
        """
        Retourne les données de la requête
        au format  : [
            ["data_line1_col1", "data_line1_col2", "data_line1_col3"],
            ["data_line2_col1", "data_line2_col2", "data_line2_col3"],
            ["data_line3_col1", "data_line3_col2", "data_line3_col3"],
        ]

        Doit être surchargée
        """
        raise NotImplementedError("Dataqueries must implement method 'data()'")
