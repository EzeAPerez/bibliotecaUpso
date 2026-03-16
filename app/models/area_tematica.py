from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from typing import List

class AreaTematica(SQLModel, table=True):
    _tablename_ = "areas_tematica"

    id: int = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)

class CreateAreaTematica(SQLModel):
    nombre: str = Field(max_length=100)

class UpdateAreaTematica(SQLModel):
    nombre: str = Field(max_length=100)
