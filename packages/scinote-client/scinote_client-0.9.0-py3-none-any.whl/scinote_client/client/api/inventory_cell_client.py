"""SciNote rest api client for inventory cells."""

from typing import List

import httpx
from pydantic import ValidationError

from ..models.inventory_cell import (
    CreateInventoryCell,
    InventoryCell,
    UpdateInventoryCell,
)


class InventoryCellClient:
    """Client for interacting with the SciNote REST API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        team_id: int,
        inventory_id: int,
        item_id: int,
    ):
        """Initialize the client."""
        self.base_url = base_url
        self.api_key = api_key
        self.team_id = team_id
        self.inventory_id = inventory_id
        self.item_id = item_id
        self.headers = {
            'Api-Key': api_key,
        }

    async def get_cells(self) -> List[InventoryCell]:
        """Get all inventory cells from SciNote."""

        # Need to loop through all pages to get all of the columns
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items/{self.item_id}/cells'
        )
        result = []

        # Keep track of visited urls to avoid infinite loops
        visited = set()
        async with httpx.AsyncClient() as client:
            while url:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                visited.add(url)
                try:
                    [
                        result.append(InventoryCell(**column))
                        for column in response.json()['data']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                url = response.json()['links'].get('next', None)

                # Check we haven't visited this url before
                if url in visited:
                    break

            return result

    async def create_cell(self, cell: CreateInventoryCell) -> InventoryCell:
        """Create a new inventory cell in SciNote."""
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items/{self.item_id}/cells'
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={
                    'data': {
                        'type': cell.type,
                        'attributes': {
                            'value': cell.value,
                            'column_id': cell.column_id,
                        },
                    },
                },
            )
            response.raise_for_status()
            return InventoryCell(**response.json()['data'])

    async def update_cell(self, cell: UpdateInventoryCell) -> InventoryCell:
        """Update an inventory cell in SciNote."""
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items/{self.item_id}/cells/{cell.id}'
        )
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url,
                headers=self.headers,
                json={
                    'data': {
                        'id': cell.id,
                        'type': cell.type,
                        'attributes': {
                            'value': cell.value,
                            'column_id': cell.column_id,
                        },
                    },
                },
            )
            response.raise_for_status()
            # If there was no update then the server will return a 204 with no
            # body, so we will return None in that case.
            if response.status_code == 204:
                return None
            else:
                return InventoryCell(**response.json()['data'])
