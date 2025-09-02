"""Model representing a team in SciNote."""

from pydantic import BaseModel, ConfigDict


class InventoryParent(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str
    relationships: dict
