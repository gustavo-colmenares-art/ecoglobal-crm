from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PagoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factura_id: int
    fecha_pago: date
    monto: Decimal
    medio_pago: str | None = None
    referencia: str | None = None
    banco: str | None = None
    observaciones: str | None = None
    registrado_en: datetime


class PagoCreate(BaseModel):
    factura_id: int
    fecha_pago: date
    monto: Decimal
    medio_pago: str | None = None
    referencia: str | None = None
    banco: str | None = None
    observaciones: str | None = None


class GestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factura_id: int
    tipo_gestion: str | None = None
    fecha_gestion: date
    resultado: str | None = None
    proxima_accion: str | None = None
    fecha_proxima: date | None = None
    gestionado_por: int | None = None
    creado_en: datetime


class GestionCreate(BaseModel):
    factura_id: int
    tipo_gestion: str
    resultado: str | None = None
    proxima_accion: str | None = None
    fecha_proxima: date | None = None


class CarteraFacturaOut(BaseModel):
    id: int
    numero: str
    cliente_id: int
    fecha_emision: date
    fecha_vencimiento: date | None = None
    total: Decimal
    saldo: Decimal
    estado: str
    dias_vencida: int


class CarteraDashboard(BaseModel):
    cartera_total: Decimal
    facturas_vencidas: int
    monto_vencido: Decimal
    dias_promedio_recaudo: float


class CarteraReporte(BaseModel):
    rango_0_30: Decimal
    rango_31_60: Decimal
    rango_61_90: Decimal
    rango_mas_90: Decimal
    total: Decimal
