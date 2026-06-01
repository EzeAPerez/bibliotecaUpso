from sqlmodel import SQLModel, Field

class Restricciones(SQLModel, table=True):
    __tablename__ = "restricciones"
    id: int = Field(primary_key=True)
    cantidad_obras: int
    cantidad_dias: int
    cantidad_renovaciones: int

class RestriccionesUpdate(SQLModel):
    cantidad_obras: int | None
    cantidad_dias: int | None
    cantidad_renovaciones: int | None