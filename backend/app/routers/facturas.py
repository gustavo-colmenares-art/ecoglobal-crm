from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.cliente import Cliente
from app.models.factura import Factura, FacturaItem
from app.models.servicio import Servicio
from app.models.usuario import Usuario
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.factura import (
    FacturaCreate,
    FacturaDashboard,
    FacturaEstadoUpdate,
    FacturaItemCreate,
    FacturaItemOut,
    FacturaOut,
    FacturaUpdate,
)
from app.services.estados import FACTURA_TRANSICIONES, validar_transicion
from app.services.facturacion import calcular_subtotal_item, recalcular_factura
from app.services.numbering import generar_numero
from app.utils.pagination import paginate
from app.utils.pdf import generar_pdf_factura

router = APIRouter(prefix="/api/v1/facturas", tags=["facturas"])

ROLES_ESCRITURA = ("superadmin", "contabilidad")


def _crear_item(db: Session, factura_id: int, payload: FacturaItemCreate) -> FacturaItem:
    subtotal = calcular_subtotal_item(payload.cantidad, payload.precio_unitario, payload.descuento_pct)
    item = FacturaItem(factura_id=factura_id, subtotal=subtotal, **payload.model_dump())
    db.add(item)
    return item


@router.get("", response_model=APIResponse[PaginatedResponse[FacturaOut]])
def listar(
    page: int = 1,
    size: int = 20,
    estado: str | None = None,
    cliente_id: int | None = None,
    vencimiento: date | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Factura).order_by(Factura.creado_en.desc())
    if estado:
        stmt = stmt.where(Factura.estado == estado)
    if cliente_id:
        stmt = stmt.where(Factura.cliente_id == cliente_id)
    if vencimiento:
        stmt = stmt.where(Factura.fecha_vencimiento == vencimiento)
    items, total, pages = paginate(db, stmt, page, size)
    return APIResponse(
        data=PaginatedResponse(items=[FacturaOut.model_validate(i) for i in items], total=total, page=page, pages=pages)
    )


@router.get("/dashboard", response_model=APIResponse[FacturaDashboard])
def dashboard(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    cartera_total = db.scalar(
        select(func.coalesce(func.sum(Factura.total), 0)).where(Factura.estado.notin_(["pagada", "anulada", "borrador"]))
    ) or Decimal("0")
    vencidas_stmt = select(Factura).where(
        Factura.estado.notin_(["pagada", "anulada", "borrador"]),
        Factura.fecha_vencimiento < date.today(),
    )
    facturas_vencidas = db.scalars(vencidas_stmt).all()
    monto_vencido = sum((f.total for f in facturas_vencidas), Decimal("0"))
    return APIResponse(
        data=FacturaDashboard(
            cartera_total=cartera_total,
            facturas_vencidas=len(facturas_vencidas),
            monto_vencido=monto_vencido,
            por_cobrar=cartera_total,
        )
    )


@router.post("", response_model=APIResponse[FacturaOut], status_code=201)
def crear(
    payload: FacturaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    servicio = db.get(Servicio, payload.servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    numero = generar_numero(db, Factura, "FAC")
    factura = Factura(
        numero=numero,
        servicio_id=payload.servicio_id,
        cliente_id=servicio.cliente_id,
        fecha_vencimiento=payload.fecha_vencimiento,
        descuento=payload.descuento,
        condiciones_pago=payload.condiciones_pago,
        observaciones=payload.observaciones,
        creado_por=current_user.id,
    )
    db.add(factura)
    db.flush()

    items = [_crear_item(db, factura.id, item) for item in payload.items]
    db.flush()
    recalcular_factura(factura, items)
    db.commit()
    db.refresh(factura)
    return APIResponse(data=FacturaOut.model_validate(factura), message="Factura creada")


@router.get("/{factura_id}", response_model=APIResponse[FacturaOut])
def obtener(factura_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    factura = db.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return APIResponse(data=FacturaOut.model_validate(factura))


@router.put("/{factura_id}", response_model=APIResponse[FacturaOut])
def actualizar(
    factura_id: int,
    payload: FacturaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    factura = db.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(factura, field, value)
    recalcular_factura(factura, factura.items)
    db.commit()
    db.refresh(factura)
    return APIResponse(data=FacturaOut.model_validate(factura), message="Factura actualizada")


@router.patch("/{factura_id}/estado", response_model=APIResponse[FacturaOut])
def cambiar_estado(
    factura_id: int,
    payload: FacturaEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    factura = db.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    if payload.estado_nuevo == "anulada":
        if current_user.rol.nombre not in ("superadmin", "contabilidad"):
            raise HTTPException(status_code=403, detail="Solo admin o contabilidad pueden anular")
    elif not validar_transicion(FACTURA_TRANSICIONES, factura.estado, payload.estado_nuevo):
        raise HTTPException(
            status_code=400,
            detail=f"Transición inválida: {factura.estado} → {payload.estado_nuevo}",
        )

    factura.estado = payload.estado_nuevo
    if payload.nota:
        factura.observaciones = f"{factura.observaciones or ''}\n{payload.nota}".strip()
    db.commit()
    db.refresh(factura)
    return APIResponse(data=FacturaOut.model_validate(factura), message="Estado actualizado")


@router.post("/{factura_id}/items", response_model=APIResponse[FacturaItemOut], status_code=201)
def agregar_item(
    factura_id: int,
    payload: FacturaItemCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    factura = db.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    item = _crear_item(db, factura_id, payload)
    db.flush()
    recalcular_factura(factura, factura.items)
    db.commit()
    db.refresh(item)
    return APIResponse(data=FacturaItemOut.model_validate(item), message="Ítem agregado")


@router.put("/{factura_id}/items/{item_id}", response_model=APIResponse[FacturaItemOut])
def actualizar_item(
    factura_id: int,
    item_id: int,
    payload: FacturaItemCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    factura = db.get(Factura, factura_id)
    item = db.get(FacturaItem, item_id)
    if not factura or not item or item.factura_id != factura_id:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item.subtotal = calcular_subtotal_item(item.cantidad, item.precio_unitario, item.descuento_pct)
    db.flush()
    recalcular_factura(factura, factura.items)
    db.commit()
    db.refresh(item)
    return APIResponse(data=FacturaItemOut.model_validate(item), message="Ítem actualizado")


@router.get("/{factura_id}/pdf")
def pdf(factura_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    factura = db.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    cliente = db.get(Cliente, factura.cliente_id)

    pdf_bytes = generar_pdf_factura(
        {
            "numero": factura.numero,
            "fecha_emision": factura.fecha_emision,
            "fecha_vencimiento": factura.fecha_vencimiento,
            "cliente": {
                "razon_social": cliente.razon_social,
                "nit": cliente.nit,
                "direccion": cliente.direccion,
                "ciudad": cliente.ciudad,
            },
            "items": [
                {
                    "descripcion": item.descripcion,
                    "cantidad": item.cantidad,
                    "precio_unitario": item.precio_unitario or Decimal("0"),
                    "descuento_pct": item.descuento_pct,
                    "subtotal": item.subtotal or Decimal("0"),
                }
                for item in factura.items
            ],
            "subtotal": factura.subtotal,
            "iva": factura.iva,
            "descuento": factura.descuento,
            "total": factura.total,
            "condiciones_pago": factura.condiciones_pago,
        }
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{factura.numero}.pdf"'},
    )
