from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from typing import List

class SubAreaTematica(SQLModel, table=True):
    __tablename__ = "subarea_tematica"

    id: int = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    id_area_tematica: int = Field(foreign_key="areas_tematica.id")

class CreateSubAreaTematica(SQLModel):
    nombre: str = Field(max_length=100)
    id_area_tematica: int

class UpdateSubAreaTematica(SQLModel):
    nombre: str | None = Field(default=None, max_length=100)
    id_area_tematica: int | None = None