# itmo-schedule

__itmo-schedule__ is an asynchronous Python library for fetching personal ITMO schedules.

## Usage

```python
import asyncio
from datetime import date
from getpass import getpass

from itmo_schedule import get_schedule


async def main():
    username = input("ISU: ")
    password = getpass("Password: ")
    schedule = await get_schedule(
        username, password, date(2026, 9, 11), date(2026, 9, 13)
    )

    for lesson in schedule.lectures:
        print("Lecture:", lesson.start, lesson.subject)

    for lesson in schedule.practicals_and_labs:
        print("Practical/Lab:", lesson.start, lesson.subject)

    for lesson in schedule.sports:
        print("Sport:", lesson.start, lesson.subject)

    for lesson in schedule.exams:
        print("Exam/Credit:", lesson.start, lesson.subject)


asyncio.run(main())

```

`get_schedule(username, password, start, end)` logs in and fetches the schedule.

### Results

`Schedule` contains five tuples sorted by start time:

* `lectures`: Lectures (`Лекции`).
* `practicals_and_labs`: Practical and laboratory classes (`Практические занятия`, `Лабораторные занятия`).
* `sports`: Physical education and externat (`Занятия спортом`, `Экстернат`).
* `exams`: Exams, graded/ungraded credits, consultations (`Экзамен`, `Зачет`, `Дифференцированный зачет`, `Консультация к экзамену`).
* `unclassified`: Any other lesson types.

| Lesson field | Description |
| --- | --- |
| `subject` | Subject name. |
| `start`, `end` | Timezone-aware datetimes. |
| `source_type` | Raw lesson type string. |
| `teacher` | Teacher full name, or `None`. |
| `location` | Classroom and building, or `None`. |
| `url` | Online class link, or `None`. |

### Specifications

* Fetches classes in `[start, end)`.
* Skips classes with `end<=start`.

## Building and testing

```sh
uv sync --package itmo-schedule --locked
uv run --package itmo-schedule pytest packages/itmo-schedule/tests
uv build --package itmo-schedule

```

## Credits

Originally developed by [Timofey Smolyankin](https://github.com/madfanat) as part of [itmom](https://github.com/madfanat/itmom/tree/main/packages/itmo-schedule).
