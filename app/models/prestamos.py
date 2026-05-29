from typing import List, Optional
from sqlmodel import SQLModel, Field
from datetime import date


class Prestamos(SQLModel, table=True):
    __tablename__ = "prestamos"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_ejemplar: int = Field(foreign_key="ejemplar.id")
    id_reserva: Optional[int] = Field(default=None, foreign_key="reserva.id")
    id_user: int = Field(foreign_key="user.id")
    id_sede: int = Field(foreign_key="sede.id")
    fecha_prestamo: date
    fecha_vencimiento: Optional[date] = Field(default=None)
    fecha_devolucion: Optional[date] = Field(default=None)
    id_estado: int = Field(default=1)

class PrestamosUpdate(SQLModel):
    id_ejemplar: Optional[int] = None
    id_reserva: Optional[int] = None
    id_user: Optional[int] = None
    id_sede: Optional[int] = None
    fecha_prestamo: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    fecha_devolucion: Optional[date] = None
    id_estado: Optional[int] = None

class PrestamosCreate(SQLModel):
    id_ejemplar: int
    id_reserva: int | None
    id_sede: int
    fecha_prestamo: date
    fecha_vencimiento: date | None
    fecha_devolucion: date | None
    id_estado: int

class PrestamosDetallado(SQLModel):
    id: int

    id_ejemplar: int
    titulo: str
    subtitulo: str

    id_reserva: int | None
    
    id_user: int
    nombre: str | None
    correo: str | None

    id_sede: int
    nombre_sede: str

    fecha_prestamo: date
    fecha_vencimiento: date | None
    fecha_devolucion: date | None

    id_estado: int
    nombre_estado: str