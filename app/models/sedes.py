from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from typing import List

class Sede(SQLModel, table=True):
    __tablename__ = "sedes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50)

class SedeCreate(SQLModel):
    nombre: str = Field(max_length=50)

class SedeUpdate(SQLModel):
    nombre: str = Field(default=None, max_length=50)
