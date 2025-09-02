"""Maps all of the inventories for a SciNote team."""

import logging

from aiocache import cached

from ..client.api.inventory_client import InventoryClient
from .inventory import Inventory

logger = logging.getLogger(__name__)

# How long we cache result from SciNote before refreshing.
CACHE_TIMEOUT_SECONDS = 120


class Inventories:
    """Maps all of the inventories for a SciNote team."""

    def __init__(self, client: InventoryClient):
        self.__client = client

    async def inventory(self, name: str) -> Inventory:
        """Get the inventory by name."""

        inventories = await self.__load_inventories()

        logger.debug(f'Checking for inventory {name}')
        if inventories.get(name) is None:
            raise ValueError(f'Inventory {name} not found')

        return inventories.get(name)

    async def inventories(self) -> list[Inventory]:
        """Get all of the inventories."""
        inventories = await self.__load_inventories()
        return [value for value in inventories.values()]

    @cached(ttl=CACHE_TIMEOUT_SECONDS)
    async def __load_inventories(self):
        logger.debug('Loading all inventories')

        result = {}
        scinote_inventories = await self.__client.get_inventories()
        for inventory in scinote_inventories:
            inventory_name = inventory.attributes.name.lower().replace(' ', '_')
            logger.debug(f'Adding inventory {inventory_name}')
            result[inventory_name] = Inventory(
                inventory_name,
                self.__client.column_client(inventory.id),
                self.__client.item_client(inventory.id),
            )

        return result
