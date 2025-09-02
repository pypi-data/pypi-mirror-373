"""Model representing a team in SciNote."""

from pydantic import BaseModel, ConfigDict


class Attributes(BaseModel):
    name: str
    description: str
    space_taken: int


class Team(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    type: str
    attributes: Attributes
