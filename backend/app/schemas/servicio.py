from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.cliente import ClienteOut


class ServicioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    cliente_id: int
    fecha_solicitud: date
    fecha_programada: date | None = None
    descripcion: str | None = None
    direccion_servicio: str | None = None
    ciudad_servicio: str | None = None
    estado: str
    prioridad: str
    observaciones: str | None = None
    creado_en: datetime
    actualizado_en: datetime


class ServicioCreate(BaseModel):
    cliente_id: int
    fecha_programada: date | None = None
    descripcion: str | None = None
    direccion_servicio: str | None = None
    ciudad_servicio: str | None = None
    prioridad: str = "normal"
    observaciones: str | None = None


class ServicioUpdate(BaseModel):
    fecha_programada: date | None = None
    descripcion: str | None = None
    direccion_servicio: str | None = None
    ciudad_servicio: str | None = None
    prioridad: str | None = None
    observaciones: str | None = None


class ServicioEstadoUpdate(BaseModel):
    estado_nuevo: str
    nota: str


class ServicioHistorialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado_antes: str | None = None
    estado_nuevo: str | None = None
    cambiado_por: int | None = None
    nota: str | None = None
    cambiado_en: datetime


class ManifiestoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    estado: str


class FacturaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    estado: str
    total: float


class ServicioDetalle(ServicioOut):
    cliente: ClienteOut | None = None
    manifiesto: ManifiestoResumen | None = None
    factura: FacturaResumen | None = None


class ServiciosDashboard(BaseModel):
    por_estado: dict[str, int]
    por_mes: dict[str, int]
    total: int


class ServicioDesdeFormulario(BaseModel):
    razon_social: str
    nit: str
    direccion: str | None = None
    telefono: str | None = None
    email: str | None = None
    contacto_nombre: str | None = None
    tipo_residuo: str | None = None
    fecha_recoleccion: date | None = None
