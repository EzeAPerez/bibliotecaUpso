from typing import List, Optional
from sqlmodel import SQLModel, Field

class Ejemplar(SQLModel, table=True):
    __tablename__ = "ejemplar"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_obra: int =  Field(foreign_key="obras.id")
    codigo_fisico: Optional[str] = Field(max_length=15)
    formato: Optional[int] = Field(default=None, foreign_key="formato.id")
    ubicacion_fisica: Optional[str] = Field(default=None, max_length=255)
    anio_ingreso: Optional[int]
    tipo_de_ingreso: Optional[int] = Field(default=None, foreign_key="tipo_ingreso.id")
    id_sede: int = Field(foreign_key="sedes.id")
    id_estado: int = Field(default=1, foreign_key="estado_obra.id")
    url: Optional[str] = Field(default=None, max_length=255)
    
class EjemplarUpdate(SQLModel):
    id_obra: Optional[int] = None
    codigo_fisico: Optional[str] = Field(default=None, max_length=15)
    formato: Optional[int] = Field(default=None)
    ubicacion_fisica: Optional[str] = Field(default=None, max_length=255)
    anio_ingreso: Optional[int]
    tipo_de_ingreso: Optional[int] = Field(default=None)
    id_sede: Optional[int] = None
    id_estado: Optional[int] = None
    url: Optional[str] = Field(default=None, max_length=255)

class EjemplarCreate(SQLModel):
    id_obra: int 
    codigo_fisico: str | None = Field(max_length=15)
    formato: int | None = Field(default=None)
    ubicacion_fisica: str | None = Field(default=None, max_length=255)
    anio_ingreso: int | None
    tipo_de_ingreso: int | None = Field(default=None)
    id_sede: int
    id_estado: int = 1
    url: str | None = Field(default=None, max_length=255)

class Subarea(SQLModel):
    id: int
    nombre: str


class Area(SQLModel):
    id: int
    nombre: str
    subareas: List[Subarea]

## modificar!
class EjemplarDetallado(SQLModel):
    id: int

    codigo_fisico: str
    formato: Optional[int]
    nombre_formato: Optional[str]
    ubicacion_fisica: Optional[str]
    anio_ingreso: Optional[int]
    tipo_de_ingreso: Optional[int]
    nombre_tipo_ingreso: Optional[str]
    id_sede: int
    nombre_sede: str
    id_estado: int
    nombres_estado: str
    
    id_obra: int
    id_tipo_material: int
    tipo_material: str
    titulo: str
    subtitulo: Optional[str]
    anio: Optional[int]
    autor: Optional[str]
    
    isbn: Optional[str]
    edicion: Optional[str]
    tomo: Optional[str]
    editorial: Optional[str]

    issn: Optional[str]
    volumen: Optional[str]
    numero: Optional[str]

    institucion: Optional[str]
    nivel_academico: Optional[int]
    nombre_nivel_academico: Optional[str]

    areas: List[Area]