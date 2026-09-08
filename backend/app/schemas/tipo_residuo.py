from pydantic import BaseModel, ConfigDict


class TipoResiduoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None
    unidad_medida: str
    peligroso: bool
    activo: bool


class TipoResiduoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None
    unidad_medida: str = "kg"
    peligroso: bool = False


class TipoResiduoUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    unidad_medida: str | None = None
    peligroso: bool | None = None
    activo: bool | None = None
