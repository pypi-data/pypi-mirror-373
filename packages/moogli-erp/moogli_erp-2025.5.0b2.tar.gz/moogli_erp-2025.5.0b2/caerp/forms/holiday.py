"""
    form schemas for holiday declaration
"""
import colander
import logging

from deform import widget
from caerp.forms.user import contractor_filter_node_factory

log = logging.getLogger(__name__)


def date_validator(form, value):
    if value["start_date"] >= value["end_date"]:
        exc = colander.Invalid(form, "La date de début doit précéder la date de fin")
        exc["start_date"] = "Doit précéder la date de fin"
        raise exc


class HolidaySchema(colander.MappingSchema):
    start_date = colander.SchemaNode(colander.Date(), title="Date de début")
    end_date = colander.SchemaNode(colander.Date(), title="Date de fin")


class HolidaysList(colander.SequenceSchema):
    holiday = HolidaySchema(title="Période", validator=date_validator)


class HolidaysSchema(colander.MappingSchema):
    holidays = HolidaysList(title="", widget=widget.SequenceWidget(min_len=1))


class SearchHolidaysSchema(colander.MappingSchema):
    start_date = colander.SchemaNode(colander.Date(), title="Date de début")
    end_date = colander.SchemaNode(colander.Date(), title="Date de fin")
    user_id = contractor_filter_node_factory()


searchSchema = SearchHolidaysSchema(
    title="Rechercher les congés des entrepreneurs", validator=date_validator
)
