"""Maps a SciNote item to an ORM item."""

from datetime import datetime
import logging
from typing import List

from ..client.api.inventory_item_client import InventoryItemClient
from ..client.models.inventory_cell import Attributes, InventoryCell
from ..client.models.inventory_column_list_item import InventoryColumnListItem
from ..client.models.inventory_item import UpdateItem
from .cell import Cell, CellFactory

logger = logging.getLogger(__name__)
"""
An item is a complete row in the inventory.

When SciNote returns an item, the values are mapped to a column ID. We need to
do this mapping here using the columns for the inventory and the values that
are passed into the constructor.
"""


class Item:
    """Maps a SciNote item to an ORM item."""

    def __init__(
        self,
        id: str,
        name: str,
        created_at: datetime,
        item_client: InventoryItemClient,
        columns: dict,
        column_list_items: dict[str, List[InventoryColumnListItem]],
        values: list[InventoryCell],
    ):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.item_client = item_client
        self.column_ids = {}
        self.column_names = {}
        self.column_list_items = column_list_items
        self.__cells = {}

        logger.debug('Columns: %s', columns)
        logger.debug('Values: %s', values)

        # Create a map of column ids to names and vice versa.
        for index, (key, value) in enumerate(columns.items()):
            name = key.lower().replace(' ', '_')
            self.column_ids[value.id] = name
            self.column_names[name] = value.id

        # Create cells for those cells that have values in SciNote.
        self.__create_cells_from_inventory_cells(values)

        # SciNote will only return values if they are not empty. We need to
        # create empty cells for the columns that are not present.
        empty_columns = set(self.column_names.keys()) - set(self.__cells.keys())
        logger.debug('Empty columns: %s', empty_columns)
        for column_name in empty_columns:
            # Get metadata for the missing column.
            column = columns[column_name]
            list_items = column_list_items.get(column.id, None)
            self.__cells[column_name] = CellFactory.create_cell(
                None,  # No id for cells that do not exist.
                Attributes(
                    column_id=column.id,
                    value_type=column.attributes.data_type,
                ),
                item_client.cell_client(self.id),
                column_list_items=list_items,
            )

    def cell(self, name) -> Cell:
        """Get the cell by name."""
        if self.column_names.get(name) is None:
            raise ValueError(f'Item {name} not found')
        return self.__cells.get(name)

    def cells(self) -> list[Cell]:
        """Get all of the cells."""
        return [value for value in self.__cells.values()]

    def match(self, **kwargs) -> bool:
        """Match the item against the given values."""
        for key, value in kwargs.items():
            if key == 'name':
                if self.name != value:
                    return False
                continue
            if key == 'id':
                if self.id != value:
                    return False
                continue

            if key not in self.column_names:
                logger.warning('Column %s not found in item', key)
                return False

            if not self.cell(key).match(value):
                return False

        return True

    async def update(self, **kwargs) -> 'Item':
        """Update the item and its cells with the given values.

        This allows for a bulk update of the item and its cells in one call to
        SciNote. The caller passes keyword arguments for the cells to update,
        where the key is the name of the column and the value is the value to
        update that cell to.

        The caller can also pass the key 'name', which represents the name of
        the item.

        The method returns the updated Item object.
        """
        # only update the item name if the call to SciNote succeeds.
        item_name = self.name
        included = []
        for key, value in kwargs.items():
            if key == 'name':
                item_name = value
                continue

            if key not in self.column_names:
                logger.error('Column %s not found in item', key)
                raise KeyError(
                    f"Column '{key}' not found in item. Update aborted."
                )

            cell = self.__cells.get(key)

            if cell is None:
                raise KeyError(
                    f"Cell '{key}' not found in item. Update aborted."
                )

            # For the update we need the column id and the value to update.
            included.append(
                {
                    'id': cell.cell_id,
                    'attributes': {
                        'value': cell._get_value_for_create_or_update(value),
                        'column_id': cell.attributes.column_id,
                    },
                }
            )

        update = UpdateItem(
            id=self.id,
            attributes={
                'name': item_name,
            },
            included=included,
        )

        result = await self.item_client.update_item(update)
        self.name = result.attributes.name
        # Update the cells for each column that was updated. We just overwrite
        # any existing cells.
        self.__create_cells_from_inventory_cells(result.inventory_cells)

        return self

    def __create_cells_from_inventory_cells(
        self, values: List[InventoryCell]
    ) -> None:
        """Create cells from a list of inventory cells."""

        # For each incoming value, map it to the column name. There is added
        # complexity as the name of the field that is the value of the cell
        # is dependent on the type of the column.
        for value in values:
            column_id = str(value.attributes.column_id)
            column_name = self.column_ids[column_id]
            list_items = self.column_list_items.get(column_id, None)

            self.__cells[column_name] = CellFactory.create_cell(
                value.id,
                value.attributes,
                self.item_client.cell_client(self.id),
                column_list_items=list_items,
            )
