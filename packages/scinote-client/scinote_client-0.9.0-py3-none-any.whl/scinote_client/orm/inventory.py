"""ORM client for an specific inventory in SciNote."""

import logging

from aiocache import Cache

from ..client.api.inventory_column_client import InventoryColumnClient
from ..client.api.inventory_item_client import InventoryItemClient
from ..client.models.inventory_cell import CreateInventoryCell
from ..client.models.inventory_columns import InventoryColumn
from .items import Item

logger = logging.getLogger(__name__)

# How long we cache result from SciNote before refreshing.
CACHE_TIMEOUT_SECONDS = 120


class Inventory:
    """ORM client for a specific inventory in SciNote."""

    def __init__(
        self,
        name: str,
        column_client: InventoryColumnClient,
        item_client: InventoryItemClient,
    ):
        self.column_client = column_client
        self.item_client = item_client
        self.name = name
        self.__columns = {}
        self.__columns_list_items = {}
        self.__item_list = []
        self.__cache = Cache(Cache.MEMORY, ttl=CACHE_TIMEOUT_SECONDS)

    async def load_columns(self) -> None:
        """Load the columns for this inventory."""

        if not await self.__cache.exists('columns'):
            columns = await self.column_client.get_columns()
            self.__columns = {}
            self.__columns_list_items = {}
            for column in columns:
                name = column.attributes.name.lower().replace(' ', '_')
                self.__columns[name] = column
                # If column is a list, we need to get the list items.
                # We do this to avoid having to repeatedly call the API for
                # individual cells of the column.
                if column.attributes.data_type == 'list':
                    list_items = await self.column_client.list_item_client(
                        column.id
                    ).get_list_items()
                    self.__columns_list_items[column.id] = list_items

            await self.__cache.set('columns', True)

    async def load_items(self) -> None:
        """Load the items for this inventory."""

        if not await self.__cache.exists('items'):
            items = await self.item_client.get_items()
            self.__item_list = []
            for item in items:
                self.__item_list.append(
                    Item(
                        item.id,
                        item.attributes.name,
                        item.attributes.created_at,
                        self.item_client,
                        self.__columns,
                        self.__columns_list_items,
                        item.inventory_cells,
                    )
                )
            await self.__cache.set('items', True)

    async def items(self) -> list[Item]:
        """Get the items for this inventory."""
        await self.load_columns()
        await self.load_items()
        return self.__item_list

    async def match(self, **kwargs) -> list[Item]:
        """Return matching items from this inventory."""
        await self.load_columns()
        await self.load_items()
        return [item for item in self.__item_list if item.match(**kwargs)]

    async def columns(self):
        """Get the columns for this inventory."""
        await self.load_columns()
        return [column for column in self.__columns.values()]

    async def has_column(self, name: str) -> bool:
        """Check if the inventory has a column."""
        await self.load_columns()
        return name in self.__columns

    async def create_item(self, name: str, **kwargs) -> Item:
        """Create a new item in this inventory."""
        await self.load_columns()

        logger.debug('creating item with name %s', name)

        cells = []
        for key, value in kwargs.items():
            if key not in self.__columns:
                raise ValueError(f'Column {key} does not exist in inventory.')

            column = self.__columns[key]
            cells.append(self.__create_inventory_cell(column, value))

        item = await self.item_client.create_item(name, cells)

        new_item = Item(
            item.id,
            item.attributes.name,
            item.attributes.created_at,
            self.item_client,
            self.__columns,
            self.__columns_list_items,
            item.inventory_cells,
        )
        self.__item_list.append(new_item)
        return new_item

    def __create_inventory_cell(
        self, column: InventoryColumn, value: str
    ) -> CreateInventoryCell:
        """Create an inventory cell for a column.

        Cells like text, number etc are created with the value.
        Cells like list_item etc are created with the id of the value.
        """
        match column.attributes.data_type:
            case 'text' | 'number' | 'date_time' | 'date':
                return CreateInventoryCell(
                    value=value,
                    column_id=column.id,
                )
            case 'list':
                if column.id not in self.__columns_list_items:
                    raise ValueError(
                        f'Column {column.attributes.name} list items not '
                        f'loaded.'
                    )
                list_items = self.__columns_list_items[column.id]
                list_item = next(
                    (
                        item
                        for item in list_items
                        if item.attributes.data == value
                    ),
                    None,
                )
                if list_item is None:
                    raise ValueError(
                        f'List item {value} does not exist in column '
                        f'{column.attributes.name}.'
                    )
                return CreateInventoryCell(
                    value=list_item.id,
                    column_id=column.id,
                )
            case _:
                raise ValueError(
                    f'Unknown data type {column.attributes.data_type}'
                )
