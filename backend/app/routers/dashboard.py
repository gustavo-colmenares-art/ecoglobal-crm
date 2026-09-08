from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.models.manifiesto import Manifiesto
from app.models.servicio import Servicio
from app.models.usuario import Usuario
from app.schemas.common import APIResponse
from app.schemas.dashboard import (
    AlertaCotizacion,
    AlertaDeclaracion,
    AlertaFactura,
    AlertaLead,
    AlertaManifiesto,
    DashboardAlertas,
    DashboardGeneral,
    FlujoEtapa,
)
from app.services import alertas
from app.services.cartera import ESTADOS_ACTIVOS, saldo_factura

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

ESTADOS_SERVICIO_ACTIVOS = (
    "cotizado",
    "confirmado",
    "programado",
    "en_ruta",
    "atendido",
    "manifiesto_pendiente",
    "manifiesto_recibido",
)

ORDEN_PIPELINE = [
    "cotizado",
    "confirmado",
    "programado",
    "en_ruta",
    "atendido",
    "manifiesto_pendiente",
    "manifiesto_recibido",
    "completado",
    "cancelado",
]


@router.get("", response_model=APIResponse[DashboardGeneral])
def general(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    total_clientes = db.scalar(select(func.count()).select_from(Cliente).where(Cliente.activo.is_(True))) or 0
    servicios_activos = (
        db.scalar(
            select(func.count()).select_from(Servicio).where(Servicio.estado.in_(ESTADOS_SERVICIO_ACTIVOS))
        )
        or 0
    )
    manifiestos_en_campo = (
        db.scalar(select(func.count()).select_from(Manifiesto).where(Manifiesto.estado == "en_campo")) or 0
    )
    facturas_venc = len(alertas.facturas_vencidas(db))
    facturas_activas = db.scalars(select(Factura).where(Factura.estado.in_(ESTADOS_ACTIVOS))).all()
    cartera_total = sum((saldo_factura(f) for f in facturas_activas), Decimal("0"))

    return APIResponse(
        data=DashboardGeneral(
            total_clientes=total_clientes,
            servicios_activos=servicios_activos,
            manifiestos_en_campo=manifiestos_en_campo,
            facturas_vencidas=facturas_venc,
            cartera_total=cartera_total,
        )
    )


@router.get("/flujo", response_model=APIResponse[list[FlujoEtapa]])
def flujo(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    rows = dict(db.execute(select(Servicio.estado, func.count()).group_by(Servicio.estado)).all())
    return APIResponse(data=[FlujoEtapa(estado=estado, cantidad=rows.get(estado, 0)) for estado in ORDEN_PIPELINE])


@router.get("/alertas", response_model=APIResponse[DashboardAlertas])
def alertas_endpoint(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return APIResponse(
        data=DashboardAlertas(
            manifiestos_demorados=[
                AlertaManifiesto(id=m.id, numero=m.numero, fecha_recoleccion=str(m.fecha_recoleccion))
                for m in alertas.manifiestos_demorados(db)
            ],
            declaraciones_sin_certificar=[
                AlertaDeclaracion(id=d.id, numero=d.numero, fecha_envio=str(d.fecha_envio))
                for d in alertas.declaraciones_sin_certificar(db)
            ],
            facturas_por_vencer=[
                AlertaFactura(id=f.id, numero=f.numero, fecha_vencimiento=str(f.fecha_vencimiento), total=f.total)
                for f in alertas.facturas_por_vencer(db)
            ],
            facturas_vencidas=[
                AlertaFactura(id=f.id, numero=f.numero, fecha_vencimiento=str(f.fecha_vencimiento), total=f.total)
                for f in alertas.facturas_vencidas(db)
            ],
            cotizaciones_sin_seguimiento=[
                AlertaCotizacion(
                    id=s.id, numero=s.numero, creado_en=str(s.creado_en), actualizado_en=str(s.actualizado_en)
                )
                for s in alertas.servicios_cotizados_sin_seguimiento(db)
            ],
            leads_sin_atender=[
                AlertaLead(id=lead.id, telefono=lead.telefono, nombre_contacto=lead.nombre_contacto, creado_en=str(lead.creado_en))
                for lead in alertas.leads_sin_atender(db)
            ],
        )
    )
