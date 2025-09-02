"""Model representing an inventory cell in SciNote."""

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class TextItem(BaseModel):
    text: str


class ListItem(BaseModel):
    inventory_list_item_id: int
    inventory_list_item_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CheckListItem(BaseModel):
    inventory_checklist_item_ids: List[int]
    inventory_checklist_item_names: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class StatusItem(BaseModel):
    inventory_status_item_id: int
    inventory_status_item_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FileItem(BaseModel):
    file_id: int
    file_name: str
    file_size: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DateTimeItem(BaseModel):
    date_time: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DateItem(BaseModel):
    date: date
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class NumberItem(BaseModel):
    data: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Attributes(BaseModel):
    value_type: str
    value: (
        TextItem
        | ListItem
        | ListItem
        | CheckListItem
        | StatusItem
        | FileItem
        | DateTimeItem
        | DateItem
        | NumberItem
    ) = None
    column_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class InventoryCell(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str = 'inventory_cells'
    attributes: Attributes


class CreateInventoryCell(BaseModel):
    """Model represents a new inventory cell in SciNote."""

    type: str = 'inventory_cells'
    value: str | int
    column_id: int


class UpdateInventoryCell(BaseModel):
    """Model represents updating an inventory cell in SciNote."""

    id: str
    type: str = 'inventory_cells'
    value: str | int
    column_id: int
