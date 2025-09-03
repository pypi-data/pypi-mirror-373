from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from maleo.enums.environment import Environment
from maleo.enums.service import Key
from maleo.types.base.string import OptionalString
from .enums import Level, LoggerType
from .google import GoogleCloudLogging


class Labels(BaseModel):
    logger_type: LoggerType = Field(..., description="Logger's type")
    service_environment: Environment = Field(..., description="Service's environment")
    service_key: Key = Field(..., description="Service's key")
    client_key: OptionalString = Field(None, description="Client's key (Optional)")


class SimpleConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dir: str = Field(..., description="Log's directory")
    level: Level = Field(Level.INFO, description="Log's level")
    google_cloud_logging: Optional[GoogleCloudLogging] = Field(
        default_factory=GoogleCloudLogging, description="Google cloud logging"
    )
