"""SciNote REST API client for inventory column list items."""

import logging
from typing import List

import httpx
from pydantic import ValidationError

from ..models.inventory_column_list_item import (
    CreateInventoryColumnListItem,
    InventoryColumnListItem,
)

logger = logging.getLogger(__name__)


class InventoryColumnListItemClient:
    """SciNote REST API client for inventory column list items."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        team_id: str,
        inventory_id: str,
        column_id: str,
    ):
        """Initialize the client with the base URL and token."""
        self.base_url = base_url
        self.api_key = api_key
        self.team_id = team_id
        self.inventory_id = inventory_id
        self.column_id = column_id
        self.headers = {
            'Api-Key': api_key,
        }

    async def get_list_items(self) -> List[InventoryColumnListItem]:
        """Get a list of inventory column list items."""
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/columns/{self.column_id}/list_items'
        )

        result = []

        # Keep track of visited urls to avoid infinite loops
        visited = set()
        async with httpx.AsyncClient() as client:
            while url:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                visited.add(url)
                logger.debug(f'Get columns response: {response.json()}')
                try:
                    [
                        result.append(InventoryColumnListItem(**column))
                        for column in response.json()['data']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                url = response.json()['links'].get('next', None)

                # Check we haven't visited this url before
                if url in visited:
                    break

            return result

    async def create_list_item(
        self, item: CreateInventoryColumnListItem
    ) -> InventoryColumnListItem:
        """Create a new list item."""
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/columns/{self.column_id}/list_items'
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    'data': {
                        'type': item.type,
                        'attributes': {
                            'data': item.data,
                        },
                    },
                },
                headers=self.headers,
            )
            response.raise_for_status()
            try:
                return InventoryColumnListItem(**response.json()['data'])
            except ValidationError as e:
                logger.error(f'Invalid response from SciNote: {e}')
                raise
