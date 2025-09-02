"""SciNote REST API client for inventory items."""

import logging
from typing import List

import httpx
from pydantic import ValidationError

from ..models.inventory_cell import CreateInventoryCell, InventoryCell
from ..models.inventory_item import InventoryItem, UpdateItem
from .inventory_cell_client import InventoryCellClient
from .inventory_item_child_client import InventoryChildClient
from .inventory_item_parent_client import InventoryParentClient

logger = logging.getLogger(__name__)


class InventoryItemClient:
    """Client for interacting with the SciNote REST API."""

    def __init__(
        self, base_url: str, api_key: str, team_id: int, inventory_id: int
    ):
        """Initialize the client."""
        self.base_url = base_url
        self.api_key = api_key
        self.team_id = team_id
        self.inventory_id = inventory_id
        self.headers = {
            'Api-Key': api_key,
        }
        self.params = {
            'include': 'inventory_cells',
        }

    def cell_client(self, item: int) -> InventoryCellClient:
        return InventoryCellClient(
            self.base_url, self.api_key, self.team_id, self.inventory_id, item
        )

    def parent_client(self, item: int) -> InventoryParentClient:
        return InventoryParentClient(
            self.base_url, self.api_key, self.team_id, self.inventory_id, item
        )

    def child_client(self, item: int) -> InventoryChildClient:
        return InventoryChildClient(
            self.base_url, self.api_key, self.team_id, self.inventory_id, item
        )

    async def get_items(self) -> List[InventoryItem]:
        """Get all inventory items from SciNote."""

        # Need to loop through all pages to get all of the items
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items'
        )
        result = []
        inventory_cells = {}

        # Keep track of visited urls to avoid infinite loops
        visited = set()
        async with httpx.AsyncClient() as client:
            while url:
                response = await client.get(
                    url, headers=self.headers, params=self.params
                )
                response.raise_for_status()
                visited.add(url)
                try:
                    [
                        result.append(InventoryItem(**item))
                        for item in response.json()['data']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                # Read of all the cell responses as well so we can marry them
                # together later.
                try:
                    [
                        inventory_cells.update(
                            {cell['id']: InventoryCell(**cell)}
                        )
                        for cell in response.json()['included']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                url = response.json()['links'].get('next', None)

                # Check we haven't visited this url before
                if url in visited:
                    break

            # If we have inventory cells, we need to attach them to the items.
            for item in result:
                item.inventory_cells = [
                    inventory_cells[cell['id']]
                    for cell in item.relationships.inventory_cells['data']
                ]

            return result

    async def create_item(
        self, name: str, cells: List[CreateInventoryCell] = None
    ) -> InventoryItem:
        """Create a new inventory item in SciNote."""
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items'
        )

        included = []
        if cells:
            for cell in cells:
                included.append(
                    {
                        'type': cell.type,
                        'attributes': {
                            'value': cell.value,
                            'column_id': cell.column_id,
                        },
                    }
                )

        json_body = {
            'data': {
                'type': 'inventory_items',
                'attributes': {
                    'name': name,
                },
            },
            'included': included,
        }

        async with httpx.AsyncClient() as client:
            request = client.build_request(
                'POST',
                url,
                headers=self.headers,
                json=json_body,
            )

            logger.debug(
                'Creating item with request: %s', request.content.decode()
            )

            response = await client.send(request)
            response.raise_for_status()
            item = InventoryItem(**response.json()['data'])

            if 'included' in response.json():
                for cell in response.json()['included']:
                    item.inventory_cells.append(InventoryCell(**cell))

            return item

    async def update_item(self, update: UpdateItem) -> InventoryItem:
        """Update an existing inventory item in SciNote."""
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items/{update.id}'
        )

        included = []
        if update.included:
            for cell in update.included:
                included.append(
                    {
                        'id': cell.id,
                        'type': cell.type,
                        'attributes': {
                            'value': cell.attributes.value,
                            'column_id': cell.attributes.column_id,
                        },
                    }
                )

        json_body = {
            'data': {
                'id': update.id,
                'type': update.type,
                'attributes': {
                    'name': update.attributes.name,
                },
            },
            'included': included,
        }

        async with httpx.AsyncClient() as client:
            logger.debug('url: %s', url)
            request = client.build_request(
                'PATCH',
                url,
                headers=self.headers,
                json=json_body,
            )

            logger.debug(
                'Updating item with request: %s', request.content.decode()
            )

            response = await client.send(request)
            response.raise_for_status()
            item = InventoryItem(**response.json()['data'])

            if 'included' in response.json():
                for cell in response.json()['included']:
                    item.inventory_cells.append(InventoryCell(**cell))

            return item
