from selenium.webdriver.remote.webdriver import WebDriver

from wbcore.contrib.example_app.factories import (
    LeagueFactory,
    SportPersonFactory,
    TeamFactory,
)
from wbcore.contrib.example_app.models import League, Sport, Team
from wbcore.contrib.example_app.serializers import (
    LeagueModelSerializer,
    SportPersonModelSerializer,
    TeamModelSerializer,
)
from wbcore.test import (
    click_element_by_path,
    fill_out_form_fields,
    open_create_instance,
)


def create_new_league_instance(
    driver: WebDriver, field_list: list[str], sport: Sport, is_create_instance_open=True
) -> League:
    if not is_create_instance_open:
        open_create_instance(driver, "Sports App", create_instance_title="Create League")

    league: dict = LeagueFactory.build(sport=sport)
    serializer = LeagueModelSerializer(league)
    fill_out_form_fields(driver, serializer, field_list, league)
    click_element_by_path(driver, "//button[@label='Save and close']")
    return league


def create_new_team_instance(driver: WebDriver, field_list: list[str], is_create_instance_open=True) -> Team:
    if not is_create_instance_open:
        open_create_instance(driver, "Sports App", create_instance_title="Create Team")

    team: dict = TeamFactory.build()
    serializer = TeamModelSerializer(team)
    fill_out_form_fields(driver, serializer, field_list, team)
    click_element_by_path(driver, "//button[@label='Save and close']")
    return team


def create_new_person_instance(driver: WebDriver, field_list: list[str], is_create_instance_open=True):
    if not is_create_instance_open:
        open_create_instance(driver, "Sports App", "Persons", create_instance_title="Create Person")
    person: dict = SportPersonFactory.build()
    serializer = SportPersonModelSerializer(person)
    fill_out_form_fields(driver, serializer, field_list, person)
    click_element_by_path(driver, "//button[@label='Save and close']")
    return person
