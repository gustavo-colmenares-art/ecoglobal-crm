from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str
    nit: str
    direccion: str | None = None
    ciudad: str | None = None
    departamento: str | None = None
    telefono: str | None = None
    email: str | None = None
    contacto_nombre: str | None = None
    contacto_cargo: str | None = None
    activo: bool
    creado_en: datetime


class ClienteCreate(BaseModel):
    razon_social: str
    nit: str
    direccion: str | None = None
    ciudad: str | None = None
    departamento: str | None = None
    telefono: str | None = None
    email: str | None = None
    contacto_nombre: str | None = None
    contacto_cargo: str | None = None


class ClienteUpdate(BaseModel):
    razon_social: str | None = None
    nit: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    departamento: str | None = None
    telefono: str | None = None
    email: str | None = None
    contacto_nombre: str | None = None
    contacto_cargo: str | None = None
    activo: bool | None = None
