from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.cliente import ClienteOut


class LeadMensajeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    direccion: str
    texto: str
    enviado_en: datetime


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    canal: str
    telefono: str
    nombre_contacto: str | None = None
    estado: str
    tipo_interes: str | None = None
    cliente_id: int | None = None
    servicio_id: int | None = None
    asignado_a: int | None = None
    notas: str | None = None
    creado_en: datetime
    actualizado_en: datetime


class LeadDetalle(LeadOut):
    cliente: ClienteOut | None = None
    mensajes: list[LeadMensajeOut] = []


class LeadEstadoUpdate(BaseModel):
    estado_nuevo: str
    tipo_interes: str | None = None
    nota: str | None = None


class LeadAsignar(BaseModel):
    usuario_id: int


class LeadConvertir(BaseModel):
    razon_social: str
    nit: str
    direccion: str | None = None
    ciudad: str | None = None
    email: str | None = None
    contacto_nombre: str | None = None
    fecha_programada: str | None = None  # YYYY-MM-DD, opcional
    descripcion: str | None = None


class LeadMensajeEntrante(BaseModel):
    """Payload que envía el puente de WhatsApp por cada mensaje recibido."""

    telefono: str
    nombre_contacto: str | None = None
    texto: str


class LeadMensajeSaliente(BaseModel):
    texto: str
