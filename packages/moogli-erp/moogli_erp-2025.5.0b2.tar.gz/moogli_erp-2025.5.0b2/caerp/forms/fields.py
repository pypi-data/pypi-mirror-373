import colander
import deform
import datetime
import calendar

from caerp import forms
from caerp.forms.widgets import DateRangeMappingWidget


@colander.deferred
def deferred_january_first(node, kw):
    """
    Deferly returns the first january value
    """
    today = datetime.date.today()
    return datetime.date(today.year, 1, 1)


class DateRangeSchema(colander.MappingSchema):
    """
    A form used to select a period
    """

    name = "date_range"

    start = colander.SchemaNode(
        colander.Date(),
        default=forms.deferred_today,
        missing=colander.drop,
        title="Entre le",
        widget_options={"css_class": "input-medium search-query"},
    )

    end = colander.SchemaNode(
        colander.Date(),
        default=colander.null,
        missing=colander.drop,
        title="Et le",
        widget_options={"css_class": "input-medium search-query"},
    )

    period = colander.SchemaNode(
        colander.String(),
        title="Période",
        widget=deform.widget.SelectWidget(
            values=(
                (None, "- Sélectionner une période -"),
                ("today", "Aujourd’hui"),
                ("thisweek", "Cette semaine"),
                ("thismonth", "Ce mois-ci"),
            )
        ),
        default=None,
        missing=colander.drop,
    )

    widget = DateRangeMappingWidget()

    def preparer(self, values):
        start = values.get("start")
        end = values.get("end")
        period = values.get("period")

        if period not in (None, colander.null):
            now = datetime.date.today()
            if period == "today":
                start = now
                end = now
            elif period == "thisweek":
                start = now - datetime.timedelta(days=now.weekday())
                end = now + datetime.timedelta(days=6 - now.weekday())
            elif period == "thismonth":
                monthrange = calendar.monthrange(now.year, now.month)
                start = now.replace(day=1)
                end = now.replace(day=monthrange[1])

        return dict(start=start, end=end, period=period)

    def validator(self, node, appstruct):
        start = appstruct.get("start")
        end = appstruct.get("end")
        if start not in (None, colander.null) and end not in (None, colander.null):
            return end >= start


class YearPeriodSchema(colander.MappingSchema):
    """
    A form used to select a period
    """

    is_range = True

    start_date = colander.SchemaNode(
        colander.Date(),
        title="Début",
        description=None,
        missing=colander.drop,
        default=deferred_january_first,
    )
    end_date = colander.SchemaNode(
        colander.Date(),
        title="Fin",
        description=None,
        missing=colander.drop,
        default=forms.deferred_today,
    )

    def validator(self, form, value):
        """
        Validate the period
        """
        if value["start_date"] > value["end_date"]:
            exc = colander.Invalid(
                form, "La date de début doit précéder la date de fin"
            )
            exc["start_date"] = "Doit précéder la date de fin"
            raise exc
