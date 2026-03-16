from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from typing import List

class EstadoObra(SQLModel, table=True):
    __tablename__ = "estado_obra"
    id: int = Field(primary_key=True)
    estado: str = Field(max_length=50)
