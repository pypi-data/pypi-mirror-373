import os
from typing import Tuple, Type
from pydantic_settings import BaseSettings, JsonConfigSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict
from Client.constants import configDirectory
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext
from Client.model.settings.rps_settings import RPSSettings
from Client.model.settings.files_settings import FilesSettings

class Settings(BaseSettings):
    """Settings for the Client library.
    This class is used to load configuration settings from environment variables,
    JSON files, and other sources. It includes settings for the RPS platform,
    rights contexts, processing contexts, and external source files.
    
    Attributes:
        rps (RpsSettings): Settings related to the RPS system.
        rights_contexts (dict[str, RightsContext]): Dictionary of rights contexts, keyed by context name.
        processing_contexts (dict[str, ProcessingContext]): Dictionary of processing contexts, keyed by context name.
        external_source_files (FilesSettings): Settings for external source files, if any.
    """
    rps: RPSSettings
    rights_contexts: dict[str, RightsContext] | None = None
    processing_contexts: dict[str, ProcessingContext] | None = None
    external_source_files: FilesSettings | None = None
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(configDirectory, ".env"),
        json_file=[os.path.join(configDirectory, "settings.json")],
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls),
            init_settings,
        )