from sqlmodel import Session, select
from models.trainer import TrainerBase, TrainerID


def createTrainer(trainer: TrainerBase, session: Session):
    new_trainer = TrainerID.model_validate(trainer)
    session.add(new_trainer)
    session.commit()
    session.refresh(new_trainer)
    return new_trainer

