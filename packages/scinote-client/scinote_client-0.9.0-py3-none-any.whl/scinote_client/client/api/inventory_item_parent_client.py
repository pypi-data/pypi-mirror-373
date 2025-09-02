"""SciNote rest api client for inventory columns."""

from typing import List

import httpx
from pydantic import ValidationError

from ..models.inventory_parent import InventoryParent


class InventoryParentClient:
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

    async def get_parents(self) -> List[InventoryParent]:
        """Get all inventory parents for the given item from SciNote."""

        # Need to loop through all pages to get all of the columns
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items/{self.item_id}/parent_relationships'
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
                        result.append(InventoryParent(**parent))
                        for parent in response.json()['data']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                url = response.json()['links'].get('next', None)

                # Check we haven't visited this url before
                if url in visited:
                    break

            return result

    async def create_parent(self, parent_id: str) -> str:
        """Create a new parent for the given item in SciNote."""
        url = (
            f'{self.base_url}/api/v1/teams/{self.team_id}/inventories/'
            f'{self.inventory_id}/items/{self.item_id}/parent_relationships'
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={
                    'data': {
                        'type': 'inventory_item_relationships',
                        'attributes': {
                            'parent_id': parent_id,
                        },
                    }
                },
            )
            response.raise_for_status()
            return response.json()['data']['id']
