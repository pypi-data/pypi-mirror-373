from google.cloud.logging import Client
from google.cloud.logging.handlers import CloudLoggingHandler
from google.oauth2.service_account import Credentials
from pathlib import Path
from typing import Optional, Union
from maleo.types.base.dict import OptionalStringToStringDict
from maleo.utils.loaders.credential.google import load


class GoogleCloudLogging:
    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        credentials_path: Optional[Union[Path, str]] = None,
    ) -> None:
        if credentials is not None and credentials_path is not None:
            raise ValueError(
                "Only either 'credentials' or 'credentials_path' can be passed as parameter"
            )

        if credentials is not None:
            self._credentials = credentials
        else:
            self._credentials = load(credentials_path)

        self._client = Client(credentials=self._credentials)
        self._client.setup_logging()

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    @property
    def client(self) -> Client:
        return self._client

    def dispose(self) -> None:
        if self._client is not None:
            self._client.close

    def create_handler(
        self, name: str, labels: OptionalStringToStringDict = None
    ) -> CloudLoggingHandler:
        return CloudLoggingHandler(client=self._client, name=name, labels=labels)
