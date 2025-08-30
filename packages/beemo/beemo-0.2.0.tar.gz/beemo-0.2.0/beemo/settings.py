from functools import cache
from pathlib import Path

import yaml
from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="beemo_")

    config: FilePath


class Config(BaseModel):
    root_path: DirectoryPath
    pages_dir: DirectoryPath | None = None
    posts_dir: DirectoryPath | None = None
    static_dir: DirectoryPath
    templates_dir: DirectoryPath
    output_dir: DirectoryPath
    blog_root: Path = Path()

    @field_validator(
        "pages_dir",
        "posts_dir",
        "static_dir",
        "templates_dir",
        "output_dir",
        mode="before",
    )
    @classmethod
    def make_relative(cls, value, info):
        if isinstance(value, str) and not Path(value).is_absolute():
            return info.data["root_path"] / value
        return value

    @model_validator(mode="after")
    def posts_or_pages_mode(self):
        if self.posts_dir is None and self.pages_dir is None:
            raise ValueError("Either posts_dir or pages_dir must be set")
        return self


@cache
def get_config() -> Config:
    settings = Settings()
    with open(settings.config, "r") as f:
        config = yaml.safe_load(f)
    config["root_path"] = settings.config.parent.absolute()
    return Config.model_validate(config)
