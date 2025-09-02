"""SciNote rest api client for inventory columns."""

import logging
from typing import List

import httpx
from pydantic import ValidationError

from ..models.inventory_columns import InventoryColumn
from .inventory_column_list_item_client import InventoryColumnListItemClient

logger = logging.getLogger(__name__)


class InventoryColumnClient:
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

    def list_item_client(self, column_id: int) -> InventoryColumnListItemClient:
        """Return a client for interacting with the list items of a column."""
        return InventoryColumnListItemClient(
            self.base_url,
            self.api_key,
            self.team_id,
            self.inventory_id,
            column_id,
        )

    # Inventory column related methods
    async def get_columns(self) -> List[InventoryColumn]:
        """Get all inventory columns from SciNote."""

        # Need to loop through all pages to get all of the columns
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/columns'
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
                        result.append(InventoryColumn(**column))
                        for column in response.json()['data']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                url = response.json()['links'].get('next', None)

                # Check we haven't visited this url before
                if url in visited:
                    break

            return result

    async def create_column(
        self, name: str, data_type: str, decimals: int = None
    ) -> str:
        """Create a new inventory column in SciNote."""
        if decimals is not None and data_type not in ['number', 'stock']:
            raise ValueError(
                'Decimals can only be set for columns with data type number'
                ' or stock'
            )

        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/columns'
        )
        json_body = {
            'data': {
                'type': 'inventory_columns',
                'attributes': {
                    'name': name,
                    'data_type': data_type,
                },
            },
        }

        if decimals is not None:
            json_body['data']['attributes']['metadata'] = {'decimals': decimals}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=json_body,
            )
            response.raise_for_status()
            return response.json()['data']['id']
