from decimal import Decimal

from pydantic import BaseModel


class DashboardGeneral(BaseModel):
    total_clientes: int
    servicios_activos: int
    manifiestos_en_campo: int
    facturas_vencidas: int
    cartera_total: Decimal


class FlujoEtapa(BaseModel):
    estado: str
    cantidad: int


class AlertaManifiesto(BaseModel):
    id: int
    numero: str
    fecha_recoleccion: str | None = None


class AlertaDeclaracion(BaseModel):
    id: int
    numero: str
    fecha_envio: str | None = None


class AlertaFactura(BaseModel):
    id: int
    numero: str
    fecha_vencimiento: str | None = None
    total: Decimal


class AlertaCotizacion(BaseModel):
    id: int
    numero: str
    creado_en: str
    actualizado_en: str


class AlertaLead(BaseModel):
    id: int
    telefono: str
    nombre_contacto: str | None = None
    creado_en: str


class DashboardAlertas(BaseModel):
    manifiestos_demorados: list[AlertaManifiesto]
    declaraciones_sin_certificar: list[AlertaDeclaracion]
    facturas_por_vencer: list[AlertaFactura]
    facturas_vencidas: list[AlertaFactura]
    cotizaciones_sin_seguimiento: list[AlertaCotizacion] = []
    leads_sin_atender: list[AlertaLead] = []
