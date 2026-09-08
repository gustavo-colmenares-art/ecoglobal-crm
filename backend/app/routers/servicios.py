from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.models.manifiesto import Manifiesto
from app.models.servicio import Servicio, ServicioHistorial
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteOut
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.servicio import (
    FacturaResumen,
    ManifiestoResumen,
    ServicioCreate,
    ServicioDesdeFormulario,
    ServicioDetalle,
    ServicioEstadoUpdate,
    ServicioHistorialOut,
    ServicioOut,
    ServiciosDashboard,
    ServicioUpdate,
)
from app.services.estados import SERVICIO_TRANSICIONES, validar_transicion
from app.services.numbering import generar_numero
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/servicios", tags=["servicios"])

ROLES_ESCRITURA = ("superadmin", "comercial")
ROLES_ESTADO = ("superadmin", "comercial", "operaciones")


@router.get("", response_model=APIResponse[PaginatedResponse[ServicioOut]])
def listar(
    page: int = 1,
    size: int = 20,
    estado: str | None = None,
    cliente_id: int | None = None,
    fecha: date | None = None,
    prioridad: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Servicio).order_by(Servicio.creado_en.desc())
    if estado:
        stmt = stmt.where(Servicio.estado == estado)
    if cliente_id:
        stmt = stmt.where(Servicio.cliente_id == cliente_id)
    if fecha:
        stmt = stmt.where(Servicio.fecha_programada == fecha)
    if prioridad:
        stmt = stmt.where(Servicio.prioridad == prioridad)

    items, total, pages = paginate(db, stmt, page, size)
    return APIResponse(
        data=PaginatedResponse(items=[ServicioOut.model_validate(i) for i in items], total=total, page=page, pages=pages)
    )


@router.get("/dashboard", response_model=APIResponse[ServiciosDashboard])
def dashboard(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    por_estado_rows = db.execute(select(Servicio.estado, func.count()).group_by(Servicio.estado)).all()
    por_mes_rows = db.execute(
        select(extract("month", Servicio.fecha_solicitud), func.count())
        .where(extract("year", Servicio.fecha_solicitud) == date.today().year)
        .group_by(extract("month", Servicio.fecha_solicitud))
    ).all()
    total = db.scalar(select(func.count()).select_from(Servicio)) or 0
    return APIResponse(
        data=ServiciosDashboard(
            por_estado={estado: count for estado, count in por_estado_rows},
            por_mes={str(int(mes)): count for mes, count in por_mes_rows},
            total=total,
        )
    )


@router.post("", response_model=APIResponse[ServicioOut], status_code=201)
def crear(
    payload: ServicioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    if not db.get(Cliente, payload.cliente_id):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    numero = generar_numero(db, Servicio, "SRV")
    servicio = Servicio(numero=numero, **payload.model_dump(), creado_por=current_user.id)
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return APIResponse(data=ServicioOut.model_validate(servicio), message="Servicio creado")


@router.post("/desde-formulario", response_model=APIResponse[ServicioOut], status_code=201)
def crear_desde_formulario(
    payload: ServicioDesdeFormulario,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    """Punto de entrada para automatizaciones externas (ej. n8n) que reciben
    respuestas del formulario de solicitud de servicio y las convierten en
    un cliente (si no existe, por NIT) + un servicio en estado 'cotizado'."""
    cliente = db.scalar(select(Cliente).where(Cliente.nit == payload.nit))
    if not cliente:
        cliente = Cliente(
            razon_social=payload.razon_social,
            nit=payload.nit,
            direccion=payload.direccion,
            telefono=payload.telefono,
            email=payload.email,
            contacto_nombre=payload.contacto_nombre,
            creado_por=current_user.id,
        )
        db.add(cliente)
        db.flush()

    servicio = Servicio(
        numero=generar_numero(db, Servicio, "SRV"),
        cliente_id=cliente.id,
        fecha_programada=payload.fecha_recoleccion,
        descripcion=f"Solicitud via formulario - {payload.tipo_residuo}" if payload.tipo_residuo else "Solicitud via formulario",
        direccion_servicio=payload.direccion,
        creado_por=current_user.id,
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return APIResponse(data=ServicioOut.model_validate(servicio), message="Servicio creado desde formulario")


@router.get("/{servicio_id}", response_model=APIResponse[ServicioDetalle])
def obtener(servicio_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    servicio = db.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    cliente = db.get(Cliente, servicio.cliente_id)
    manifiesto = db.scalar(
        select(Manifiesto).where(Manifiesto.servicio_id == servicio_id).order_by(Manifiesto.creado_en.desc())
    )
    factura = db.scalar(
        select(Factura).where(Factura.servicio_id == servicio_id).order_by(Factura.creado_en.desc())
    )

    detalle = ServicioDetalle(
        **ServicioOut.model_validate(servicio).model_dump(),
        cliente=ClienteOut.model_validate(cliente) if cliente else None,
        manifiesto=ManifiestoResumen.model_validate(manifiesto) if manifiesto else None,
        factura=FacturaResumen.model_validate(factura) if factura else None,
    )
    return APIResponse(data=detalle)


@router.put("/{servicio_id}", response_model=APIResponse[ServicioOut])
def actualizar(
    servicio_id: int,
    payload: ServicioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    servicio = db.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(servicio, field, value)
    db.commit()
    db.refresh(servicio)
    return APIResponse(data=ServicioOut.model_validate(servicio), message="Servicio actualizado")


@router.patch("/{servicio_id}/estado", response_model=APIResponse[ServicioOut])
def cambiar_estado(
    servicio_id: int,
    payload: ServicioEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESTADO)),
):
    servicio = db.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    if payload.estado_nuevo == "cancelado":
        if current_user.rol.nombre not in ("superadmin", "comercial"):
            raise HTTPException(status_code=403, detail="Solo admin o comercial pueden cancelar")
    elif not validar_transicion(SERVICIO_TRANSICIONES, servicio.estado, payload.estado_nuevo):
        raise HTTPException(
            status_code=400,
            detail=f"Transición inválida: {servicio.estado} → {payload.estado_nuevo}",
        )

    estado_antes = servicio.estado
    servicio.estado = payload.estado_nuevo
    db.add(
        ServicioHistorial(
            servicio_id=servicio.id,
            estado_antes=estado_antes,
            estado_nuevo=payload.estado_nuevo,
            cambiado_por=current_user.id,
            nota=payload.nota,
        )
    )
    db.commit()
    db.refresh(servicio)
    return APIResponse(data=ServicioOut.model_validate(servicio), message="Estado actualizado")


@router.get("/{servicio_id}/historial", response_model=APIResponse[list[ServicioHistorialOut]])
def historial(servicio_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    if not db.get(Servicio, servicio_id):
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    registros = db.scalars(
        select(ServicioHistorial)
        .where(ServicioHistorial.servicio_id == servicio_id)
        .order_by(ServicioHistorial.cambiado_en)
    ).all()
    return APIResponse(data=[ServicioHistorialOut.model_validate(r) for r in registros])
