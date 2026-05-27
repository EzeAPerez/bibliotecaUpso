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
    observaciones: Optional[str]
    id_estado: int = Field(default=1)

class TrasladosUpdate(SQLModel):
    id_ejemplar: int | None = None
    id_reserva: int | None = None
    id_sede_origen: int | None = None
    id_sede_destino: int | None = None
    fecha_solicitud: date | None = None
    fecha_entrega: date | None = None
    encargado: str | None = None 
    observaciones: str | None = None
    id_estado: int | None = None 

class TrasladosCreate(SQLModel):
    id_ejemplar: Optional[int] = None
    id_reserva: Optional[int] = Field(default=None)
    id_sede_origen: Optional[int] = Field(default=None)
    id_sede_destino: Optional[int] = Field(default=None)
    fecha_entrega: Optional[date] = None
    encargado: Optional[str] = None
    observaciones: Optional[str] = None
    id_estado: int = Field(default=1)

class TrasladosDetallado(SQLModel):
    id: int
    id_ejemplar: Optional[int]
    codigo_ejemplar: Optional[str] = None
    titulo_obra: Optional[str] = None
    subtitulo_obra: Optional[str] = None
    id_reserva: Optional[int] = None
    id_sede_origen: Optional[int] = None
    nombre_sede_origen: Optional[str] = None
    id_sede_destino: Optional[int] = None
    nombre_sede_destino: Optional[str] = None
    fecha_solicitud: date
    fecha_entrega: Optional[date]
    encargado: Optional[str]
    observaciones: Optional[str]
    id_estado: int
    nombre_estado: Optional[str]
