from itmo_schedule import LessonType
from pydantic import Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


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

    refresh_interval: int = Field(
        default=30,
        ge=1,
        description="Интервал автообновления календаря в минутах",
    )

    default_calendar_prefix: str = Field(
        default="ИТМО",
        description="Префикс для названия календарей, который будет отображаться в приложении",
    )

    summary_template: str = Field(
        default="{label} {title} — {type}",
        min_length=1,
        description="Шаблон названия события (доступны: {label} (эмодзи), {title}, {type}, {teachers}, {location}, {url})",
    )

    description_template: str = Field(
        default="Преподаватель: {teacher}",
        description="Шаблон подробного описания события (поддерживает многострочный текст)",
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
            LessonType.LECTURE: "Лекция",             # Лекции
            LessonType.PRACTICAL: "Практика",         # Практические занятия
            LessonType.LAB: "Лабораторная",           # Лабораторные занятия
            LessonType.SPORT: "Спорт",                # Занятия спортом
            LessonType.EXTERNAT: "Экстернат",         # Экстернат
            LessonType.EXAM: "Экзамен",               # Экзамен
            LessonType.CREDIT: "Зачет",               # Зачет
            LessonType.GRADED_CREDIT: "Диф. зачет",   # Дифференцированный зачет
            LessonType.CONSULTATION: "Консультация",  # Консультация к экзамену
        },
        description="Маппинг системных типов пар в сокращенные названия",
    )

    labels: dict[str, str] = Field(
        default={
            LessonType.LECTURE: "📚",         # Лекции
            LessonType.PRACTICAL: "🧪",       # Практические занятия
            LessonType.LAB: "🔬",             # Лабораторные занятия
            LessonType.SPORT: "🏋️",           # Занятия спортом
            LessonType.EXTERNAT: "🌍",        # Экстернат
            LessonType.EXAM: "🔥",            # Экзамен
            LessonType.CREDIT: "✅",          # Зачет
            LessonType.GRADED_CREDIT: "💯",   # Дифференцированный зачет
            LessonType.CONSULTATION: "💬",    # Консультация к экзамену
        },
        description="Маппинг типов пар в эмодзи-метки",
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
        env_prefix="ITMOSCHEDULE_",
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
