from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None = None


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    rol: RolOut | None = None
    activo: bool
    creado_en: datetime
    ultimo_acceso: datetime | None = None


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol_id: int


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None
    rol_id: int | None = None
    activo: bool | None = None
