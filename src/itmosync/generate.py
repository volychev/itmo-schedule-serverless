from datetime import UTC, datetime
from pathlib import Path

from itmo_schedule import get_schedule

from .html import render_index
from .ical import render_calendar
from .settings import settings


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


async def generate_calendars(base_output_dir: Path) -> None:
    start_date, end_date = _resolve_dates(settings.fetch_start, settings.fetch_end)
    username = settings.username.get_secret_value()

    print(f"Fetching schedule from {start_date} to {end_date}...")

    schedule = await get_schedule(
        username=username,
        password=settings.password.get_secret_value(),
        start=start_date,
        end=end_date,
    )

    output_dir = base_output_dir / settings.url_hash.get_secret_value()
    output_dir.mkdir(parents=True, exist_ok=True)

    categories = {
        "general": (
            schedule.lectures
            + schedule.practicals_and_labs
            + schedule.sports
            + schedule.exams
            + schedule.unclassified
        ),
        "lectures": schedule.lectures,
        "practicals": schedule.practicals_and_labs,
        "sports": schedule.sports,
        "exams": schedule.exams,
        "unclassified": schedule.unclassified,
    }

    print(f"Total lessons (general): {len(categories['general'])}. Generating files...")

    file_info = []

    for category_name, lessons in categories.items():
        ical_data = render_calendar(lessons, name=f"{settings.default_calendar_prefix}: {category_name.capitalize()}")

        file_name = f"{category_name}.ics"
        file_path = output_dir / file_name
        file_path.write_bytes(ical_data)

        file_info.append({
            "name": category_name,
            "filename": file_name,
            "count": len(lessons),
            "emoji": "📚" if category_name == "general" else "📅"
        })

    html_content = render_index(file_info)
    (output_dir / "index.html").write_text(html_content, encoding="utf-8")

    print(f"✅ Calendars and index.html successfully saved to {output_dir}")
