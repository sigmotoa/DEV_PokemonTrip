from sqlmodel import SQLModel, Field

class TrainerBase(SQLModel):
    name: str | None = Field(default=None,
                             min_length=5,
                             max_length=100)

class TrainerID(TrainerBase, table=True):
    id: int | None = Field(default=None, primary_key=True, gt=0)