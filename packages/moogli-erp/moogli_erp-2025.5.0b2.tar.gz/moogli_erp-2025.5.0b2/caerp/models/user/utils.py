import datetime
import json
import logging
from dataclasses import dataclass

from datetime import date
from dateutil.relativedelta import relativedelta
from functools import lru_cache
from typing import (
    Optional,
    Union,
    List,
    Tuple,
    Iterable,
)

import requests
from caerp_base.models.base import DBSESSION
from sqlalchemy import func
from sqlalchemy.orm import with_polymorphic, aliased

from caerp.models.activity import (
    Event,
    Attendance,
    Activity,
)
from caerp.models.config import Config
from caerp.models.career_path import CareerPath
from caerp.models.user.userdatas import (
    User,
    UserDatas,
    UserDatasCustomFields,
    CaeSituationOption,
)
from caerp.models.workshop import Timeslot, Workshop
from caerp.utils.colanderalchemy import get_model_columns_list


logger = logging.getLogger(__name__)


def get_userdatas_first_step(
    userdatas_id: int, limit_date: date = None, stage_type_filter: List[str] = None
) -> Union[CareerPath, None]:
    """
    Return the first CareerPath with a stage type of the user
    after the given date if specified
    with the given stage types if specified

    :param userdatas_id: id of the userdatas concerned
    :param limit_date: Optional limit date, we want the first step after this date
    :param stage_type_filter: Optional list of the stage types we want
        eg: ['exit'], ['entry','contract']

    :returns: A CareerPath (the first step) or None
    """
    first_step_query = (
        DBSESSION()
        .query(CareerPath)
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.stage_type != None)
    )
    if limit_date:
        first_step_query = first_step_query.filter(CareerPath.start_date >= limit_date)
    if stage_type_filter:
        first_step_query = first_step_query.filter(
            CareerPath.stage_type.in_(stage_type_filter)
        )
    first_step_query = first_step_query.order_by(CareerPath.start_date)
    return first_step_query.first()


def get_userdatas_last_step(
    userdatas_id: int, limit_date: date = None, stage_type_filter: List[str] = None
) -> Union[CareerPath, None]:
    """
    Return the last CareerPath with a stage type of the user
    before the given date if specified
    with the given stage types if specified

    :param userdatas_id: id of the userdatas concerned
    :param limit_date: Optional limit date, we want the last step before this date
    :param stage_type_filter: Optional list of the stage types we want
        eg: ['exit'], ['entry','contract']

    :returns: A CareerPath (the last step) or None
    """
    last_step_query = (
        DBSESSION()
        .query(CareerPath)
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.stage_type != None)  # noqa: E711
    )
    if limit_date:
        last_step_query = last_step_query.filter(CareerPath.start_date <= limit_date)
    if stage_type_filter:
        last_step_query = last_step_query.filter(
            CareerPath.stage_type.in_(stage_type_filter)
        )
    last_step_query = last_step_query.order_by(CareerPath.start_date.desc())
    return last_step_query.first()


def get_userdatas_steps_on_period(
    userdatas_id: int,
    period_start_date: Optional[date],
    period_end_date: date,
    stage_type_only: List[str] = None,
    stage_type_exclude: List[str] = None,
    sort_descending: bool = False,
) -> List[CareerPath]:
    """
    Return all the CareerPath with a stage type of the user between two dates
    with the given stage types if specified

    :param userdatas_id: id of the userdatas concerned
    :param period_start_date: The period start date, we want the steps after this date
    :param period_end_date: The period end date, we want the steps before this date
    :param stage_type_only: Optional list of the stage types we want
        eg: ['exit'], ['entry','contract','amendment']
    :param stage_type_exclude: Optional list of the stage types we do not want
    :param sort_descending: True if we want the steps sorted from last to first

    :returns: A list of CareerPath (the steps)
    """
    steps_query = (
        DBSESSION()
        .query(CareerPath)
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.start_date <= period_end_date)
        .filter(CareerPath.stage_type != None)
    )
    if period_start_date:
        steps_query = steps_query.filter(CareerPath.start_date >= period_start_date)

    if stage_type_only:
        steps_query = steps_query.filter(CareerPath.stage_type.in_(stage_type_only))
    if stage_type_exclude:
        steps_query = steps_query.filter(
            CareerPath.stage_type.notin_(stage_type_exclude)
        )
    if sort_descending:
        steps_query = steps_query.order_by(CareerPath.start_date.desc())
    else:
        steps_query = steps_query.order_by(CareerPath.start_date)
    return steps_query.all()


@dataclass
class Parcours:
    """
    Parcours qualifies a list of consecutive CareerPaths

    A parcours contains :
    - exaclty one CareerPath considered as entry
    - optionaly one CareerPath considered as exit
    - any number of steps (it includes entry, and exit if any)
    """

    entry: CareerPath
    exit: Optional[CareerPath]
    steps: List[CareerPath]

    @property
    def exit_date(self):
        return self._date_or_none(self.exit)

    @property
    def entry_date(self):
        return self._date_or_none(self.entry)

    @property
    def contract_date(self):
        return self._date_or_none(self.first_of_type(["contract"]))

    @staticmethod
    def _date_or_none(step: Optional[CareerPath]) -> Optional[date]:
        if step:
            return step.start_date
        else:
            return None

    def last_of_type(self, types: List[str]) -> Optional[CareerPath]:
        for cp in reversed(self.steps):
            if cp.stage_type in types:
                return cp

    def first_of_type(self, types: List[str]) -> Optional[CareerPath]:
        for cp in self.steps:
            if cp.stage_type in types:
                return cp


def get_ongoing_parcours(userdatas_id: int, at_date: date) -> Optional[Parcours]:
    """
    Returns the steps of the ongoing steps at a given date

    Useful in case of multiple parcours, isolate one, that we consider as the relevant one.

    - if at_date is after the last exit, the most recent parcours before will be returned
    - if at_date is between an entry and an exit, the exit is not included in parcours (considered in future)
    """
    query = (
        CareerPath.query()
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.start_date <= at_date)
    )

    steps = query.all()

    # Cannot manage to SQL-sort it, don't know why…
    steps.sort(key=lambda x: x.start_date)

    my_entry, my_exit = None, None
    latest_exit, latest_entry = None, None
    for step in reversed(steps):  # anti-chronological
        if step.stage_type in ["entry", "contract", "amendment"]:
            latest_entry = step
        elif step.stage_type == "exit":
            if latest_entry is None:
                # We are at our ongoing exit
                # If there are several exits, we keep the earliest
                my_exit = step
                # … and continue to iterate to get relevant entry

            else:
                # We are before our ongoing entry, fast-forward to get relevant steps
                my_exit = latest_exit
                break

            latest_exit = step

    my_entry = latest_entry
    if (
        latest_exit and latest_entry and (latest_entry.start_date > my_exit.start_date)
    ):  # Missing CareerPath of type entry
        my_entry = None

    in_parcours = False
    relevant_steps = []
    for step in steps:
        if step == my_exit:
            relevant_steps.append(step)
            break
        elif (step == my_entry) or (my_entry is None):
            in_parcours = True
        if in_parcours:
            relevant_steps.append(step)

    if my_entry:
        return Parcours(
            steps=relevant_steps,
            entry=my_entry,
            exit=my_exit,
        )
    else:
        # No entry -> no parcours ! (anormal)
        return None


def get_userdatas_seniority(user_id: int, at_date: date = None) -> int:
    """
    Return the seniority (in months) of the given user in the CAE calculated
    from entry date to the earliest date between given date, exit date, and today
    """
    parcours = get_ongoing_parcours(user_id, at_date)
    if not parcours:
        return 0
    else:
        counting_period_start = parcours.entry_date

        if parcours.exit_date is None:
            counting_period_end = date.today()
        else:
            counting_period_end = min(parcours.exit_date, at_date)

        td = relativedelta(counting_period_end, counting_period_start)
        return (td.years * 12) + td.months


def is_userdatas_active_on_period(userdatas_id: int, start: date, end: date) -> bool:
    """
    Returns whether the user was active during the given period

    This means that he has an entry before the period ends and
    no exit or an exit after the period start

    NB : User can exit and come back, the period can be on the absence
    and this function should return False in this case

    :returns: True if active else False
    """
    parcours = get_ongoing_parcours(userdatas_id, end)
    if parcours is None:
        return False
    elif parcours.exit is None:
        return True
    else:
        return parcours.exit_date >= start


def get_all_userdatas_active_on_period(start: date, end: date) -> List[UserDatas]:
    """
    Returns all the UserDatas active on the given period

    This means all users that has an entry before the period ends and
    no exit or an exit after the period start

    :returns: A list of UserDatas
    """
    all = (
        UserDatas.query()
        .join(CareerPath)
        .filter(CareerPath.stage_type.in_(["entry", "contract", "amendment"]))
        .all()
    )
    actives = []
    for pp in all:
        if is_userdatas_active_on_period(pp.id, start, end):
            actives.append(pp)
    logger.debug(
        f"{len(actives)} actives user on period {start.strftime('%d/%m/%Y')} \
            to {end.strftime('%d/%m/%Y')} for {len(all)} entered users"
    )
    return actives


def get_user_analytical_accounts(user_id: int, only_active: bool = False) -> str:
    """
    Return a string with the analytical accounts of the given user
    """
    compta_str = ""
    user = User.get(user_id)
    for c in user.companies:
        if c.code_compta and c.code_compta not in compta_str:
            if c.active or not only_active:
                compta_str += f"{c.code_compta}, "
    if len(compta_str) > 0:
        compta_str = compta_str[:-2]
    return compta_str


def get_tuple_option_label(options_tuple: tuple, key: str) -> str:
    """
    Return label associated to a given key in a tuple of options '(key, label)'
    """
    try:
        label = [
            option_label
            for option_key, option_label in options_tuple
            if option_key == key
        ][0]
    except IndexError:
        label = ""
    return label


def get_social_statuses_label(social_statuses) -> str:
    """
    Return a string with the social statuses of the given user
    """
    if len(social_statuses) > 1:
        social_statuses_label = ""
        for social_status in social_statuses:
            social_statuses_label += f"{social_status.social_status.label} ; "
        social_statuses_label = social_statuses_label[:-3]
    elif len(social_statuses) == 1:
        social_statuses_label = social_statuses[0].social_status.label
    else:
        social_statuses_label = ""
    return social_statuses_label


def get_active_custom_fields() -> List[str]:
    """
    Returns the names of all active custom fields
    """
    return json.loads(Config.get_value("userdatas_active_custom_fields", "[]"))


def get_active_custom_fields_names() -> List[str]:
    """
    Returns the names of all active custom fields
    """
    active_custom_fields_names = []
    for field in get_model_columns_list(UserDatasCustomFields):
        if field.name in get_active_custom_fields():
            active_custom_fields_names.append(field.name)
    return active_custom_fields_names


def get_active_custom_fields_labels() -> List[str]:
    """
    Returns the labels of all active custom fields
    """
    active_custom_fields_labels = []
    for field in get_model_columns_list(UserDatasCustomFields):
        if field.name in get_active_custom_fields():
            active_custom_fields_labels.append(field.info["colanderalchemy"]["title"])
    return active_custom_fields_labels


def get_custom_field_value_string(userdatas: UserDatas, custom_field: str) -> str:
    """
    Return string value of the given custom field of the given userdatas

    Used for dataqueries exports
    """
    value = ""
    if userdatas.custom_fields:
        value = str(getattr(userdatas.custom_fields, custom_field))
    if value == "True":
        value = "Oui"
    if value == "False":
        value = "Non"
    if value == "None":
        value = ""
    return value


def get_userdatas_cae_situation(
    userdatas_id: int, date_ref: date = None
) -> Union[CaeSituationOption, None]:
    """
    Return the CaeSituationOption of the user
    before the given date if specified

    :param userdatas_id: id of the userdatas concerned
    :param date_ref: Optional limit date, we want the CAE situation before this date

    :returns: A CaeSituationOption (the CAE situation) or None
    """
    last_situation_step_query = (
        DBSESSION()
        .query(CareerPath)
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.cae_situation_id != None)
    )
    if date_ref:
        last_situation_step_query = last_situation_step_query.filter(
            CareerPath.start_date <= date_ref
        )
    last_situation_step_query = last_situation_step_query.order_by(
        CareerPath.start_date.desc()
    )
    last_situation_step = last_situation_step_query.first()
    if last_situation_step:
        return CaeSituationOption.get(last_situation_step.cae_situation_id)
    else:
        return None


def get_user_accompaniment_stats(
    user_id: int, start: date, end: date
) -> Tuple[int, float, Union[date, None], str, int, float, Union[date, None], str]:
    """
    Return statistics on the accompaniment of the given user on the given period :
    - Number of appointments attended
    - Number of hours of appointments attended
    - Date of the last appointment attended
    - Type of the last appointment attended
    - Number of workshops attended
    - Number of hours of workshops attended
    - Date of the last workshop attended
    - Title of the last workshop attended
    """
    nb_rdvs = 0
    nb_h_rdvs = 0
    last_rdv_date = None
    last_rdv_name = ""
    nb_ateliers = 0
    nb_h_ateliers = 0
    last_atelier_date = None
    last_atelier_name = ""

    all_events = with_polymorphic(Event, "*")
    timeslot_workshop = aliased(Workshop)

    # Event.datetime may be wrong, the reliable time is Timeslot.start_time
    date_of_event = func.IF(
        all_events.type_ == "timeslot",
        Timeslot.start_time,
        all_events.datetime,
    )

    query = (
        all_events.query()
        .join(Attendance)
        .outerjoin(timeslot_workshop, Timeslot.workshop)
        .where(date_of_event.between(start, end))
        .where(Attendance.status == "attended")
        .where(Attendance.account_id == user_id)
        .order_by(date_of_event.desc())
    )
    for event in query.all():
        if isinstance(event, Activity):
            nb_rdvs += 1
            if event.duration:
                nb_h_rdvs += int(event.duration) / 60
            if not last_rdv_date:
                last_rdv_date = event.datetime.date()
                last_rdv_name = event.type_object.label
        elif isinstance(event, Timeslot):
            nb_ateliers += 1
            time_delta = event.end_time - event.start_time
            nb_h_ateliers += time_delta.seconds / 3600
            if not last_atelier_date:
                last_atelier_date = event.start_time.date()
                last_atelier_name = event.workshop.title
        else:
            logger.error(f"Unexpected event type : {type(event)}")
    nb_h_rdvs = round(nb_h_rdvs, 2)
    nb_h_ateliers = round(nb_h_ateliers, 2)
    return (
        nb_rdvs,
        nb_h_rdvs,
        last_rdv_date,
        last_rdv_name,
        nb_ateliers,
        nb_h_ateliers,
        last_atelier_date,
        last_atelier_name,
    )


def get_user_companies_names(user_id: int, only_active: bool = False) -> str:
    """
    Return a string with the name of active companies of the given user
    """
    user = User.get(user_id)
    companies_names_str = ""
    if only_active:
        companies = user.active_companies
    else:
        companies = user.companies
    if len(companies) == 1:
        companies_names_str = f"{companies[0].name}"
    elif len(companies) > 1:
        for c in companies:
            companies_names_str += f"- {c.name}\r\n"
        companies_names_str = companies_names_str[:-2]
    return companies_names_str


def get_user_companies_goals(user_id: int, only_active: bool = False) -> str:
    """
    Return a string with the goals of active companies of the given user
    """
    user = User.get(user_id)
    companies_goals_str = ""
    if only_active:
        companies = user.active_companies
    else:
        companies = user.companies
    if len(companies) == 1:
        companies_goals_str = f"{companies[0].goal}"
    elif len(companies) > 1:
        for c in companies:
            companies_goals_str += f"- {c.goal}\r\n"
        companies_goals_str = companies_goals_str[:-2]
    return companies_goals_str


def get_user_companies_activities(
    user_id: int, only_main: bool = False, only_active: bool = False
) -> str:
    """
    Return a string with the activities of the active companies of the given user

    Option "only_main" will return only the main (first) activity of each company
    """
    user = User.get(user_id)
    companies_activities = []
    companies_activities_str = ""
    if only_active:
        companies = user.active_companies
    else:
        companies = user.companies
    for c in companies:
        if only_main:
            companies_activities.append(c.main_activity)
        else:
            for a in c.activities:
                if a not in companies_activities:
                    companies_activities.append(a.label)
    if len(companies_activities) == 1:
        companies_activities_str = f"{companies_activities[0]}"
    elif len(companies_activities) > 1:
        for activity in companies_activities:
            companies_activities_str += f"- {activity}\r\n"
        companies_activities_str = companies_activities_str[:-2]
    return companies_activities_str


def get_user_turnover(
    user_id: int, start: date, end: date, only_active: bool = False
) -> int:
    """
    Return the global turnover of the actives companies of the given user
    on the given period

    For multi-employees companies turnover is equally split by employee
    """
    user = User.get(user_id)
    user_turnover = 0
    if only_active:
        companies = user.active_companies
    else:
        companies = user.companies
    for c in companies:
        company_turnover = c.get_turnover(start, end)
        if len(c.employees) > 1:
            nb_employees = 0
            for e in c.employees:
                if e.userdatas and is_userdatas_active_on_period(
                    e.userdatas.id, start, end
                ):
                    nb_employees += 1
            user_turnover += round(company_turnover / max(1, nb_employees), 2)
        else:
            user_turnover += company_turnover
    return user_turnover


@lru_cache(maxsize=200)  # memoize
def get_epci_label(postcode: str, city: str) -> str:
    """
    From a postcode, gets EPCI (« Communauté de commune ») from geo.api.gouv.fr name

    Result is fetched from API and cached in RAM to avoid spamming the API

    :return a str (starting with "Inconnu" if no result was found)
    """
    base_url = "https://geo.api.gouv.fr"
    if not postcode or len(postcode) != 5:
        return ""
    postcode_resp = requests.get(
        f"{base_url}/communes",
        params=dict(codePostal=postcode, fields="epci"),
    )

    try:
        postcode_resp.raise_for_status()
        json_resp = postcode_resp.json()
        if not json_resp:
            raise KeyError("Code postal inconnu")

        epcis = set(i["epci"]["nom"] for i in json_resp)
        if len(epcis) == 1:
            epci_label = epcis.pop()
        else:
            # There may be >1 EPCI per postcode, another request will help
            # Using api adresse first as it allows fuzzy match
            # (/communes require exact match on name..)
            city_code_resp = requests.get(
                "https://api-adresse.data.gouv.fr/search/",
                params=dict(q=city, type="municipality", postcode=postcode, limit=1),
            )
            city_code_resp.raise_for_status()
            found_cities = city_code_resp.json()["features"]
            if len(found_cities) < 1:
                raise KeyError("Combinaison Commune/CP inconnue")
            city_insee_code = found_cities[0]["properties"]["citycode"]

            city_resp = requests.get(
                f"{base_url}/communes/{city_insee_code}",
                params=dict(fields="epci"),
            )
            city_resp.raise_for_status()
            epci_label = city_resp.json()["epci"]["nom"]

    except (requests.HTTPError, requests.ConnectionError) as e:
        logger.warning(f"Erreur en requêtant {e.request.url} : {e}")
        return "INCONNU (pas de réponse API)"

    except KeyError as e:
        return f"INCONNU ({e})"
    else:
        return epci_label


def iter_situations_durations(
    ud: UserDatas,
    until_date: date,
) -> Iterable[Tuple[CaeSituationOption, datetime.timedelta]]:
    """
    Yields the duration of each successive situation in the career path

    A situation can span accross several CareerPath in two cases :
    - if CareerPath.cae_situation is None
    - if two consecutive CareerPath have the same CareerPath.cae_situation

    This function considers those siblings as a single duration.
    """
    career_steps = (
        CareerPath.query()
        .join(CareerPath.cae_situation)
        .filter(CareerPath.userdatas == ud)
        .filter(CareerPath.start_date <= until_date)
    ).all()
    # Cannot manage to SQL-sort it, don't know why…
    career_steps.sort(key=lambda x: x.start_date)

    prev_step = None
    situation_start = None

    for step in career_steps:
        if not prev_step:
            situation_start = step.start_date
        # step.cae_situation == None means no change in situation, keep going with current one
        elif (step.cae_situation is not None) and (
            step.cae_situation != prev_step.cae_situation
        ):
            if prev_step.end_date:
                situation_stop = min(step.start_date, prev_step.end_date)
            else:
                situation_stop = step.start_date
            yield prev_step.cae_situation, (situation_stop - situation_start)
            situation_start = step.start_date
        prev_step = step

    # Last step
    if prev_step is not None:  # may be zero steps in query
        if prev_step.end_date:
            situation_stop = min(prev_step.end_date, until_date)
        else:
            situation_stop = until_date
        yield prev_step.cae_situation, (situation_stop - situation_start)


def iter_hours_change(ud: UserDatas) -> Iterable[Tuple[date, float]]:
    """
    Yields all hours change with its date

    Iterate career steps and yield the date and new hour count each time a step
    introduce a change in num_hours.
    """
    career_steps = (CareerPath.query().filter(CareerPath.userdatas == ud)).all()
    # Cannot manage to SQL-sort it, don't know why…
    career_steps.sort(key=lambda x: x.start_date)
    for step in career_steps:
        if step.num_hours:
            hours_per_day = step.num_hours * 12 / 365
            yield step.start_date, hours_per_day
        elif step.stage_type == "exit":
            yield step.start_date, 0


def get_num_hours_worked(ud: UserDatas, start_date, end_date) -> int:
    """
    Returns the number of hours worked within a time period

    Based on the contract hours number across time.
    If end_date is in the future, result is a projection.

    :param start_date: inclusive (the worked hours for the start date are counted)
    :param end_date: exclusive (the worked hours for the end date are not counted, you
       may want to add +1 day to this arg)
    """
    total_hours = 0
    current_hours_per_day = 0
    period_start_date = start_date
    for effect_date, new_hours_per_day in iter_hours_change(ud):
        if effect_date < end_date:
            if effect_date >= start_date:
                nb_days = (effect_date - period_start_date).days
                hours_to_add = current_hours_per_day * nb_days
                assert hours_to_add >= 0
                total_hours += hours_to_add
            # Start a new period
            current_hours_per_day = new_hours_per_day
            period_start_date = max(effect_date, start_date)

    if period_start_date < end_date:
        nb_days = (end_date - period_start_date).days
        hours_to_add = current_hours_per_day * nb_days
        assert hours_to_add >= 0
        total_hours += hours_to_add

    return int(total_hours)


def collect_activity_typologies(ud: UserDatas) -> list[dict]:
    """Collect all activity typologies related to a user

    Sources are :
    - the typology set on user profile (UserDatas)
    - the typologies set on the activities list of profile (UserDatas)
    - the typologies set on each company linked to the user
    """
    out = []
    out.append(
        dict(
            source="userdatas",
            rank=0,
            typology=ud.activity_typologie.label if ud.activity_typologie else "",
        )
    )
    for idx, companydata in enumerate(ud.activity_companydatas):
        if companydata.activity:  # Skip if activity is not filled
            out.append(
                dict(
                    source="userdatas_activities",
                    rank=idx,
                    typology=companydata.activity.label,
                )
            )

    # Ignore internal company
    companies = [i for i in ud.user.companies if not i.internal]
    # Put active companies first
    companies.sort(key=lambda c: not c.active)

    for company in companies:
        for idx, activity in enumerate(company.activities):
            out.append(
                dict(
                    source="company",
                    rank=idx,
                    typology=activity.label,
                )
            )

    return out
