from typing import List, Optional
from sqlmodel import SQLModel, Field
from datetime import date

class Renovaciones(SQLModel, table=True):
    __tablename__ = "renovaciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_prestamo: int = Field(foreign_key="prestamos.id")
    fecha_renovacion: date
    fecha_vencimiento_anterior: date
    fecha_vencimiento_nueva: date

class RenovacionesUpdate(SQLModel):
    id_prestamo: Optional[int]
    fecha_renovacion: Optional[date]
    fecha_vencimiento_anterior: Optional[date]
    fecha_vencimiento_nueva: Optional[date]

class RenovacionesCreate(SQLModel):
    id_prestamo: int
    fecha_renovacion: date 
    fecha_vencimiento_anterior: date
    fecha_vencimiento_nueva: date

class RenovacionesCreateUser(SQLModel):
    id_prestamo: int


class RenovacionesDetallada(SQLModel):
    id: int
    id_prestamo: int
    id_user: int
    
    titulo: str
    subtitulo: str
    codigo_fisico: str

    fecha_renovacion: date 
    fecha_vencimiento_anterior: date
    fecha_vencimiento_nueva: date

class PaginatedRenovaciones(SQLModel):
    items: List[RenovacionesDetallada]
    total: int