from typing import List
from fastapi import FastAPI, HTTPException
from sqlmodel.orm import session

from operations_csv import createPokemon, showPokemons, showPokemon, deletePokemon
from models import (PokemonBase, PokemonID)
from db import SessionDep, create_all_tables
from operations_db import createPokemon_db, show_all_pokemon_db

app = FastAPI(lifespan=create_all_tables)

@app.post("/pokemon", response_model=PokemonID)
async def create_pokemon(pokemon:PokemonBase, session:SessionDep):
    return createPokemon_db(pokemon, session)


@app.get("/pokemon", response_model=list[PokemonID])
async def show_pokemons(session:SessionDep):
    return show_all_pokemon_db(session)

@app.get("/pokemon/{id}", response_model=PokemonID)
async def show_one_pokemon(id:int):
    pokemon = showPokemon(id)
    if not(pokemon):
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")
    return pokemon

@app.delete("/pokemon/{id}", response_model=PokemonBase)
async def delete_one_pokemon(id:int):
    deleted = deletePokemon(id)
    if not(deleted):
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")
    return deleted

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
