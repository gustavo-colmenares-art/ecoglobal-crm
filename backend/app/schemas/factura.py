from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FacturaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factura_id: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal | None = None
    descuento_pct: Decimal
    subtotal: Decimal | None = None
    tipo_residuo_id: int | None = None


class FacturaItemCreate(BaseModel):
    descripcion: str
    cantidad: Decimal = Decimal("1")
    precio_unitario: Decimal
    descuento_pct: Decimal = Decimal("0")
    tipo_residuo_id: int | None = None


class FacturaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    servicio_id: int
    cliente_id: int
    fecha_emision: date
    fecha_vencimiento: date | None = None
    subtotal: Decimal
    iva: Decimal
    descuento: Decimal
    total: Decimal
    estado: str
    observaciones: str | None = None
    condiciones_pago: str | None = None
    creado_en: datetime
    items: list[FacturaItemOut] = []


class FacturaCreate(BaseModel):
    servicio_id: int
    fecha_vencimiento: date | None = None
    descuento: Decimal = Decimal("0")
    condiciones_pago: str | None = None
    observaciones: str | None = None
    items: list[FacturaItemCreate] = []


class FacturaUpdate(BaseModel):
    fecha_vencimiento: date | None = None
    descuento: Decimal | None = None
    condiciones_pago: str | None = None
    observaciones: str | None = None


class FacturaEstadoUpdate(BaseModel):
    estado_nuevo: str
    nota: str | None = None


class FacturaDashboard(BaseModel):
    cartera_total: Decimal
    facturas_vencidas: int
    monto_vencido: Decimal
    por_cobrar: Decimal
