from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from models.trainer import TrainerBase, TrainerID


def createTrainer(trainer: TrainerBase, session: Session):
    new_trainer = TrainerID.model_validate(trainer)
    session.add(new_trainer)
    session.commit()
    session.refresh(new_trainer)
    return new_trainer

def findTrainer(id:int, session: Session):
    try:
        return session.get_one(TrainerID, id)
    except NoResultFound:
        return None

def update_trainer_image_db(id: int, image_url: str, session: Session):
    trainer = findTrainer(id, session)
    if trainer is None:
        return None
    trainer.image_url = image_url
    session.add(trainer)
    session.commit()
    session.refresh(trainer)
    return trainer