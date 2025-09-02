"""Model representing an inventory item in SciNote."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .inventory_cell import InventoryCell


class Attributes(BaseModel):
    name: str
    archived: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Relationships(BaseModel):
    inventory_cells: dict


class InventoryItem(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str
    attributes: Attributes
    relationships: Relationships

    # This is not present in the schema from SciNote, we add it here so
    # we can retrieve the cells while we're retrieving the items.
    inventory_cells: list[InventoryCell] = []


class UpdateIncludedCellsAttributes(BaseModel):
    value: str | int
    column_id: int


class UpdateIncludedCells(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: str
    type: str = 'inventory_cells'
    attributes: UpdateIncludedCellsAttributes


class UpdateItem(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str = 'inventory_items'
    attributes: Attributes
    included: list[UpdateIncludedCells] = []
