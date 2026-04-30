from fastapi import FastAPI, HTTPException, UploadFile, File
from sqlmodel import Session

from models.pokemon import (PokemonBase,
                    PokemonID,
                    PokemonUpdate)
from models.trainer import TrainerBase, TrainerID
from db import SessionDep, create_all_tables
from operations.operations_pokemon_db import (createPokemon_db,
                                              show_all_pokemon_db,
                                              find_one_pokemon_db,
                                              update_one_pokemon_db,
                                              kill_one_pokemon_db)
from operations.operations_trainer_db import createTrainer, findTrainer
from utils import save_img_local, save_img_remote

app = FastAPI(lifespan=create_all_tables)


@app.post("/image/local")
async def image_save_local(img: UploadFile = File(...)):
    path = save_img_local(img)
    return {"path for your image": path}


@app.post("/pokemon", response_model=PokemonID)
async def create_pokemon(pokemon: PokemonBase, session: SessionDep):
    trainer = findTrainer(pokemon.trainer_id, session)
    if trainer:
        return createPokemon_db(pokemon, session)
    else:
        raise HTTPException(status_code=404, detail="trainer not found")


@app.get("/pokemon", response_model=list[PokemonID])
async def show_pokemons(session: SessionDep):
    return show_all_pokemon_db(session)


@app.get("/pokemon/{id}", response_model=PokemonID)
async def show_one_pokemon(id: int, session: SessionDep):
    pokemon = find_one_pokemon_db(id, session)
    if not (pokemon):
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")
    return pokemon


@app.patch("/pokemon/{id}", response_model=PokemonID, response_model_exclude={"name", "type"})
async def update_pokemon(id: int, pokemon: PokemonUpdate, session: SessionDep):
    update = update_one_pokemon_db(id, pokemon, session)
    if not (update):
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")
    return update


@app.delete("/pokemon/{id}", response_model=PokemonBase)
async def delete_one_pokemon(id: int, session: SessionDep):
    deleted = kill_one_pokemon_db(id, session)
    if not (deleted):
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")
    return deleted


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/image/remote")
async def image_save_remote(file:UploadFile = File(...)):
    url_img = save_img_remote(file)
    return {"url for your image":url_img}


@app.post("/trainer", response_model=TrainerID)
def creater_trainer(trainer:TrainerBase, session: SessionDep):
    return createTrainer(trainer, session)
