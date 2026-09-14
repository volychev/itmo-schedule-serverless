from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from icalendar import Calendar, Event
from itmo_schedule import Lesson, LessonType

from .config import config


def _init_calendar(name: str) -> Calendar:
    calendar = Calendar()

    calendar.add("prodid", "-//volychev//itmo-sync//EN")
    calendar.add("version", "2.0")
    calendar.add("x-wr-calname", name)
    calendar.add("x-wr-timezone", "Europe/Moscow")

    return calendar


def _create_event(lesson: Lesson, now: datetime, namespace: UUID) -> Event:
    identity = f"{lesson.source_type}|{lesson.subject}|{lesson.start.isoformat()}"

    event = Event()
    event.add("uid", f"{uuid5(namespace, identity)}@itmo-sync")
    event.add("dtstamp", now)
    event.add("dtstart", lesson.start.astimezone(UTC))
    event.add("dtend", lesson.end.astimezone(UTC))

    source_type_key = lesson.source_type.name if isinstance(lesson.source_type, LessonType) else lesson.source_type

    context = {
        "title": lesson.subject,
        "type": config.appearance.type_names.get(source_type_key, lesson.source_type),
        "label": config.appearance.labels.get(source_type_key, config.appearance.default_label),
        "teacher": lesson.teacher or "Не указан",
        "teacher_short": _get_teacher_short(lesson.teacher),
        "location": lesson.location or "Не указано",
        "url": lesson.url or "Не указана",
        "format": config.appearance.format_labels.get(lesson.format_id, ""),
        "note": lesson.note or "",
    }

    if lesson.source_type == LessonType.BOOKING:
        summary_tpl = config.templates.bookings.summary
        desc_tpl = config.templates.bookings.description
    else:
        summary_tpl = config.templates.events.summary
        desc_tpl = config.templates.events.description

    summary = summary_tpl.format(**context).strip()
    event.add("summary", summary)

    raw_description = desc_tpl.format(**context)
    description = "\n".join(line for line in raw_description.splitlines() if line.strip())

    if description:
        event.add("description", description)

    if config.system.include_location and lesson.location:
        event.add("location", lesson.location)

    if config.system.include_url and lesson.url:
        event.add("url", lesson.url)

    return event


def _get_teacher_short(full_name: str | None) -> str:
    if not full_name:
        return "Не указан"

    parts = full_name.strip().split()

    if len(parts) >= 3:
        return f"{parts[0]} {parts[1][0]}. {parts[2][0]}."
    elif len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."

    return full_name


def render_calendar(lessons: Iterable[Lesson], name: str = "ИТМО") -> bytes:
    calendar = _init_calendar(name)
    now = datetime.now(UTC)

    for lesson in lessons:
        event = _create_event(lesson, now, NAMESPACE_URL)
        calendar.add_component(event)

    return calendar.to_ical()
