from sqlmodel import SQLModel, Field

class TipoIngreso(SQLModel, table=True):
    __tablename__ = "tipo_ingreso"
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=50)

class TipoIngresoCreate(SQLModel):
    nombre: str = Field(max_length=50)

class TipoIngresoUpdate(SQLModel):
    nombre: str = Field(default=None, max_length=50)