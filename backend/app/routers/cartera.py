from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.cartera import Pago, SeguimientoCartera
from app.models.factura import Factura
from app.models.usuario import Usuario
from app.schemas.cartera import (
    CarteraDashboard,
    CarteraFacturaOut,
    CarteraReporte,
    GestionCreate,
    GestionOut,
    PagoCreate,
    PagoOut,
)
from app.schemas.common import APIResponse
from app.services.cartera import ESTADOS_ACTIVOS, actualizar_estado_por_pago, dias_vencida, saldo_factura

router = APIRouter(prefix="/api/v1/cartera", tags=["cartera"])

ROLES_ESCRITURA = ("superadmin", "cartera")


@router.get("", response_model=APIResponse[list[CarteraFacturaOut]])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    facturas = db.scalars(select(Factura).where(Factura.estado.in_(ESTADOS_ACTIVOS))).all()
    data = [
        CarteraFacturaOut(
            id=f.id,
            numero=f.numero,
            cliente_id=f.cliente_id,
            fecha_emision=f.fecha_emision,
            fecha_vencimiento=f.fecha_vencimiento,
            total=f.total,
            saldo=saldo_factura(f),
            estado=f.estado,
            dias_vencida=dias_vencida(f),
        )
        for f in facturas
    ]
    return APIResponse(data=data)


@router.get("/dashboard", response_model=APIResponse[CarteraDashboard])
def dashboard(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    facturas = db.scalars(select(Factura).where(Factura.estado.in_(ESTADOS_ACTIVOS))).all()
    cartera_total = sum((saldo_factura(f) for f in facturas), Decimal("0"))
    vencidas = [f for f in facturas if dias_vencida(f) > 0]
    monto_vencido = sum((saldo_factura(f) for f in vencidas), Decimal("0"))

    pagadas = db.scalars(select(Factura).where(Factura.estado == "pagada")).all()
    dias_recaudo = [
        (max(p.fecha_pago for p in f.pagos) - f.fecha_emision).days for f in pagadas if f.pagos
    ]
    promedio = sum(dias_recaudo) / len(dias_recaudo) if dias_recaudo else 0.0

    return APIResponse(
        data=CarteraDashboard(
            cartera_total=cartera_total,
            facturas_vencidas=len(vencidas),
            monto_vencido=monto_vencido,
            dias_promedio_recaudo=round(promedio, 1),
        )
    )


@router.get("/reporte", response_model=APIResponse[CarteraReporte])
def reporte(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    facturas = db.scalars(select(Factura).where(Factura.estado.in_(ESTADOS_ACTIVOS))).all()
    r0_30 = r31_60 = r61_90 = r_mas_90 = Decimal("0")
    for f in facturas:
        saldo = saldo_factura(f)
        dias = dias_vencida(f)
        if dias <= 30:
            r0_30 += saldo
        elif dias <= 60:
            r31_60 += saldo
        elif dias <= 90:
            r61_90 += saldo
        else:
            r_mas_90 += saldo
    return APIResponse(
        data=CarteraReporte(
            rango_0_30=r0_30,
            rango_31_60=r31_60,
            rango_61_90=r61_90,
            rango_mas_90=r_mas_90,
            total=r0_30 + r31_60 + r61_90 + r_mas_90,
        )
    )


@router.post("/pagos", response_model=APIResponse[PagoOut], status_code=201)
def registrar_pago(
    payload: PagoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    factura = db.get(Factura, payload.factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    pago = Pago(**payload.model_dump(), registrado_por=current_user.id)
    db.add(pago)
    db.flush()
    actualizar_estado_por_pago(factura)
    db.commit()
    db.refresh(pago)
    return APIResponse(data=PagoOut.model_validate(pago), message="Pago registrado")


@router.get("/pagos", response_model=APIResponse[list[PagoOut]])
def historial_pagos(
    factura_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Pago).order_by(Pago.fecha_pago.desc())
    if factura_id:
        stmt = stmt.where(Pago.factura_id == factura_id)
    pagos = db.scalars(stmt).all()
    return APIResponse(data=[PagoOut.model_validate(p) for p in pagos])


@router.post("/gestiones", response_model=APIResponse[GestionOut], status_code=201)
def registrar_gestion(
    payload: GestionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    if not db.get(Factura, payload.factura_id):
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    gestion = SeguimientoCartera(**payload.model_dump(), gestionado_por=current_user.id)
    db.add(gestion)
    db.commit()
    db.refresh(gestion)
    return APIResponse(data=GestionOut.model_validate(gestion), message="Gestión registrada")


@router.get("/gestiones/{factura_id}", response_model=APIResponse[list[GestionOut]])
def gestiones_de_factura(factura_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    if not db.get(Factura, factura_id):
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    gestiones = db.scalars(
        select(SeguimientoCartera)
        .where(SeguimientoCartera.factura_id == factura_id)
        .order_by(SeguimientoCartera.fecha_gestion.desc())
    ).all()
    return APIResponse(data=[GestionOut.model_validate(g) for g in gestiones])
