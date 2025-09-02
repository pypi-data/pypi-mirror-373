from cheshirecat_python_sdk.clients import HttpClient, WSClient
from cheshirecat_python_sdk.configuration import Configuration
from cheshirecat_python_sdk.endpoints import (
    AdminsEndpoint,
    AuthHandlerEndpoint,
    ChunkerEndpoint,
    CustomEndpoint,
    EmbedderEndpoint,
    FileManagerEndpoint,
    LargeLanguageModelEndpoint,
    MemoryEndpoint,
    MessageEndpoint,
    PluginsEndpoint,
    RabbitHoleEndpoint,
    SettingsEndpoint,
    UsersEndpoint,
    VectorDatabaseEndpoint,
)


class CheshireCatClient:
    def __init__(self, configuration: Configuration, token: str | None = None):
        self.__http_client = HttpClient(
            host=configuration.host,
            port=configuration.port,
            apikey=configuration.auth_key,
            is_https=configuration.secure_connection
        )
        self.__ws_client = WSClient(
            host=configuration.host,
            port=configuration.port,
            apikey=configuration.auth_key,
            is_wss=configuration.secure_connection
        )

        if token:
            self.add_token(token)

    def add_token(self, token: str) -> 'CheshireCatClient':
        self.__ws_client.set_token(token)
        self.__http_client.set_token(token)
        return self

    @property
    def http_client(self) -> HttpClient:
        return self.__http_client

    @property
    def ws_client(self) -> WSClient:
        return self.__ws_client

    @property
    def admins(self):
        return AdminsEndpoint(self)

    @property
    def auth_handler(self):
        return AuthHandlerEndpoint(self)

    @property
    def chunker(self):
        return ChunkerEndpoint(self)

    @property
    def embedder(self):
        return EmbedderEndpoint(self)

    @property
    def file_manager(self):
        return FileManagerEndpoint(self)

    @property
    def large_language_model(self):
        return LargeLanguageModelEndpoint(self)

    @property
    def memory(self):
        return MemoryEndpoint(self)

    @property
    def message(self):
        return MessageEndpoint(self)

    @property
    def plugins(self):
        return PluginsEndpoint(self)

    @property
    def rabbit_hole(self):
        return RabbitHoleEndpoint(self)

    @property
    def settings(self):
        return SettingsEndpoint(self)

    @property
    def users(self):
        return UsersEndpoint(self)

    @property
    def custom(self):
        return CustomEndpoint(self)

    @property
    def vector_database(self):
        return VectorDatabaseEndpoint(self)
