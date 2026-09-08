from pydantic import BaseModel, ConfigDict


class PlantaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    nit: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    telefono: str | None = None
    email: str | None = None
    contacto: str | None = None
    activo: bool


class PlantaCreate(BaseModel):
    nombre: str
    nit: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    telefono: str | None = None
    email: str | None = None
    contacto: str | None = None


class PlantaUpdate(BaseModel):
    nombre: str | None = None
    nit: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    telefono: str | None = None
    email: str | None = None
    contacto: str | None = None
    activo: bool | None = None
