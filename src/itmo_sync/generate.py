from datetime import UTC, datetime
from pathlib import Path

from itmo_schedule import FormatId, Lesson, LessonType, get_schedule

from .config import MatchRule, RenameRule, config
from .ical import render_calendar
from .page import render_index


def _resolve_dates(start_mm_dd: str, end_mm_dd: str) -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    current_year = now.year

    start_month, start_day = map(int, start_mm_dd.split("-"))
    end_month, end_day = map(int, end_mm_dd.split("-"))

    start = datetime(current_year, start_month, start_day, tzinfo=UTC)
    end = datetime(current_year, end_month, end_day, tzinfo=UTC)

    if end < start:
        end = end.replace(year=current_year + 1)

    if start > now and (start - now).days > 180:
        start = start.replace(year=current_year - 1)
        end = end.replace(year=end.year - 1)

    return start, end


def _matches_rule(lesson: Lesson, rule: MatchRule | str) -> bool:
    if isinstance(rule, str):
        return lesson.subject == rule
    
    if rule.match != lesson.subject:
        return False
        
    if rule.type is not None:
        expected_type = rule.type.value if isinstance(rule.type, LessonType) else rule.type
        if isinstance(expected_type, str):
            try:
                expected_type = LessonType[expected_type].value
            except KeyError:
                pass
        
        if lesson.source_type != expected_type:
            return False
            
    if rule.format is not None:
        expected_format = rule.format
        if isinstance(expected_format, str):
            try:
                expected_format = FormatId[expected_format]
            except KeyError:
                pass

        if isinstance(expected_format, FormatId):
            if lesson.format_id != expected_format.value:
                return False
        else:
            lesson_format = config.appearance.format_labels.get(lesson.format_id, "")
            if lesson_format != expected_format:
                return False
            
    return True


async def generate_calendars(base_output_dir: Path) -> None:
    start_date, end_date = _resolve_dates(config.system.fetch_start, config.system.fetch_end)
    username = config.username.get_secret_value()

    print(f"Fetching schedule from {start_date} to {end_date}...")

    schedule = await get_schedule(
        username=username,
        password=config.password.get_secret_value(),
        start=start_date,
        end=end_date,
    )

    output_dir = base_output_dir / config.url_hash.get_secret_value()
    output_dir.mkdir(parents=True, exist_ok=True)

    filtered_lectures = schedule.lectures
    filtered_practicals = schedule.practicals_and_labs
    filtered_sports = schedule.sports
    filtered_exams = schedule.exams
    filtered_bookings = schedule.bookings
    filtered_unclassified = schedule.unclassified

    if config.rules.ignore:
        def should_keep(lesson: Lesson) -> bool:
            return not any(_matches_rule(lesson, rule) for rule in config.rules.ignore)

        filtered_lectures = tuple(l for l in schedule.lectures if should_keep(l))
        filtered_practicals = tuple(l for l in schedule.practicals_and_labs if should_keep(l))
        filtered_sports = tuple(l for l in schedule.sports if should_keep(l))
        filtered_exams = tuple(l for l in schedule.exams if should_keep(l))
        filtered_bookings = tuple(l for l in schedule.bookings if should_keep(l))
        filtered_unclassified = tuple(l for l in schedule.unclassified if should_keep(l))

    if config.rules.renames:
        for group in (filtered_lectures, filtered_practicals, filtered_sports, filtered_exams, filtered_bookings, filtered_unclassified):
            for lesson in group:
                for rule in config.rules.renames:
                    if _matches_rule(lesson, rule):
                        lesson.subject = rule.to

    categories = {
        "general": (
            filtered_lectures
            + filtered_practicals
            + filtered_sports
            + filtered_exams
            + filtered_bookings
            + filtered_unclassified
        ),
        "lectures": filtered_lectures,
        "practicals": filtered_practicals,
        "sports": filtered_sports,
        "exams": filtered_exams,
        "bookings": filtered_bookings,
        "unclassified": filtered_unclassified,
    }

    print(f"Total lessons (general): {len(categories['general'])}. Generating files...")

    file_info = []

    for category_name, lessons in categories.items():
        ical_data = render_calendar(lessons, name=f"{config.system.default_calendar_prefix}: {category_name.capitalize()}")

        file_name = f"{category_name}.ics"
        file_path = output_dir / file_name
        file_path.write_bytes(ical_data)

        file_info.append({
            "name": category_name,
            "filename": file_name,
            "count": len(lessons),
            "emoji": "📚" if category_name == "general" else "📅"
        })

    html_content = render_index(
        file_info=file_info,
        start_date=start_date.strftime("%d.%m.%Y"),
        end_date=end_date.strftime("%d.%m.%Y"),
        last_updated=datetime.now(UTC).strftime("%d.%m.%Y %H:%M UTC"),
    )
    (output_dir / "index.html").write_text(html_content, encoding="utf-8")

    print(f"✅ Calendars and index.html successfully saved to {output_dir}")
