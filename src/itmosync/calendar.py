from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from icalendar import Calendar, Event
from itmo_schedule import Lesson

from .settings import settings


def _init_calendar(name: str, refresh_interval: int = 30) -> Calendar:
    calendar = Calendar()

    calendar.add("prodid", "-//volychev//itmosync//EN")
    calendar.add("version", "2.0")
    calendar.add("x-wr-calname", name)
    calendar.add("x-wr-timezone", "Europe/Moscow")

    refresh_duration: str = f"PT{refresh_interval}M"
    calendar.add("x-published-ttl", refresh_duration)                   # Apple
    calendar.add("refresh-interval;value=duration", refresh_duration)   # Google / Outlook

    return calendar


def _create_event(lesson: Lesson, now: datetime, namespace: UUID) -> Event:
    identity = f"{lesson.source_type}|{lesson.subject}|{lesson.start.isoformat()}"

    event = Event()
    event.add("uid", f"{uuid5(namespace, identity)}@itmosync")
    event.add("dtstamp", now)
    event.add("dtstart", lesson.start.astimezone(UTC))
    event.add("dtend", lesson.end.astimezone(UTC))

    context = {
        "title": lesson.subject,
        "type": settings.type_names.get(lesson.source_type, lesson.source_type),
        "label": settings.labels.get(lesson.source_type, settings.default_label),
        "teacher": lesson.teacher or "Не указан",
        "location": lesson.location or "Не указано",
        "url": lesson.url or "Не указана",
    }

    summary = settings.summary_template.format(**context).strip()
    event.add("summary", summary)

    raw_description = settings.description_template.format(**context)
    description = "\n".join(line for line in raw_description.splitlines() if line.strip())

    if description:
        event.add("description", description)

    if settings.include_location and lesson.location:
        event.add("location", lesson.location)

    if settings.include_url_field and lesson.url:
        event.add("url", lesson.url)

    return event


def render_calendar(lessons: Iterable[Lesson], name: str) -> bytes:
    calendar = _init_calendar(name)
    now = datetime.now(UTC)

    for lesson in lessons:
        event = _create_event(lesson, now, NAMESPACE_URL)
        calendar.add_component(event)

    return calendar.to_ical()
