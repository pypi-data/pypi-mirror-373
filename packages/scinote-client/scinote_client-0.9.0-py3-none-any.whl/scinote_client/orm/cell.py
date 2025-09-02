"""ORM client for a specific cell in an inventory in SciNote."""

from abc import ABC, abstractmethod
import logging
from typing import List

from ..client.api.inventory_cell_client import InventoryCellClient
from ..client.models.inventory_cell import (
    Attributes,
    CreateInventoryCell,
    UpdateInventoryCell,
)
from ..client.models.inventory_column_list_item import InventoryColumnListItem

logger = logging.getLogger(__name__)


class Cell(ABC):
    """Base class for a cell in an inventory in SciNote."""

    def __init__(
        self, cell_id: int, attributes: Attributes, client: InventoryCellClient
    ):
        self.cell_id = cell_id
        self.attributes = attributes
        self.__client = client

    def value(self):
        """Get the value of the cell."""
        logger.debug('Getting value for cell %s', self.attributes)

        # Empty cells will not have a value.
        if self.attributes.value is None:
            return None

        return self._do_value()

    @abstractmethod
    def _do_value(self):
        """Get the value of the cell."""
        pass

    async def update_value(self, value: str):
        """Update the value stored in cell."""
        logger.debug(f'Updating value for cell {self.attributes}')
        # We need to check if we are creating a new value or updating an
        # existing one.

        # For some cells like list, we need to convert to the list id from
        # the string that is being used.
        value = self._get_value_for_create_or_update(value)

        if self.attributes.value is None:
            await self.__do_create_cell(value)
        else:
            await self.__do_update_cell(value)

    async def __do_create_cell(self, value: str):
        try:
            result = await self.__client.create_cell(
                CreateInventoryCell(
                    value=value, column_id=self.attributes.column_id
                )
            )
            if result:
                self.cell_id = result.id
                self.attributes = result.attributes
        except Exception as e:
            logger.error(f'Failed to create cell value={value}: {e}')
            raise

    async def __do_update_cell(self, value: str):
        try:
            result = await self.__client.update_cell(
                UpdateInventoryCell(
                    id=self.cell_id,
                    value=value,
                    column_id=self.attributes.column_id,
                )
            )
            if result:
                self.attributes = result.attributes
        except Exception as e:
            logger.error(f'Failed to update cell {self.cell_id}: {e}')
            raise

    @abstractmethod
    def _get_value_for_create_or_update(self, value) -> str:
        """Get the value for create or update."""
        pass

    def match(self, value: str) -> bool:
        """Check if the value of the cell matches the supplied string."""

        if self.attributes.value is None:
            return False

        return self._do_match(value)

    @abstractmethod
    def _do_match(self, value: str) -> bool:
        """Check if the value of the cell matches the supplied string."""
        pass


class ListCell(Cell):
    """ORM client for a list cell in an inventory in SciNote."""

    def __init__(
        self,
        cell_id: int,
        attributes: Attributes,
        client: InventoryCellClient,
        list_column_items: List[InventoryColumnListItem],
    ):
        super().__init__(cell_id, attributes, client)
        self.list_column_items = list_column_items

    def _do_value(self):
        """Get the value of the cell."""
        return self.attributes.value.inventory_list_item_name

    def _do_match(self, value: str) -> bool:
        """Check if the value of the cell matches the supplied string."""
        return value == self.attributes.value.inventory_list_item_name

    def _get_value_for_create_or_update(self, value) -> str:
        """Get the value for create or update."""
        # We need to map the list item data to the list item id
        list_item_id = next(
            (
                item.id
                for item in self.list_column_items
                if item.attributes.data == value
            ),
            None,
        )
        if list_item_id is None:
            raise ValueError(
                f'List item {value} does not exist in column '
                f'{self.attributes.column_id}.'
            )
        return list_item_id


class TextCell(Cell):
    """ORM client for a text cell in an inventory in SciNote."""

    def __init__(
        self, cell_id: int, attributes: Attributes, client: InventoryCellClient
    ):
        super().__init__(cell_id, attributes, client)

    def _do_value(self):
        """Get the value of the cell."""
        return self.attributes.value.text

    def _do_match(self, value: str) -> bool:
        """Check if the value of the cell matches the supplied string."""
        return value == self.attributes.value.text

    def _get_value_for_create_or_update(self, value) -> str:
        """Get the value for create or update."""
        return value


class NumberCell(Cell):
    """ORM client for a number cell in an inventory in SciNote."""

    def __init__(
        self, cell_id: int, attributes: Attributes, client: InventoryCellClient
    ):
        super().__init__(cell_id, attributes, client)

    def _do_value(self):
        """Get the value of the cell."""
        return self.attributes.value.data

    def _do_match(self, value: str) -> bool:
        """Check if the value of the cell matches the supplied string."""
        return value == self.attributes.value.data

    def _get_value_for_create_or_update(self, value) -> str:
        """Get the value for create or update."""
        return value


class DateCell(Cell):
    """ORM client for a date cell in an inventory in SciNote."""

    def __init__(
        self, cell_id: int, attributes: Attributes, client: InventoryCellClient
    ):
        super().__init__(cell_id, attributes, client)

    def _do_value(self):
        """Get the value of the cell."""
        return self.attributes.value.date

    def _do_match(self, value: str) -> bool:
        """Check if the value of the cell matches the supplied string."""
        return value == self.attributes.value.date

    def _get_value_for_create_or_update(self, value) -> str:
        """Get the value for create or update."""
        return value


class DateTimeCell(Cell):
    """ORM client for a specific cell in an inventory in SciNote."""

    def __init__(
        self, cell_id: int, attributes: Attributes, client: InventoryCellClient
    ):
        super().__init__(cell_id, attributes, client)

    def _do_value(self):
        """Get the value of the cell."""
        return self.attributes.value.date_time

    def _do_match(self, value: str) -> bool:
        """Check if the value of the cell matches the supplied string."""
        return value == self.attributes.value.date_time

    def _get_value_for_create_or_update(self, value) -> str:
        """Get the value for create or update."""
        return value


class CellFactory:
    """Factory class for creating cells in an inventory in SciNote."""

    @staticmethod
    def create_cell(
        cell_id: int,
        attributes: Attributes,
        client: InventoryCellClient,
        **kwargs,
    ) -> Cell:
        """Create a new cell in the inventory."""
        match attributes.value_type:
            case 'list':
                if 'column_list_items' not in kwargs:
                    raise ValueError(
                        'Missing column_list_items for list column type.'
                    )
                return ListCell(
                    cell_id, attributes, client, kwargs['column_list_items']
                )
            case 'text':
                return TextCell(cell_id, attributes, client)
            case 'number':
                return NumberCell(cell_id, attributes, client)
            case 'date_time':
                return DateTimeCell(cell_id, attributes, client)
            case 'date':
                return DateCell(cell_id, attributes, client)
            case _:
                raise ValueError(
                    f'Unsupported value type {attributes.value_type}'
                )
