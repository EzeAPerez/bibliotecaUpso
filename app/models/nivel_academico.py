from sqlmodel import SQLModel, Field

class NivelAcademico(SQLModel, table=True):
    __tablename__ = "nivel_academico"
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=50)

class NivelAcademicoCreate(SQLModel):
    nombre: str = Field(max_length=50)

class NivelAcademicoUpdate(SQLModel):
    nombre: str = Field(default=None, max_length=50)