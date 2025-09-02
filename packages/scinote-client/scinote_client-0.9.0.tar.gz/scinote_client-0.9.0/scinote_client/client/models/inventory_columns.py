"""Model representing a team in SciNote."""

from pydantic import BaseModel, ConfigDict


class Attributes(BaseModel):
    name: str
    data_type: str


class InventoryColumn(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str
    attributes: Attributes
