from fastapi import FastAPI
from operations import createPokemon
from models import (PokemonBase, PokemonID)

app = FastAPI()

@app.post("/pokemon", response_model=PokemonID)
async def create_pokemon(pokemon:PokemonBase):
    return createPokemon(pokemon)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
