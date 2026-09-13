from dataclasses import dataclass
from datetime import datetime


@dataclass
class Lesson:
    subject: str
    start: datetime
    end: datetime
    source_type: str
    teacher: str | None = None
    location: str | None = None
    url: str | None = None


@dataclass
class Schedule:
    lectures: tuple[Lesson, ...] = ()
    practicals_and_labs: tuple[Lesson, ...] = ()
    sports: tuple[Lesson, ...] = ()
    exams: tuple[Lesson, ...] = ()
    unclassified: tuple[Lesson, ...] = ()
