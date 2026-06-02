from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form, Depends
from typing import Optional
from fastapi.params import Depends
from sqlmodel import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.pokemon import (PokemonBase,
                            PokemonID,
                            PokemonUpdate)
from models.pokemon_types import PokemonType
from models.trainer import TrainerBase, TrainerID
from db import SessionDep, create_all_tables, get_session
from operations.operations_pokemon_db import (createPokemon_db,
                                              show_all_pokemon_db,
                                              find_one_pokemon_db,
                                              update_one_pokemon_db,
                                              kill_one_pokemon_db,
                                              update_pokemon_image_db)
from operations.operations_trainer_db import createTrainer, findTrainer, update_trainer_image_db
from utils import save_img_local, save_img_remote

app = FastAPI(lifespan=create_all_tables)

templates = Jinja2Templates(directory="templates")


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
    return await show_all_pokemon_db(session)


@app.get("/pokemon/{id}", response_model=PokemonID)
async def show_one_pokemon(id: int, session: SessionDep):
    pokemon = await find_one_pokemon_db(id, session)
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


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/image/remote")
async def image_save_remote(file: UploadFile = File(...)):
    url_img = save_img_remote(file)
    return {"url for your image": url_img}


@app.post("/trainer", response_model=TrainerID)
def creater_trainer(trainer: TrainerBase, session: SessionDep):
    return createTrainer(trainer, session)

@app.post("/pokemon/{id}/image", response_model=PokemonID)
async def upload_pokemon_image(id: int, session: SessionDep, file: UploadFile = File(...)):
    pokemon = find_one_pokemon_db(id, session)
    if not pokemon:
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")
    url_img = save_img_remote(file)
    return update_pokemon_image_db(id, url_img, session)

@app.post("/trainer/{id}/image", response_model=TrainerID)
async def upload_trainer_image(id: int, session: SessionDep, file: UploadFile = File(...)):
    trainer = findTrainer(id, session)
    if not trainer:
        raise HTTPException(status_code=404, detail=f"{id} Trainer not found")
    url_img = save_img_remote(file)
    return update_trainer_image_db(id, url_img, session)


@app.get("/html", response_class=HTMLResponse)
async def myHtml():
    my_html = """<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mi primer HTML</title>
</head>
<body>
<h1>Hello</h1>

<h2>Etiqueta H2</h2>

<a href="http://sigmotoa.com" target="_top">Visita mi sitio</a>

<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAEXCAMAAADcLvXKAAABL1BMVEX////23DL1xxLhtQsAAADdwycAaDYAZDcnJyf7yhD///z2zjSSmiWMjIz1xgPg4OB4eHjOzs7fsABjhix7kSj30k722h0AYjcodDJiYmKNmSaJkiry8vLcwRnkuQ0AaTQuLi7+/O3guRTvwhH67aD5537mxB9WVlaCgoL29vb9+d/330r89cv12hT45W/w1Cz56Irs2obkvTD20SL157nmwULpymP9+u7IsB+ppCEYGBhqamqVlZWqqqrGxsb89c/88bv7767330X887734mD67Jznz1Tr1mr42mL645/t1YL42njpyV7rznL26cL579Lu1Y/x36i5qiDg0IK9v4FWfypEei1TiFsqcxkAZRQAXh3H0rKBonYAVSTf6NOFkQBwjSpplFugtopniBo/Pz/5TbYZAAAJX0lEQVR4nO2de1fTSBiH0wZQCxSJ0gUkBdrKJZSLgFuty6VcdhGR2+q6oq6u6/f/DJuZZNJkLskkTWbGc+b5YyHZ1PP05ZeZd9IEDEOj0Wg0Go1Go9FoNBqNRjMoFeegfdjrtVq9w/aBsyhbJ5nKQWvjqFQLUyqtPe0dq+vutE5q664lSa22vrbVrsgWJHFaRzWqcd+8tKGY+PEJvcgY60ctdaJyeMSj7Ff8qSNbF9I+Wed19r3l13txI5Wz592SLN2LPwVZ3msyY+KsZXEGrJ9Kk25nVIblPunIkW6lTnQUKSnZGlC6VDsQL72RNdJ91tuipZ8OLu1WW7B2LtKiQ3Kaj7SLwHnyeNATsc+aMOnF3CrtZmRLlPVJftLuQCIo2r0cS10SlZFKvtKlWk+EdX7jB0LAuqyTt3NJRLudc6oBR8UX+yh36VLtuGhpJ78JxmPTHrZ/L9o633NxcxhiF91qr+WobA/72DfFSi/m5zzcp+iIHOQTkLAypNhRpJWHNeFcdLC3BrcmnV3rq0KtNwZVtinOrvXrQq0HG0JoZfasnxVqXYizwtYxzoVbZz0ZGXlWu9bxzmpax4ZDhHWWPhUzXCo3TcHW6Ue+aKGXmmVXmrQu9nJ26lkmkuilskvdNBuE9WGh1mlndKzMsNA062L7kHTd0ybuDAotwbqdxnoTd/alTXIgLPbjDieFdSBt+85ImjgZhwteFaS4GhJII+emaTKs7T+KteYf+pD0UpmQJq0LXjcaZ7zWWKHD0oS1WfQnHa85g40VOiKNDyENs+iLT4fVFPloUqVx64a5XbC04XBZQ2m7TJfGrU3rvGhro1rmzMcSSxqzbpjWbuHWZ9WdRGk7kg5cOmrdcHcU/9n0eXKxQT7KbOmIte1uFx5rw7islpO0I+kgpSPW7qaAWBuLrnU0Izu+Htq7GZEuE9Lh8Rrkw7os3toYjWqHBWnS9TjrBtwUIG08qwaC/TqHtKPSZD7Mfs/nSb8VYX1Q7dcVkwY/g81mojQqtictYNwDeNblTVIavJfoNi0f/vloow0xtxK98bV3SOky9kYY0sA7+O5CiDQc+1hES83IRwRBATEqbGkMDmkxIwjAi0izmSTNU2oxIwjAgdZmLqW2iv2UIMxUFRQyl1IL6EEQu1UwPORS6qJXjCEq0AnPdT1DqQtfe4VxZ3XTrGOS2LvgKrWAdq9PB1hHtOu4NFepLbH3qr6pgmmv7ps265S88FgLmhcRTtVPQN0FfMWl+UotbtjzOKuGvcgJh6vUzwVLg34VaddpkyRXqUUsYqLAmaZZpyqrN8Mg2jGdH19ARHV7EUbjtBUtNbjix5bmCYiUUscWm8daSqlji80RawkDiMcOU5uj1MLHakRvAGtppTYqrGQ3FS41u9jJ1sI7kBCVzNaCm70or+naidaC+2qMTsZa/ypT2jBOqcVOGq4tyc/AdrJYW8Ku3LB4Q9NOspb+uLGT3lp+qcFSLHWtpZeavjqIt1ag1NSGtal2qgGUaT3WWuq0GEC5CB9nLbMDCXNOFDvOWmKzF2ExjbWk1SKFKVw7zlq2bACxgGRbi730GwvZ+Sl/LgKIZoRpLelyAhXic1PW5Ghdy1YNw22tUEDIiDBPR9miEYiIMKTVGUEAxJKGHhF1phgPvMtmRETSb5VhgV9ioFur0oMgrriCrcR6IAxPsFWLNdlB0SKi1mgNuOaIiDr9HmKXIyJ12ZIExNKAEhHJV/codJI/SFerdfJ4nhhsq9hHijNxkRhs9QY+d6WeGBH1Bj53EMFueyIjYinWhQB2iXvOiIgocaksyiVhjUekrmCtLy3iThHMuqGg9RVpXVff2rGI0xGLyLZav28X4ljkLaDqW19RrJs/gzV541bEWrX1F+CSZl1XvdauNXE6RiPy01iXVbfepVqHI6LieH1jmbS73xWf0a8t2k22kWIr2D2dm1Tr0PmoYqf6lm4dKraKq4ILE3/SAC+2iiuw5wzrfrEVXO1WtsHYRrMOiq3glYUOFKNZ94ut3lWcRYtpHRS7IVuS4IptHRRbvauTN9A6/iEDNe5nCXMdY42KLe8+YBZvzRhrvxsR+YAdH9ux1k1FBxEz1trPiGprsI4Vb+0XW7H+6SrB2tNWrX+6TLKGGVGtE7lOtIbjiGIfk14knI1+RtT6FKyynWwNtNVazni9E7J+wKCp2Ox4Y9UhD8pLtv0CcPvSZWwW4W7cgt1/yjYN827sybf3f01Pz8+PjNy79wvgHg7c90G2aZi/oeRIMh8VCrZzxyEMufsk27XPJ27r+c+yXft85pV2IyLbNaAy759t3mk47zLdx990/wsO+fKPbFuE8/UxGNluXwzb6Hc9hUZpfxN8WbLLVWVakdOwYALVKdm2CPaTsDRtRZa81MeT2NaKRKSVznpUtq8H8VhBgrYSf+LTYbV4LIT9La043t2+HIPMzj6OMAa3vz3C+abCZ2F3ZHsXzxcFehH+HiTgX9nOhvEhtfTInfQhu/MxvfX8d9nW37+kTDXos6Zln4//vXdHhfePHj8JmB2LAx7xVfKnYbtpB2u/zZJrnXJeDOZH4X9HNQzxOAGvtdR+lfZYN5+2xKur6XrUiPWZPGvqryvg1JbW+WUvtcxiZ061zGIPUmp5w8hZdTCkTJDO6FSE0SSmMCQOIyEqCcj202g0Go1Go9GkYaV7H2do3zCGvG+7E+CYySHimO4r+Gq0OSPY+uEQyZxr7eNbk+xF/8eEdOuHBoc1fPGrYPM36daTHNYwIKv97fvSrQ0Oa/DOjD18h0TrcQ7r7irYvxzasyLFGgsm1Xoheswc8RMSBrIej+7msfYDMuN92RckDBnA+oe3c8KXFyQMyW49gV7Y9b6ZE6VsDJLrcW/nJPon9kQpG33rHzOQ5f0Y6653zMxK+JBVY9/7ZlmCNWIuxhoRns1n+pONwIhg1uicirVeDb0QvINlasgEWqPxK84avrPV0AH+ELggzRrtjrOG78wPcxd8PxE+WIJ1MC/HWYdnc2/AXMBeLcx6ZQ6wGmu9AI+BJx0KiNc0jWM/KWHWKcfrcLuHZUekdcq58QfV+pXa1hOkMUTUkJ3N+jeGtahZPZs1Q1rYrJ7JGu1YWZ3z6YqNSCZr9KJJ4p8RNKunsUYL8WBtHgzvaKoUNavvjXtgQ+2Kvxv+xCf8LVRItL3HeoFGo9FoNBqNRqPRaDQajUajAP8DD3RB93ZdlwgAAAAASUVORK5CY" content="Imagen de la copa del mundo FIFA" alt="algo">

<a href="form.html">Clic para ver el formulario</a>

</body>
</html>"""
    return HTMLResponse(content=my_html, status_code=200)


@app.get("/htmltem", response_class=HTMLResponse)
async def templating(request: Request):
    return templates.TemplateResponse(
        request, "index.html"
    )


@app.get("/htmlpokemon/{id}", response_class=HTMLResponse)
async def htmlpokemon(request: Request, id: int, session: SessionDep):
    pokemon = find_one_pokemon_db(id, session)
    if not (pokemon):
        raise HTTPException(status_code=404, detail=f"{id} Pokemon not found")

    return templates.TemplateResponse(request, "pokemon.html",
                                      {"pokemon": pokemon})


@app.get("/htmlpokemon", response_class=HTMLResponse)
async def show_pokemons(request: Request, session: SessionDep):
    pokemons = show_all_pokemon_db(session)

    return templates.TemplateResponse(
        request, "pokemones.html", {"pokemones": pokemons})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse({"request": request}, "base.html")


@app.get("/pokemons", response_class=HTMLResponse)
async def show_all_pokemons_html(request: Request, session: Session = Depends(get_session)):
    pokemons = await show_all_pokemon_db(session)
    print(pokemons)
    return templates.TemplateResponse(request, "all_pokemon.html", {"pokemon_list": pokemons})


@app.get("/pokemons/{id}", response_class=HTMLResponse)
async def show_one_pokemon_html(request: Request, id: int, session: SessionDep):
    one_pokemon = await find_one_pokemon_db(id, session)
    return templates.TemplateResponse(request, "one_pokemon.html", {"poke": one_pokemon})


@app.get("/pokemons/create/", response_class=HTMLResponse)
async def catch_one_pokemon_html(request: Request):
    return templates.TemplateResponse(request, "catch.html")


@app.post("/pokemons/create/", response_class=HTMLResponse)
async def pokemon_catched(
        name: str = Form(),
        type: Optional[str] = Form(None),
        level: Optional[int] = Form(None),
        session: Session = Depends(get_session)):
    new_pokemon = PokemonBase(name=name, type=type, level=level)
    catched = await create_pokemon(new_pokemon, session)

    return RedirectResponse("/pokemons", status_code=302)
