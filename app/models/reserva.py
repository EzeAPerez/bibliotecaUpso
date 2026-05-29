from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date

class Reserva(SQLModel, table=True):
    __tablename__ = "reserva"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    id_obra: int = Field(foreign_key="obras.id")
    id_ejemplar: Optional[int] = Field(default=None, foreign_key="ejemplar.id")
    id_user: int = Field(foreign_key="users.id")
    id_sede: int = Field(foreign_key="sedes.id")
    fecha_solicitud: date
    fecha_confirmacion: Optional[date] = Field(default=None)
    fecha_retiro: Optional[date] = Field(default=None)
    id_estado: int = Field(default=1, foreign_key="estado_reserva.id")


class ReservaUpdate(SQLModel):
    id_obra: Optional[int] = None
    id_ejemplar: Optional[int] = None
    id_sede: Optional[int] = None
    fecha_solicitud: Optional[date] = None 
    fecha_confirmacion: Optional[date] = None
    fecha_retiro: Optional[date] = None
    id_estado: Optional[int] = None

class ReservaCreate(SQLModel):
    id_obra: int
    id_ejemplar: Optional[int] = None
    id_sede: int
    fecha_solicitud: date
    fecha_confirmacion: Optional[date] = None
    fecha_retiro: Optional[date] = None
    id_estado: int

class ReservaCreateUser(SQLModel):
    id_obra: int
    id_sede: int


class ReservaDetallada(SQLModel):
    id: int
    id_obra:int
    titulo: str
    subtitulo: str
    autor: str

    id_ejemplar: Optional[int] = None
    codigo_fisico: Optional[str] = None
    
    id_user: Optional[int] = None
    correo: Optional[str] = None 

    id_sede: int
    nombre_sede: str

    fecha_solicitud: date
    fecha_confirmacion: Optional[date] = None
    fecha_retiro: Optional[date] = None

    id_estado: int
    nombre_estado: str