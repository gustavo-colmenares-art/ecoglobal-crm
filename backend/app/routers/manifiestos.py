from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.cliente import Cliente
from app.models.manifiesto import Manifiesto, ManifiestoHistorial, ManifiestoItem
from app.models.servicio import Servicio
from app.models.tipo_residuo import TipoResiduo
from app.models.usuario import Usuario
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.manifiesto import (
    ManifiestoCreate,
    ManifiestoEstadoUpdate,
    ManifiestoHistorialOut,
    ManifiestoItemCreate,
    ManifiestoItemOut,
    ManifiestoItemUpdate,
    ManifiestoOut,
    ManifiestoUpdate,
)
from app.services.estados import MANIFIESTO_TRANSICIONES, validar_transicion
from app.services.numbering import generar_numero
from app.utils.pagination import paginate
from app.utils.pdf import generar_pdf_manifiesto

router = APIRouter(prefix="/api/v1/manifiestos", tags=["manifiestos"])

ROLES_ESCRITURA = ("superadmin", "operaciones")


@router.get("", response_model=APIResponse[PaginatedResponse[ManifiestoOut]])
def listar(
    page: int = 1,
    size: int = 20,
    estado: str | None = None,
    operario_id: int | None = None,
    fecha: date | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Manifiesto).order_by(Manifiesto.creado_en.desc())
    if estado:
        stmt = stmt.where(Manifiesto.estado == estado)
    if operario_id:
        stmt = stmt.where(Manifiesto.operario_id == operario_id)
    if fecha:
        stmt = stmt.where(Manifiesto.fecha_recoleccion == fecha)
    items, total, pages = paginate(db, stmt, page, size)
    return APIResponse(
        data=PaginatedResponse(items=[ManifiestoOut.model_validate(i) for i in items], total=total, page=page, pages=pages)
    )


@router.post("", response_model=APIResponse[ManifiestoOut], status_code=201)
def crear(
    payload: ManifiestoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    if not db.get(Servicio, payload.servicio_id):
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    numero = generar_numero(db, Manifiesto, "MAN")
    manifiesto = Manifiesto(
        numero=numero,
        servicio_id=payload.servicio_id,
        operario_id=payload.operario_id,
        fecha_recoleccion=payload.fecha_recoleccion,
        observaciones_campo=payload.observaciones_campo,
        creado_por=current_user.id,
    )
    db.add(manifiesto)
    db.flush()
    for item in payload.items:
        db.add(ManifiestoItem(manifiesto_id=manifiesto.id, **item.model_dump()))
    db.commit()
    db.refresh(manifiesto)
    return APIResponse(data=ManifiestoOut.model_validate(manifiesto), message="Manifiesto generado")


@router.get("/{manifiesto_id}", response_model=APIResponse[ManifiestoOut])
def obtener(manifiesto_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    manifiesto = db.get(Manifiesto, manifiesto_id)
    if not manifiesto:
        raise HTTPException(status_code=404, detail="Manifiesto no encontrado")
    return APIResponse(data=ManifiestoOut.model_validate(manifiesto))


@router.put("/{manifiesto_id}", response_model=APIResponse[ManifiestoOut])
def actualizar(
    manifiesto_id: int,
    payload: ManifiestoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    manifiesto = db.get(Manifiesto, manifiesto_id)
    if not manifiesto:
        raise HTTPException(status_code=404, detail="Manifiesto no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(manifiesto, field, value)
    db.commit()
    db.refresh(manifiesto)
    return APIResponse(data=ManifiestoOut.model_validate(manifiesto), message="Manifiesto actualizado")


@router.patch("/{manifiesto_id}/estado", response_model=APIResponse[ManifiestoOut])
def cambiar_estado(
    manifiesto_id: int,
    payload: ManifiestoEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    manifiesto = db.get(Manifiesto, manifiesto_id)
    if not manifiesto:
        raise HTTPException(status_code=404, detail="Manifiesto no encontrado")
    if not validar_transicion(MANIFIESTO_TRANSICIONES, manifiesto.estado, payload.estado_nuevo):
        raise HTTPException(
            status_code=400,
            detail=f"Transición inválida: {manifiesto.estado} → {payload.estado_nuevo}",
        )
    estado_antes = manifiesto.estado
    manifiesto.estado = payload.estado_nuevo
    db.add(
        ManifiestoHistorial(
            manifiesto_id=manifiesto.id,
            estado_antes=estado_antes,
            estado_nuevo=payload.estado_nuevo,
            cambiado_por=current_user.id,
            nota=payload.nota,
        )
    )
    db.commit()
    db.refresh(manifiesto)
    return APIResponse(data=ManifiestoOut.model_validate(manifiesto), message="Estado actualizado")


@router.post("/{manifiesto_id}/items", response_model=APIResponse[ManifiestoItemOut], status_code=201)
def agregar_item(
    manifiesto_id: int,
    payload: ManifiestoItemCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    if not db.get(Manifiesto, manifiesto_id):
        raise HTTPException(status_code=404, detail="Manifiesto no encontrado")
    if not db.get(TipoResiduo, payload.tipo_residuo_id):
        raise HTTPException(status_code=404, detail="Tipo de residuo no encontrado")
    item = ManifiestoItem(manifiesto_id=manifiesto_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return APIResponse(data=ManifiestoItemOut.model_validate(item), message="Residuo agregado")


@router.put("/{manifiesto_id}/items/{item_id}", response_model=APIResponse[ManifiestoItemOut])
def actualizar_item(
    manifiesto_id: int,
    item_id: int,
    payload: ManifiestoItemUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    item = db.get(ManifiestoItem, item_id)
    if not item or item.manifiesto_id != manifiesto_id:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return APIResponse(data=ManifiestoItemOut.model_validate(item), message="Cantidad actualizada")


@router.get("/{manifiesto_id}/historial", response_model=APIResponse[list[ManifiestoHistorialOut]])
def historial(manifiesto_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    if not db.get(Manifiesto, manifiesto_id):
        raise HTTPException(status_code=404, detail="Manifiesto no encontrado")
    registros = db.scalars(
        select(ManifiestoHistorial)
        .where(ManifiestoHistorial.manifiesto_id == manifiesto_id)
        .order_by(ManifiestoHistorial.cambiado_en)
    ).all()
    return APIResponse(data=[ManifiestoHistorialOut.model_validate(r) for r in registros])


@router.get("/{manifiesto_id}/pdf")
def pdf(manifiesto_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    manifiesto = db.get(Manifiesto, manifiesto_id)
    if not manifiesto:
        raise HTTPException(status_code=404, detail="Manifiesto no encontrado")
    servicio = db.get(Servicio, manifiesto.servicio_id)
    cliente = db.get(Cliente, servicio.cliente_id)
    operario = db.get(Usuario, manifiesto.operario_id) if manifiesto.operario_id else None

    items_data = []
    for item in manifiesto.items:
        tipo = db.get(TipoResiduo, item.tipo_residuo_id)
        items_data.append(
            {
                "codigo": tipo.codigo,
                "nombre": tipo.nombre,
                "cantidad_declarada": item.cantidad_declarada,
                "cantidad_real": item.cantidad_real,
                "unidad_medida": item.unidad_medida,
            }
        )

    pdf_bytes = generar_pdf_manifiesto(
        {
            "numero": manifiesto.numero,
            "fecha_generacion": manifiesto.fecha_generacion,
            "servicio_numero": servicio.numero,
            "cliente": {
                "razon_social": cliente.razon_social,
                "nit": cliente.nit,
                "direccion": cliente.direccion,
                "ciudad": cliente.ciudad,
                "contacto_nombre": cliente.contacto_nombre,
            },
            "operario_nombre": operario.nombre if operario else None,
            "items": items_data,
            "nombre_receptor": manifiesto.nombre_receptor,
            "cargo_receptor": manifiesto.cargo_receptor,
        }
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{manifiesto.numero}.pdf"'},
    )
