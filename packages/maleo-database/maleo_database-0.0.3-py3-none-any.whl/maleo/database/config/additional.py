from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Union
from maleo.enums.cache import Origin, Layer
from maleo.enums.expiration import Expiration
from maleo.types.base.string import OptionalString


class RedisCacheNamespaces(BaseModel):
    base: str = Field(..., description="Base Redis's namespace")

    def create(
        self,
        *ext: str,
        origin: Origin,
        layer: Layer,
        base_override: OptionalString = None,
    ) -> str:
        return ":".join(
            [self.base if base_override is None else base_override, origin, layer, *ext]
        )


class BaseAdditionalConfig(BaseModel):
    """Base additional configuration class for database."""


AdditionalConfigT = TypeVar("AdditionalConfigT", bound=Optional[BaseAdditionalConfig])


class RedisAdditionalConfig(BaseAdditionalConfig):
    ttl: Union[float, int] = Field(
        Expiration.EXP_15MN.value, description="Time to live"
    )
    namespaces: RedisCacheNamespaces = Field(
        ..., description="Redis cache's namepsaces"
    )
