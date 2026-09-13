from itmo_schedule import FormatId, LessonType
from pydantic import BaseModel, Field, SecretStr, model_validator
from typing import Any
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

class MatchRule(BaseModel):
    match: str
    type: LessonType | str | None = None
    format: str | None = None


class RenameRule(MatchRule):
    to: str

    @model_validator(mode='before')
    @classmethod
    def convert_dict(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if 'match' not in data and len(data) == 1:
                k, v = next(iter(data.items()))
                return {'match': k, 'to': v}
        return data


class Settings(BaseSettings):
    url_hash: SecretStr = Field(
        default=SecretStr(""),
        description="Уникальный путь (хэш) для генерации ссылок",
    )

    username: SecretStr = Field(
        default=SecretStr(""),
        description="Табельный номер / логин ИСУ студента",
    )

    password: SecretStr = Field(
        default=SecretStr(""),
        description="Пароль от аккаунта ИСУ",
    )

    fetch_start: str = Field(
        default="09-01",
        pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
        description="Месяц и день начала парсинга в формате ММ-ДД",
    )

    fetch_end: str = Field(
        default="06-30",
        pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
        description="Месяц и день конца парсинга в формате ММ-ДД",
    )

    default_calendar_prefix: str = Field(
        default="ИТМО",
        description="Префикс для названия календарей, который будет отображаться в приложении",
    )

    summary_template: str = Field(
        default="{label} {title} — {type}. {format}",
        min_length=1,
        description="Шаблон названия события (доступны: {label} (эмодзи), {title}, {type}, {teacher}, {location}, {url}, {format}, {note})",
    )

    description_template: str = Field(
        default="Преподаватель: {teacher}\n\n{note}",
        description="Шаблон подробного описания события (поддерживает многострочный текст)",
    )

    booking_summary_template: str = Field(
        default="{label} Бронирование: {title}",
        min_length=1,
        description="Шаблон названия события для бронирований",
    )

    booking_description_template: str = Field(
        default="{format}\n\n{note}",
        description="Шаблон подробного описания события для бронирований",
    )

    include_location: bool = Field(
        default=True,
        description="Заполнять ли стандартное поле геолокации/аудитории (LOCATION)",
    )

    include_url_field: bool = Field(
        default=True,
        description="Заполнять ли стандартное системное поле ссылки на пару (URL)",
    )

    type_names: dict[str, str] = Field(
        default={
            LessonType.LECTURE.name: "Лекция",             # Лекции
            LessonType.PRACTICAL.name: "Практика",         # Практические занятия
            LessonType.LAB.name: "Лабораторная",           # Лабораторные занятия
            LessonType.SPORT.name: "Спорт",                # Занятия спортом
            LessonType.EXTERNAT.name: "Экстернат",         # Экстернат
            LessonType.EXAM.name: "Экзамен",               # Экзамен
            LessonType.CREDIT.name: "Зачет",               # Зачет
            LessonType.GRADED_CREDIT.name: "Диф. зачет",   # Дифференцированный зачет
            LessonType.CONSULTATION.name: "Консультация",  # Консультация к экзамену
            LessonType.BOOKING.name: "Бронирование",       # Бронирования аудиторий
        },
        description="Маппинг системных типов пар в сокращенные названия",
    )

    ignore: list[MatchRule | str] = Field(
        default_factory=list,
        description="Правила для полного исключения предметов из календаря",
    )

    renames: list[RenameRule] = Field(
        default_factory=list,
        description="Правила для переименования предметов",
    )

    labels: dict[str, str] = Field(
        default={
            LessonType.LECTURE.name: "📚",         # Лекции
            LessonType.PRACTICAL.name: "🧪",       # Практические занятия
            LessonType.LAB.name: "🔬",             # Лабораторные занятия
            LessonType.SPORT.name: "🏋️",           # Занятия спортом
            LessonType.EXTERNAT.name: "🌍",        # Экстернат
            LessonType.EXAM.name: "🔥",            # Экзамен
            LessonType.CREDIT.name: "✅",          # Зачет
            LessonType.GRADED_CREDIT.name: "💯",   # Дифференцированный зачет
            LessonType.CONSULTATION.name: "💬",    # Консультация к экзамену
            LessonType.BOOKING.name: "🗓️",         # Бронирования аудиторий
        },
        description="Маппинг типов пар в эмодзи-метки",
    )

    format_labels: dict[int, str] = Field(
        default={
            FormatId.IN_PERSON: "Очно",
            FormatId.HYBRID: "Смешанный формат",
            FormatId.REMOTE: "Дистанционно",
        },
        description="Маппинг форматов проведения (id) в текст с эмодзи",
    )

    default_label: str = Field(
        default="📝",
        min_length=1,
        description="Метка по умолчанию для нераспознанных типов занятий",
    )

    model_config = SettingsConfigDict(
        yaml_file="settings.yaml",
        yaml_file_encoding="utf-8",
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ITMO_SYNC_",
        env_nested_delimiter="__",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
        )


settings = Settings()
