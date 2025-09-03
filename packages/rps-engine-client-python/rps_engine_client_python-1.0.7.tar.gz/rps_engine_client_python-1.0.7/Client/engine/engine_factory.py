"""Get the RPS Engine class after all configuration."""
from Client.auth.credentials_token_provider import ClientCredentialsTokenProvider
from Client.context_source import ContextSource
from Client.engine.rps_engine import RPSEngine
from Client.engine.rps_engine_converter import RPSEngineConverter
from Client.engine_client_options import EngineClientOptions
from Client.engine_context.rps_engine_context_json_file_provider import RPSEngineContextJsonFileProvider
from Client.engine_context.rps_engine_context_resolver import RPSEngineContextResolver
from Client.engine_context.rps_engine_context_settings_provider import RPSEngineContextSettingsProvider
from Client.json.engine_json_rest_api_client import EngineJsonRestApiClient
from Client.settings import Settings


class EngineFactory:
    """
    Factory for creating a fully configured RPSEngine instance.

    This class encapsulates the logic for assembling all required components and dependencies
    for the RPS Engine, including authentication, client options, and context resolver.
    The context resolver can be constructed from either JSON files or in-memory settings,
    depending on the selected ContextSource.

    Usage example:
        engine = EngineFactory.get_engine(ContextSource.JSON)
        # or
        engine = EngineFactory.get_engine(ContextSource.SETTINGS)
    """
    @classmethod
    def get_engine(cls, context_source: "ContextSource" = ContextSource.JSON) -> "RPSEngine":
        """
        Create and return a configured RPSEngine instance.

        This method assembles all required dependencies for the engine, including authentication,
        client options, and the context resolver. The context resolver can be built from either
        JSON files or in-memory settings, depending on the context_source argument.

        Args:
            context_source (ContextSource, optional):
                Determines the source for context data. Use ContextSource.JSON to load from JSON files,
                or ContextSource.SETTINGS to use in-memory settings. Defaults to ContextSource.JSON.

        Returns:
            RPSEngine: A fully configured RPS Engine instance ready for use.

        Raises:
            ValueError: If required settings for the selected context source are missing or invalid.
        """
        settings = Settings()
        engine_client_options = EngineClientOptions(settings=settings)

        engine_provider = EngineJsonRestApiClient(engine_client_options,
                                                  ClientCredentialsTokenProvider(client_options=engine_client_options))

        builder = cls._CONTEXT_RESOLVER_BUILDERS.get(context_source)
        if not builder:
            raise ValueError(f"Unknown context_source: {context_source}. Use ContextSource.JSON or ContextSource.SETTINGS.")
        rps_engine_context_resolver = builder(settings)

        return RPSEngine(engine_provider, RPSEngineConverter(), rps_engine_context_resolver)

    @staticmethod
    def _create_json_context_resolver(settings: Settings) -> RPSEngineContextResolver:
        """
        Build a context resolver using JSON file providers.

        Args:
            settings (Settings): The settings object containing file paths.

        Returns:
            RPSEngineContextResolver: Resolver using JSON file providers.

        Raises:
            ValueError: If required file paths are missing in settings.
        """
        if not hasattr(settings, "external_source_files") or \
           not hasattr(settings.external_source_files, "rightsContextsFilePath") or \
           not hasattr(settings.external_source_files, "processingContextsFilePath"):
            raise ValueError("Missing required settings for JSON context provider: external_source_files.rightsContextsFilePath and external_source_files.processingContextsFilePath")
        
        return RPSEngineContextResolver(RPSEngineContextJsonFileProvider(
            settings.external_source_files.rightsContextsFilePath,
            settings.external_source_files.processingContextsFilePath))

    @staticmethod
    def _create_settings_context_resolver(settings: Settings) -> RPSEngineContextResolver:
        """
        Build a context resolver using in-memory settings providers.

        Args:
            settings (Settings): The settings object containing context data.

        Returns:
            RPSEngineContextResolver: Resolver using in-memory settings providers.

        Raises:
            ValueError: If required context data is missing in settings.
        """
        if not hasattr(settings, "rights_contexts") or not hasattr(settings, "processing_contexts"):
            raise ValueError("Missing required settings for settings context provider: rights_contexts and processing_contexts")
        return RPSEngineContextResolver(RPSEngineContextSettingsProvider(
            settings.rights_contexts, settings.processing_contexts))

    _CONTEXT_RESOLVER_BUILDERS = {
        ContextSource.JSON: _create_json_context_resolver.__func__,
        ContextSource.SETTINGS: _create_settings_context_resolver.__func__,
    }