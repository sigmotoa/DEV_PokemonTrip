from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from models.pokemon import PokemonBase, PokemonID, PokemonUpdate


async def createPokemon_db(pokemon: PokemonBase, session: Session):
    new_pokemon = PokemonID.model_validate(pokemon)
    session.add(new_pokemon)
    session.commit()
    await session.refresh(new_pokemon)

    return new_pokemon


async def show_all_pokemon_db(session: Session):
    # return session.query(PokemonID).all()
    # session.exec(select(PokemonID).gr)
    return session.exec(select(PokemonID))
    # statement = select(PokemonID)
    # results = session.exec(statement)
    # return results


async def find_one_pokemon_db(id: int, session: Session):
    try:
        return session.get_one(PokemonID, id)
    except NoResultFound:
        return None


def update_one_pokemon_db(id: int, new_pokemon: PokemonUpdate, session: Session):
    pokemon = find_one_pokemon_db(id, session)
    if pokemon is None:
        return None
    pokemon_update = new_pokemon.model_dump(exclude_unset=True)
    pokemon.sqlmodel_update(pokemon_update)
    session.add(pokemon)
    session.commit()
    session.refresh(pokemon)

    return pokemon


def kill_one_pokemon_db(id: int, session: Session):
    try:
        pokemon = session.get_one(PokemonID, id)
        session.delete(pokemon)
        session.commit()
        return pokemon
    except NoResultFound:
        return None



def update_pokemon_image_db(id: int, image_url: str, session: Session):
    pokemon = find_one_pokemon_db(id, session)
    if pokemon is None:
        return None
    pokemon.image_url = image_url
    session.add(pokemon)
    session.commit()
    session.refresh(pokemon)
    return pokemon

