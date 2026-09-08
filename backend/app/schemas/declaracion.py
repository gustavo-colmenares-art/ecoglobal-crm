from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DeclaracionItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    declaracion_id: int
    manifiesto_item_id: int | None = None
    tipo_residuo_id: int
    cantidad: Decimal | None = None
    unidad_medida: str | None = None
    observaciones: str | None = None


class DeclaracionItemCreate(BaseModel):
    manifiesto_item_id: int | None = None
    tipo_residuo_id: int
    cantidad: Decimal | None = None
    unidad_medida: str | None = None
    observaciones: str | None = None


class DeclaracionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    manifiesto_id: int
    planta_id: int
    fecha_envio: date | None = None
    fecha_certificacion: date | None = None
    numero_certificado: str | None = None
    estado: str
    observaciones: str | None = None
    creado_en: datetime
    items: list[DeclaracionItemOut] = []


class DeclaracionCreate(BaseModel):
    manifiesto_id: int
    planta_id: int
    fecha_envio: date | None = None
    observaciones: str | None = None
    items: list[DeclaracionItemCreate] = []


class DeclaracionUpdate(BaseModel):
    planta_id: int | None = None
    fecha_envio: date | None = None
    observaciones: str | None = None


class DeclaracionEstadoUpdate(BaseModel):
    estado_nuevo: str
    nota: str | None = None


class DeclaracionCertificar(BaseModel):
    numero_certificado: str
    fecha_certificacion: date
