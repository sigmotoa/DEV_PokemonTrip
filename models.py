# from pydantic import BaseModel, Field
from email.policy import default

from pokemon_types import PokemonType
from typing import Optional
from sqlmodel import SQLModel, Field


class PokemonBase(SQLModel):
    name: str | None = Field(default=None,
                             min_length=3,
                             max_length=64)
    type: PokemonType | None = Field(default=None,
                                     )
    level: int | None = Field(default=None,
                              gt=0,
                              le=100)


class PokemonID(PokemonBase, table=True):
    id: int | None = Field(default=None, primary_key=True, gt=0)

class PokemonUpdate(PokemonBase):
    type: PokemonType = Field(None, exclude=True)
    name: str | None = Field(None,exclude=True)
    level : int | None = Field(default=None,gt=1,
                              le=100)
