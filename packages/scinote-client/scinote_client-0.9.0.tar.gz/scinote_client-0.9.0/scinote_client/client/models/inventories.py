"""Model representing a team in SciNote."""

from pydantic import BaseModel, ConfigDict


class Attributes(BaseModel):
    name: str


class Inventory(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str
    attributes: Attributes
