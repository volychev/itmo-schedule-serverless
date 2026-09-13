from enum import IntEnum, StrEnum


class LessonType(StrEnum):
    LECTURE = "Лекции"

    PRACTICAL = "Практические занятия"
    LAB = "Лабораторные занятия"

    SPORT = "Занятия спортом"
    EXTERNAT = "Экстернат"

    EXAM = "Экзамен"
    CREDIT = "Зачет"
    GRADED_CREDIT = "Дифференцированный зачет"

    CONSULTATION = "Консультация"

    BOOKING = "Бронирования"


class WorkTypeId(IntEnum):
    LECTURE = 1
    LAB = 2
    PRACTICAL = 3
    EXAM = 5
    CREDIT = 6
    CONSULTATION = 10
    SPORT = 11


class FlowTypeId(IntEnum):
    LESSON = 2
    SPORT = 3
    BOOKING = 5


class FormatId(IntEnum):
    IN_PERSON = 2
    HYBRID = 1
    REMOTE = 3
