from typing import List
from fastapi import FastAPI, HTTPException
from operations import createPokemon, showPokemons, showPokemon
from models import (PokemonBase, PokemonID)

app = FastAPI()

@app.post("/pokemon", response_model=PokemonID)
async def create_pokemon(pokemon:PokemonBase):
    return createPokemon(pokemon)


@app.get("/pokemon", response_model=list[PokemonID])
async def show_pokemons():
    return showPokemons()

@app.get("/pokemon/{id}", response_model=PokemonID)
async def show_one_pokemon(id:int):
    pokemon = showPokemon(id)
    if not(pokemon):
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")
    return pokemon

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
