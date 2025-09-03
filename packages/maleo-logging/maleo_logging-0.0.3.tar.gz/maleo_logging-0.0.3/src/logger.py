import logging
import os
from datetime import datetime, timezone
from typing import Literal, Optional, Union, overload
from maleo.enums.environment import Environment
from maleo.enums.service import Key
from maleo.types.base.dict import OptionalStringToStringDict
from maleo.types.base.string import OptionalString
from .dtos import Labels
from maleo.utils.merger import merge_dicts
from .enums import Level, LoggerType
from .google import GoogleCloudLogging


class Base(logging.Logger):
    def __init__(
        self,
        type: LoggerType,
        dir: str,
        *,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        client_key: OptionalString = None,
        level: Level = Level.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        self._type = type  # Declare logger type

        # Ensure environment exists
        actual_environment = environment or os.getenv("ENVIRONMENT")
        if actual_environment is None:
            raise ValueError(
                "ENVIRONMENT environment variable must be set if 'environment' is set to None"
            )
        else:
            self._environment = Environment(actual_environment)

        # Ensure service_key exists
        actual_service_key = service_key or os.getenv("SERVICE_KEY")
        if actual_service_key is None:
            raise ValueError(
                "SERVICE_KEY environment variable must be set if 'service_key' is set to None"
            )
        else:
            self._service_key = Key(actual_service_key)

        self._client_key = client_key  # Declare client key

        # Ensure client_key is valid if logger type is a client
        if self._type == LoggerType.CLIENT and self._client_key is None:
            raise ValueError(
                "'client_key' parameter must be provided if 'logger_type' is 'client'"
            )

        # Define logger name
        base_name = f"{self._environment} - {self._service_key} - {self._type}"
        if self._type == LoggerType.CLIENT:
            self._name = f"{base_name} - {self._client_key}"
        else:
            self._name = base_name

        # Define log labels
        self._labels = Labels(
            logger_type=self._type,
            service_environment=self._environment,
            service_key=self._service_key,
            client_key=client_key,
        )

        super().__init__(self._name, level)  # Init the superclass's logger

        # Clear existing handlers to prevent duplicates
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.addHandler(console_handler)

        # Google Cloud Logging handler (If enabled)
        if google_cloud_logging is not None:
            final_labels = self._labels.model_dump(mode="json", exclude_none=True)
            if labels is not None:
                final_labels = merge_dicts(final_labels, labels)
            cloud_logging_handler = google_cloud_logging.create_handler(
                name=self._name.replace(" ", ""),
                labels=final_labels,
            )
            self.addHandler(cloud_logging_handler)
        else:
            self.warning(
                "Cloud logging is not configured. Will not add cloud logging handler"
            )

        # Define aggregate log directory
        if aggregate_file_name is not None:
            if not aggregate_file_name.endswith(".log"):
                aggregate_file_name += ".log"
            log_filename = os.path.join(self._log_dir, "aggregate", aggregate_file_name)

            # File handler
            file_handler = logging.FileHandler(log_filename, mode="a")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(file_handler)

        if inidividual_log:
            # Define log directory
            if self._type == LoggerType.CLIENT:
                log_dir = f"{self._type}/{self._client_key}"
            else:
                log_dir = f"{self._type}"
            self._log_dir = os.path.join(dir, log_dir)
            os.makedirs(self._log_dir, exist_ok=True)

            # Generate timestamped filename
            log_filename = os.path.join(
                self._log_dir,
                f"{datetime.now(tz=timezone.utc).isoformat(timespec="seconds")}.log",
            )

            # File handler
            file_handler = logging.FileHandler(log_filename, mode="a")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(file_handler)

    @property
    def type(self) -> str:
        return self._type

    @property
    def location(self) -> str:
        return self._log_dir

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def service(self) -> str:
        return self._service_key

    @property
    def client(self) -> OptionalString:
        return self._client_key

    @property
    def identity(self) -> str:
        return self._name

    @property
    def labels(self) -> Labels:
        return self._labels

    def dispose(self):
        """Dispose of the logger by removing all handlers."""
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()
        self.handlers.clear()


class Application(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level: Level = Level.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.APPLICATION,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Cache(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level: Level = Level.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.CACHE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Client(Base):
    def __init__(
        self,
        dir: str,
        client_key: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level: Level = Level.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.CLIENT,
            environment=environment,
            service_key=service_key,
            client_key=client_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Controller(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level: Level = Level.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.CONTROLLER,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Database(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level=Level.INFO,
        google_cloud_logging=None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.DATABASE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Exception(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level=Level.INFO,
        google_cloud_logging=None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.EXCEPTION,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Middleware(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level=Level.INFO,
        google_cloud_logging=None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.MIDDLEWARE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Repository(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level: Level = Level.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.REPOSITORY,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class Service(Base):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Key] = None,
        level: Level = Level.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.SERVICE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


@overload
def create(
    dir: str,
    type: Literal[LoggerType.APPLICATION],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Application: ...
@overload
def create(
    dir: str,
    type: Literal[LoggerType.CACHE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Cache: ...
@overload
def create(
    dir: str,
    type: Literal[LoggerType.CLIENT],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    client_key: str,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Client: ...
@overload
def create(
    dir: str,
    type: Literal[LoggerType.CONTROLLER],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Controller: ...
@overload
def create(
    dir: str,
    type: Literal[LoggerType.DATABASE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Database: ...
@overload
def create(
    dir: str,
    type: Literal[LoggerType.MIDDLEWARE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Middleware: ...
@overload
def create(
    dir: str,
    type: Literal[LoggerType.REPOSITORY],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Repository: ...
@overload
def create(
    dir: str,
    type: Literal[LoggerType.SERVICE],
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Service: ...
def create(
    dir: str,
    type: LoggerType = LoggerType.BASE,
    *,
    environment: Optional[Environment] = None,
    service_key: Optional[Key] = None,
    client_key: OptionalString = None,
    level: Level = Level.INFO,
    google_cloud_logging: Optional[GoogleCloudLogging] = None,
    labels: OptionalStringToStringDict = None,
    aggregate_file_name: OptionalString = None,
    inidividual_log: bool = True,
) -> Union[
    Base,
    Application,
    Cache,
    Client,
    Controller,
    Database,
    Exception,
    Middleware,
    Repository,
    Service,
]:
    if type not in LoggerType:
        raise ValueError(f"Invalid logger type of '{type}'")

    if type is LoggerType.BASE:
        return Base(
            type=type,
            dir=dir,
            environment=environment,
            service_key=service_key,
            client_key=client_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.APPLICATION:
        return Application(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.CACHE:
        return Cache(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.CLIENT:
        if client_key is None:
            raise ValueError(
                "Argument 'client_key' can not be None if 'logger_type' is 'client'"
            )
        return Client(
            dir=dir,
            client_key=client_key,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.CONTROLLER:
        return Controller(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.DATABASE:
        return Database(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.EXCEPTION:
        return Exception(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.MIDDLEWARE:
        return Middleware(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.REPOSITORY:
        return Repository(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
    elif type is LoggerType.SERVICE:
        return Service(
            dir=dir,
            environment=environment,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
