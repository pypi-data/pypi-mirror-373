"""SciNote rest api client."""

import os
from typing import List

import httpx
from pydantic import ValidationError

from ..models.teams import Team
from .inventory_client import InventoryClient


def CreateClient() -> 'TeamsClient':
    url = os.getenv('SCINOTE_BASE_URL')
    api_key = os.getenv('SCINOTE_API_KEY')

    assert url, 'SCINOTE_BASE_URL environment variable is required.'
    assert api_key, 'SCINOTE_API_KEY environment variable is required.'

    return TeamsClient(url, api_key)


class TeamsClient:
    """Client for interacting with the SciNote REST API."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the client with the base URL and API key."""
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Api-Key': api_key,
        }

    def inventory_client(self, team_id: int) -> InventoryClient:
        return InventoryClient(self.base_url, self.api_key, team_id)

    # Teams related methods
    async def get_teams(self) -> List[Team]:
        """Get all teams from SciNote."""
        # Need to loop through all pages to get all of the teams
        url = f'{self.base_url}/api/v1/teams'
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
                        result.append(Team(**team))
                        for team in response.json()['data']
                    ]
                except ValidationError as e:
                    raise ValueError(f'Invalid response from SciNote: {e}')

                url = response.json()['links'].get('next', None)

                # Check we haven't visited this url before
                if url in visited:
                    break

        return result
