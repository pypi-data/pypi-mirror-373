import factory
import pytz
from faker import Faker

from wbcore.contrib.agenda.factories import CalendarItemFactory
from wbcore.contrib.example_app.models import Match

fake = Faker()


class MatchFactory(CalendarItemFactory):
    class Meta:
        model = Match

    home = factory.SubFactory("wbcore.contrib.example_app.factories.TeamFactory")
    away = factory.SubFactory("wbcore.contrib.example_app.factories.TeamFactory")

    date_time = factory.LazyAttribute(lambda _: fake.date_time(tzinfo=pytz.utc))
    stadium = factory.SubFactory("wbcore.contrib.example_app.factories.StadiumFactory")
    status = factory.Faker("random_element", elements=[x[0] for x in Match.MatchStatus])
    score_home = factory.Faker("pyint", min_value=0, max_value=1000)
    score_away = factory.Faker("pyint", min_value=0, max_value=1000)
    referee = factory.SubFactory("wbcore.contrib.example_app.factories.SportPersonFactory")
    league = factory.SubFactory("wbcore.contrib.example_app.factories.LeagueFactory")
    sport = factory.SelfAttribute(".league.sport")
    task_id = factory.Faker("text", max_nb_chars=50)
