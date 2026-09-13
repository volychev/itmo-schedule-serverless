import asyncio
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from .enums import LessonType
from .models import Lesson, Schedule


async def parse_schedule(payload: dict[str, Any]) -> Schedule:
    if payload.get("code", 0) != 0:
        raise ValueError("Unsuccessful schedule response")

    timezone = ZoneInfo("Europe/Moscow")

    lectures = []
    practicals_and_labs = []
    sports = []
    exams = []
    unclassified = []

    for day in payload.get("data", []):
        date_str = day.get("date")

        for raw in day.get("lessons", []):
            start = datetime.fromisoformat(f"{date_str}T{raw['time_start']}").replace(tzinfo=timezone)
            end = datetime.fromisoformat(f"{date_str}T{raw['time_end']}").replace(tzinfo=timezone)

            if end <= start:
                continue

            location_parts = [raw[k] for k in ("room", "building") if raw.get(k)]

            raw_type = raw.get("type", "")
            raw_type_lower = raw_type.lower()

            if "лекц" in raw_type_lower:
                stype = LessonType.LECTURE
            elif "практ" in raw_type_lower:
                stype = LessonType.PRACTICAL
            elif "лаб" in raw_type_lower:
                stype = LessonType.LAB
            elif "спорт" in raw_type_lower or "физ" in raw_type_lower:
                stype = LessonType.SPORT
            elif "экстерн" in raw_type_lower:
                stype = LessonType.EXTERNAT
            elif "диф" in raw_type_lower and "зач" in raw_type_lower:
                stype = LessonType.GRADED_CREDIT
            elif "зач" in raw_type_lower:
                stype = LessonType.CREDIT
            elif "экзам" in raw_type_lower:
                stype = LessonType.EXAM
            elif "консульт" in raw_type_lower:
                stype = LessonType.CONSULTATION
            else:
                stype = raw_type.strip()

            lesson = Lesson(
                subject=raw.get("subject", "Без названия"),
                start=start,
                end=end,
                source_type=stype,
                teacher=raw.get("teacher_name") or raw.get("teacher_fio") or None,
                location=", ".join(location_parts) if location_parts else None,
                url=raw.get("zoom_url") or None,
            )

            if stype == LessonType.LECTURE:
                lectures.append(lesson)
            elif stype in (LessonType.PRACTICAL, LessonType.LAB):
                practicals_and_labs.append(lesson)
            elif stype in (LessonType.SPORT, LessonType.EXTERNAT):
                sports.append(lesson)
            elif stype in (LessonType.EXAM, LessonType.CREDIT, LessonType.GRADED_CREDIT, LessonType.CONSULTATION):
                exams.append(lesson)
            else:
                unclassified.append(lesson)

    await asyncio.sleep(0)

    sort_key = lambda x: x.start

    return Schedule(
        lectures=tuple(sorted(lectures, key=sort_key)),
        practicals_and_labs=tuple(sorted(practicals_and_labs, key=sort_key)),
        sports=tuple(sorted(sports, key=sort_key)),
        exams=tuple(sorted(exams, key=sort_key)),
        unclassified=tuple(sorted(unclassified, key=sort_key)),
    )
