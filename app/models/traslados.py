from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date

class Traslados(SQLModel, table=True):
    __tablename__ = "traslados"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_ejemplar: Optional[int]
    id_reserva: Optional[int] = Field(default=None)
    id_sede_origen: Optional[int] = Field(default=None)
    id_sede_destino: Optional[int] = Field(default=None)
    fecha_solicitud: date
    fecha_entrega: Optional[date]
    encargado: Optional[str]
    obrservaciones: Optional[str]
    id_estado: int = Field(default=1)

class TrasladosUpdate(SQLModel):
    id_ejemplar: int | None = None
    id_reserva: int | None = None
    id_sede_origen: int | None = None
    id_sede_destino: int | None = None
    fecha_solicitud: date | None = None
    fecha_entrega: date | None = None
    encargado: str | None = None 
    obrservaciones: str | None = None
    id_estado: int | None = None 