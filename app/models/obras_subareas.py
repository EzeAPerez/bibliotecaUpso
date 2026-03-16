from sqlmodel import SQLModel, Field

class obrasysubareas(SQLModel, table=True):
    __tablename__ = "obra_subarea_tematica"

    id_obra: int = Field(foreign_key="obras.id", primary_key=True)
    id_subarea: int = Field(foreign_key="subarea_tematica.id", primary_key=True)

class ObrasySubareasDetallado(SQLModel):
    id_obra: int
    id_subarea: int
    nombre_obra: str
    nombre_subarea: str
    nombre_area: str
    id_area: int
