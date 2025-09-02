from slugify import slugify

from wbcore.contrib.example_app.models import EventType


def get_event_types_for_league(league_id: int) -> list[dict[str, int | str]]:
    """Retrieves all event types involved inside a league

    Args:
        league_id (str): ID of the league in question

    Returns:
        list[dict[int,str, str]]: A list of dictionaries with the event type's id, name and slugified name
    """

    event_types = (
        EventType.objects.filter(sport__leagues=league_id, events__isnull=False).distinct().values("id", "name")
    )
    for event_type in event_types:
        event_type["slugified_name"] = slugify(event_type["name"], separator="_")
    return event_types
