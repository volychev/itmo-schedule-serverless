from enum import StrEnum


class LessonType(StrEnum):
    LECTURE = "Лекции"

    PRACTICAL = "Практические занятия"
    LAB = "Лабораторные занятия"

    SPORT = "Занятия спортом"
    EXTERNAT = "Экстернат"

    EXAM = "Экзамен"
    CREDIT = "Зачет"
    GRADED_CREDIT = "Дифференцированный зачет"
    CONSULTATION = "Консультация к экзамену"
