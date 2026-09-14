from pathlib import Path
from typing import Any

from itmo_schedule import LessonType
from pydantic import BaseModel, Field, SecretStr, model_validator
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
        if isinstance(data, dict) and 'match' not in data and len(data) == 1:
            k, v = next(iter(data.items()))
            return {'match': k, 'to': v}
        return data

class TemplateEventsConfig(BaseModel):
    summary: str = "{label} {title} — {type}. {format}"
    description: str = "Преподаватель: {teacher}\n\n{note}"

class TemplateBookingsConfig(BaseModel):
    summary: str = "{label} Бронирование: {title}"
    description: str = "{format}\n\n{note}"

class TemplatesConfig(BaseModel):
    events: TemplateEventsConfig = Field(default_factory=TemplateEventsConfig)
    bookings: TemplateBookingsConfig = Field(default_factory=TemplateBookingsConfig)

class RulesConfig(BaseModel):
    ignore: list[MatchRule | str] = Field(default_factory=list)
    renames: list[RenameRule] = Field(default_factory=list)

class AppearanceConfig(BaseModel):
    type_names: dict[str, str] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    format_labels: dict[int, str] = Field(default_factory=dict)
    default_label: str = "📝"

class SystemConfig(BaseModel):
    fetch_start: str = "09-01"
    fetch_end: str = "06-30"
    default_calendar_prefix: str = "ИТМО"
    include_location: bool = True
    include_url: bool = True

def _get_yaml_files() -> tuple[str, ...]:
    files = []
    config_dir = Path("config")

    if config_dir.exists() and config_dir.is_dir():
        for file in sorted(config_dir.iterdir()):
            if file.suffix in (".yaml", ".yml"):
                files.append(str(file))

    if Path("config.yaml").exists():
        files.append("config.yaml")

    return tuple(files) if files else ("config.yaml",)

class Config(BaseSettings):
    url_hash: SecretStr = Field(default=SecretStr(""))
    username: SecretStr = Field(default=SecretStr(""))
    password: SecretStr = Field(default=SecretStr(""))

    templates: TemplatesConfig = Field(default_factory=TemplatesConfig)
    rules: RulesConfig = Field(default_factory=RulesConfig)
    appearance: AppearanceConfig = Field(default_factory=AppearanceConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)

    model_config = SettingsConfigDict(
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
        yaml_files = _get_yaml_files()
        yaml_source = YamlConfigSettingsSource(settings_cls, yaml_file=yaml_files)
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            yaml_source,
        )

config = Config()
