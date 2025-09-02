"""SciNote rest api client for inventories."""

import logging
from typing import List

import httpx
from pydantic import ValidationError

from ..models.inventories import Inventory
from .inventory_column_client import InventoryColumnClient
from .inventory_item_client import InventoryItemClient

logger = logging.getLogger(__name__)


class InventoryClient:
    """Client for interacting with the SciNote REST API."""

    def __init__(self, base_url: str, api_key: str, team_id: int):
        """Initialize the client."""
        self.base_url = base_url
        self.api_key = api_key
        self.team_id = team_id
        self.headers = {
            'Api-Key': api_key,
        }

    def column_client(self, inventory_id: int) -> InventoryColumnClient:
        return InventoryColumnClient(
            self.base_url, self.api_key, self.team_id, inventory_id
        )

    def item_client(self, inventory_id: int) -> InventoryItemClient:
        return InventoryItemClient(
            self.base_url, self.api_key, self.team_id, inventory_id
        )

    # Inventory related methods
    async def get_inventories(self) -> List[Inventory]:
        """Get all inventories from SciNote."""
        logger.debug('Getting all inventories')
        # Need to loop through all pages to get all of the inventories
        url = f'{self.base_url}/api/v1/teams/{self.team_id}/inventories'
        result = []

        # Keep track of visited urls to avoid infinite loops
        visited = set(url)
        async with httpx.AsyncClient() as client:
            while url:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                visited.add(url)
                try:
                    [
                        result.append(Inventory(**inventory))
                        for inventory in response.json()['data']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                url = response.json()['links'].get('next', None)

                # Check we haven't visited this url before
                if url in visited:
                    break

        logger.debug(f'Inventories retrieved: {result}')
        return result

    async def create_inventory(self, name: str) -> Inventory:
        """Create a new inventory in SciNote."""
        logger.debug('Creating inventory %s', name)
        url = f'{self.base_url}/api/v1/teams/{self.team_id}/inventories'
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={
                    'data': {
                        'type': 'inventories',
                        'attributes': {'name': name},
                    }
                },
            )
            response.raise_for_status()
            try:
                return Inventory(**(response.json()['data']))
            except ValueError as e:
                logger.error(f'Invalid response: {e}')
                raise
