from pydantic import BaseModel, Field
from maleo.enums.environment import Environment
from maleo.types.base.dict import OptionalStringToStringDict
from maleo.types.base.string import OptionalString


class DatabaseIdentifierConfig(BaseModel):
    enabled: bool = Field(True, description="Whether the database is enabled")
    environment: Environment = Field(..., description="Database's environment")
    name: str = Field(..., description="Database's name")
    description: OptionalString = Field(None, description="Database's description")
    tags: OptionalStringToStringDict = Field(None, description="Database's tags")
