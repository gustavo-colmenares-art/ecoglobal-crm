from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ManifiestoItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manifiesto_id: int
    tipo_residuo_id: int
    cantidad_declarada: Decimal | None = None
    cantidad_real: Decimal | None = None
    unidad_medida: str | None = None
    descripcion_adicional: str | None = None
    numero_contenedor: str | None = None
    observaciones: str | None = None


class ManifiestoItemCreate(BaseModel):
    tipo_residuo_id: int
    cantidad_declarada: Decimal | None = None
    unidad_medida: str | None = None
    descripcion_adicional: str | None = None
    numero_contenedor: str | None = None
    observaciones: str | None = None


class ManifiestoItemUpdate(BaseModel):
    cantidad_real: Decimal | None = None
    cantidad_declarada: Decimal | None = None
    unidad_medida: str | None = None
    descripcion_adicional: str | None = None
    numero_contenedor: str | None = None
    observaciones: str | None = None


class ManifiestoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    servicio_id: int
    operario_id: int | None = None
    fecha_generacion: date
    fecha_recoleccion: date | None = None
    fecha_retorno: date | None = None
    estado: str
    firma_cliente: bool
    nombre_receptor: str | None = None
    cargo_receptor: str | None = None
    observaciones_campo: str | None = None
    observaciones_retorno: str | None = None
    creado_en: datetime
    items: list[ManifiestoItemOut] = []


class ManifiestoCreate(BaseModel):
    servicio_id: int
    operario_id: int | None = None
    fecha_recoleccion: date | None = None
    observaciones_campo: str | None = None
    items: list[ManifiestoItemCreate] = []


class ManifiestoUpdate(BaseModel):
    operario_id: int | None = None
    fecha_recoleccion: date | None = None
    fecha_retorno: date | None = None
    firma_cliente: bool | None = None
    nombre_receptor: str | None = None
    cargo_receptor: str | None = None
    observaciones_campo: str | None = None
    observaciones_retorno: str | None = None


class ManifiestoEstadoUpdate(BaseModel):
    estado_nuevo: str
    nota: str


class ManifiestoHistorialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado_antes: str | None = None
    estado_nuevo: str | None = None
    cambiado_por: int | None = None
    nota: str | None = None
    cambiado_en: datetime
