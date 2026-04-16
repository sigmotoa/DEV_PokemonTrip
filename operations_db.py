from sqlmodel import  Session

from models import PokemonBase, PokemonID


def createPokemon_db(pokemon:PokemonBase, session:Session):
    new_pokemon = PokemonID.model_validate(pokemon)
    session.add(new_pokemon)
    session.commit()
    session.refresh(new_pokemon)

    return new_pokemon