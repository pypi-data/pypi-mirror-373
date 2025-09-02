"""Model representing an inventory column list item in SciNote."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Attributes(BaseModel):
    data: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class InventoryColumnListItem(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str = 'inventory_list_items'
    attributes: Attributes


class CreateInventoryColumnListItem(BaseModel):
    """Model represents a new inventory column list item in SciNote."""

    type: str = 'inventory_list_items'
    data: str
