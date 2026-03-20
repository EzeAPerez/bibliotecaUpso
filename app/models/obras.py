from typing import List, Optional
from sqlmodel import SQLModel, Field

from models.area_tematica import AreaTematica
from models.obras_subareas import obrasysubareas

class Obras(SQLModel, table=True):
    __tablename__ = "obras"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_tipo_material: int = Field(foreign_key="tipo_material.id")
    codigo_fisico: str = Field(max_length=15)
    titulo: str = Field(max_length=150)
    subtitulo: Optional[str] = Field(default=None, max_length=150)
    formato: Optional[str] = Field(default=None, max_length=50)
    anio: Optional[int]
    autor: Optional[str] = Field(default=None, max_length=255)
    ubicacion_fisica: Optional[str] = Field(default=None, max_length=255)
    anio_ingreso: Optional[int]
    tipo_de_ingreso: Optional[str] = Field(default=None, max_length=100)
    id_sede: int = Field(foreign_key="sedes.id")
    id_estado: int = Field(default=1, foreign_key="estado_obra.id")
    
    ##Libros##
    isbn: Optional[str] = Field(default=None, max_length=20)
    edicion: Optional[str] = Field(default=None, max_length=50)
    tomo: Optional[str] = Field(default=None, max_length=20)
    editorial: Optional[str] = Field(default=None, max_length=100)

    ##Revista##
    issn: Optional[str] = Field(default=None, max_length=15)
    volumen: Optional[str] = Field(default=None, max_length=100)
    numero: Optional[str] = Field(default=None, max_length=100)

    ##Tessis##
    institucion: Optional[str] = Field(default=None, max_length=255)
    nivel_academico: Optional[str] = Field(default=None, max_length=150)

class ObraUpdate(SQLModel):
    id_tipo_material: Optional[int] = None
    codigo_fisico: Optional[str] = Field(default=None, max_length=15)
    titulo: Optional[str] = Field(default=None, max_length=150)
    subtitulo: Optional[str] = Field(default=None, max_length=150)
    formato: Optional[str] = Field(default=None, max_length=50)
    anio: Optional[int] = None
    autor: Optional[str] = Field(default=None, max_length=255)
    ubicacion_fisica: Optional[str] = Field(default=None, max_length=255)
    anio_ingreso: Optional[int] = None
    tipo_de_ingreso: Optional[str] = Field(default=None, max_length=100)
    id_sede: Optional[int] = None
    id_estado: Optional[int] = None

    ## Libros ##
    isbn: Optional[str] = Field(default=None, max_length=20)
    edicion: Optional[str] = Field(default=None, max_length=50)
    tomo: Optional[str] = Field(default=None, max_length=20)
    editorial: Optional[str] = Field(default=None, max_length=100)

    ## Revista ##
    issn: Optional[str] = Field(default=None, max_length=15)
    volumen: Optional[str] = Field(default=None, max_length=100)
    numero: Optional[str] = Field(default=None, max_length=100)

    ## Tesis ##
    institucion: Optional[str] = Field(default=None, max_length=100)
    nivel_academico: Optional[str] = Field(default=None, max_length=100)

class ObraCreate(SQLModel):
    codigo_fisico: str = Field(max_length=15)
    id_tipo_material: int 
    titulo: str = Field(max_length=250)
    subtitulo: str | None = Field(default=None, max_length=150)
    formato: str | None = Field(default=None, max_length=50)
    anio: int | None = None
    autor: str | None = Field(default=None, max_length=255)
    ubicacion_fisica: str | None = Field(default=None, max_length=255)
    anio_ingreso: int | None = None
    tipo_de_ingreso: str | None = Field(default=None, max_length=100)
    id_sede: int
    id_estado: int = 1

    isbn: str | None = Field(default=None, max_length=20)
    edicion: str | None = Field(default=None, max_length=50)
    tomo: str | None = Field(default=None, max_length=20)
    editorial: str | None = Field(default=None, max_length=100)

    issn: str | None = Field(default=None, max_length=15)
    volumen: str | None = Field(default=None, max_length=100)
    numero: str | None = Field(default=None, max_length=100)

    institucion: str | None = Field(default=None, max_length=100)
    nivel_academico: str | None = Field(default=None, max_length=100)

    subareas: List[int] = Field(default_factory=list)

class Subarea(SQLModel):
    id: int
    nombre: str


class Area(SQLModel):
    id: int
    nombre: str
    subareas: List[Subarea]


class ObraDetallada(SQLModel):
    id: int
    codigo_fisico: str
    id_tipo_material: int
    tipo_material: str
    titulo: str
    subtitulo: Optional[str]
    formato: Optional[str]
    anio: Optional[int]
    autor: Optional[str]
    ubicacion_fisica: Optional[str]
    anio_ingreso: Optional[int]
    tipo_de_ingreso: Optional[str]
    id_sede: int
    nombre_sede: str
    id_estado: int

    isbn: Optional[str]
    edicion: Optional[str]
    tomo: Optional[str]
    editorial: Optional[str]

    issn: Optional[str]
    volumen: Optional[str]
    numero: Optional[str]

    institucion: Optional[str]
    nivel_academico: Optional[str]

    areas: List[Area]