from sqlmodel import SQLModel, Field

class Formato(SQLModel, table=True):
    __tablename__ = "formato"
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=50)

class FormatoCreate(SQLModel):
    nombre: str = Field(max_length=50)

class FormatoUpdate(SQLModel):
    nombre: str = Field(default=None, max_length=50)