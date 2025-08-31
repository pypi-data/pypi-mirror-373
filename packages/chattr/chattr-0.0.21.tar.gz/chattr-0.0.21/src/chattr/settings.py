"""This module contains the settings for the Chattr app."""

from json import loads
from pathlib import Path
from typing import Self

from dotenv import load_dotenv
from jsonschema import validate
from loguru import logger
from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    FilePath,
    HttpUrl,
    SecretStr,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

logger.add(
    sink=Path.cwd() / "logs" / "chattr.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    colorize=True,
)


class ModelSettings(BaseModel):
    url: HttpUrl = Field(default=None)
    name: str = Field(default=None)
    api_key: SecretStr = Field(default=None)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    system_message: str = Field(
        default="You are a helpful assistant that can answer questions about the time and generate audio files from text."
    )

    @model_validator(mode="after")
    def check_api_key_exist(self) -> Self:
        """
        Ensure that an API key and model name are provided if a model URL is set.
        This method validates the presence of required credentials for the model provider.

        Returns:
            Self: The validated ModelSettings instance.

        Raises:
            ValueError: If the API key or model name is missing when a model URL is provided.
        """
        if self.url:
            if not self.api_key or not self.api_key.get_secret_value():
                raise ValueError(
                    "You need to provide API Key for the Model provider via `MODEL__API_KEY`"
                )
            if not self.name:
                raise ValueError("You need to provide Model name via `MODEL__NAME`")
        return self


class MemorySettings(BaseModel):
    collection_name: str = Field(default="memories")
    embedding_dims: int = Field(default=384)


class VectorDatabaseSettings(BaseModel):
    name: str = Field(default="chattr")
    url: HttpUrl = HttpUrl("http://localhost:6333")


class MCPSettings(BaseModel):
    path: FilePath = Field(default=None)
    schema_path: FilePath = Field(
        default_factory=lambda: Path.cwd() / "assets" / "mcp-config.json"
    )

    @model_validator(mode="after")
    def is_json(self) -> Self:
        """
        Validate that the MCP config file is a JSON file.
        This method checks the file extension of the provided MCP config path.

        Returns:
            Self: The validated MCPSettings instance.

        Raises:
            ValueError: If the MCP config file does not have a .json extension.
        """
        if self.path and self.path.suffix != ".json":
            raise ValueError("MCP config file must be a JSON file")
        return self

    @model_validator(mode="after")
    def check_mcp_config(self) -> Self:
        """
        Validate the MCP config file against its JSON schema.
        This method ensures the MCP config file matches the expected schema definition.

        Returns:
            Self: The validated MCPSettings instance.

        Raises:
            ValidationError: If the config file does not match the schema.
        """
        if self.path:
            validate(
                instance=loads(self.path.read_text(encoding="utf-8")),
                schema=loads(self.schema_path.read_text(encoding="utf-8")),
            )
        return self


class DirectorySettings(BaseModel):
    base: DirectoryPath = Field(default_factory=lambda: Path.cwd())
    assets: DirectoryPath = Field(default_factory=lambda: Path.cwd() / "assets")
    log: DirectoryPath = Field(default_factory=lambda: Path.cwd() / "logs")
    image: DirectoryPath = Field(
        default_factory=lambda: Path.cwd() / "assets" / "image"
    )
    audio: DirectoryPath = Field(
        default_factory=lambda: Path.cwd() / "assets" / "audio"
    )
    video: DirectoryPath = Field(
        default_factory=lambda: Path.cwd() / "assets" / "video"
    )

    @model_validator(mode="after")
    def create_missing_dirs(self) -> Self:
        """
        Ensure that all specified directories exist, creating them if necessary.
        This method checks and creates any missing directories defined in the DirectorySettings.

        Returns:
            Self: The validated DirectorySettings instance.
        """
        for directory in [
            self.base,
            self.assets,
            self.log,
            self.image,
            self.audio,
            self.video,
        ]:
            directory.mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
        return self


class Settings(BaseSettings):
    """Configuration for the Chattr app."""

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_parse_none_str="None",
        env_file=".env",
        extra="ignore",
    )

    model: ModelSettings = ModelSettings()
    memory: MemorySettings = MemorySettings()
    vector_database: VectorDatabaseSettings = VectorDatabaseSettings()
    mcp: MCPSettings = MCPSettings()
    directory: DirectorySettings = DirectorySettings()


if __name__ == "__main__":
    print(Settings().model_dump())
