from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.declaracion import Declaracion, DeclaracionItem
from app.models.manifiesto import Manifiesto, ManifiestoItem
from app.models.planta_certificadora import PlantaCertificadora
from app.models.usuario import Usuario
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.declaracion import (
    DeclaracionCertificar,
    DeclaracionCreate,
    DeclaracionEstadoUpdate,
    DeclaracionOut,
    DeclaracionUpdate,
)
from app.services.estados import DECLARACION_TRANSICIONES, validar_transicion
from app.services.numbering import generar_numero
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/declaraciones", tags=["declaraciones"])

ROLES_ESCRITURA = ("superadmin", "operaciones")


@router.get("", response_model=APIResponse[PaginatedResponse[DeclaracionOut]])
def listar(
    page: int = 1,
    size: int = 20,
    estado: str | None = None,
    planta_id: int | None = None,
    manifiesto_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Declaracion).order_by(Declaracion.creado_en.desc())
    if estado:
        stmt = stmt.where(Declaracion.estado == estado)
    if planta_id:
        stmt = stmt.where(Declaracion.planta_id == planta_id)
    if manifiesto_id:
        stmt = stmt.where(Declaracion.manifiesto_id == manifiesto_id)
    items, total, pages = paginate(db, stmt, page, size)
    return APIResponse(
        data=PaginatedResponse(items=[DeclaracionOut.model_validate(i) for i in items], total=total, page=page, pages=pages)
    )


@router.post("", response_model=APIResponse[DeclaracionOut], status_code=201)
def crear(
    payload: DeclaracionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    manifiesto = db.get(Manifiesto, payload.manifiesto_id)
    if not manifiesto:
        raise HTTPException(status_code=404, detail="Manifiesto no encontrado")
    if not db.get(PlantaCertificadora, payload.planta_id):
        raise HTTPException(status_code=404, detail="Planta certificadora no encontrada")

    numero = generar_numero(db, Declaracion, "DEC")
    declaracion = Declaracion(
        numero=numero,
        manifiesto_id=payload.manifiesto_id,
        planta_id=payload.planta_id,
        fecha_envio=payload.fecha_envio,
        observaciones=payload.observaciones,
        creado_por=current_user.id,
    )
    db.add(declaracion)
    db.flush()

    if payload.items:
        for item in payload.items:
            db.add(DeclaracionItem(declaracion_id=declaracion.id, **item.model_dump()))
    else:
        # sin items explícitos: se heredan del manifiesto (cantidad real o, si no hay, la declarada)
        for mi in manifiesto.items:
            db.add(
                DeclaracionItem(
                    declaracion_id=declaracion.id,
                    manifiesto_item_id=mi.id,
                    tipo_residuo_id=mi.tipo_residuo_id,
                    cantidad=mi.cantidad_real or mi.cantidad_declarada,
                    unidad_medida=mi.unidad_medida,
                )
            )

    db.commit()
    db.refresh(declaracion)
    return APIResponse(data=DeclaracionOut.model_validate(declaracion), message="Declaración creada")


@router.get("/{declaracion_id}", response_model=APIResponse[DeclaracionOut])
def obtener(declaracion_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    declaracion = db.get(Declaracion, declaracion_id)
    if not declaracion:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")
    return APIResponse(data=DeclaracionOut.model_validate(declaracion))


@router.put("/{declaracion_id}", response_model=APIResponse[DeclaracionOut])
def actualizar(
    declaracion_id: int,
    payload: DeclaracionUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    declaracion = db.get(Declaracion, declaracion_id)
    if not declaracion:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(declaracion, field, value)
    db.commit()
    db.refresh(declaracion)
    return APIResponse(data=DeclaracionOut.model_validate(declaracion), message="Declaración actualizada")


@router.patch("/{declaracion_id}/estado", response_model=APIResponse[DeclaracionOut])
def cambiar_estado(
    declaracion_id: int,
    payload: DeclaracionEstadoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    declaracion = db.get(Declaracion, declaracion_id)
    if not declaracion:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")
    if not validar_transicion(DECLARACION_TRANSICIONES, declaracion.estado, payload.estado_nuevo):
        raise HTTPException(
            status_code=400,
            detail=f"Transición inválida: {declaracion.estado} → {payload.estado_nuevo}",
        )
    declaracion.estado = payload.estado_nuevo
    if payload.nota:
        declaracion.observaciones = f"{declaracion.observaciones or ''}\n{payload.nota}".strip()
    db.commit()
    db.refresh(declaracion)
    return APIResponse(data=DeclaracionOut.model_validate(declaracion), message="Estado actualizado")


@router.post("/{declaracion_id}/certificar", response_model=APIResponse[DeclaracionOut])
def certificar(
    declaracion_id: int,
    payload: DeclaracionCertificar,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    declaracion = db.get(Declaracion, declaracion_id)
    if not declaracion:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")
    if not validar_transicion(DECLARACION_TRANSICIONES, declaracion.estado, "certificada"):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede certificar una declaración en estado '{declaracion.estado}'",
        )
    declaracion.estado = "certificada"
    declaracion.numero_certificado = payload.numero_certificado
    declaracion.fecha_certificacion = payload.fecha_certificacion
    db.commit()
    db.refresh(declaracion)
    return APIResponse(data=DeclaracionOut.model_validate(declaracion), message="Declaración certificada")
