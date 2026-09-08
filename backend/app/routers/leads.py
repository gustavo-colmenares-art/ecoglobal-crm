from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.cliente import Cliente
from app.models.lead import Lead, LeadMensaje
from app.models.servicio import Servicio
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteOut
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.lead import (
    LeadAsignar,
    LeadConvertir,
    LeadDetalle,
    LeadEstadoUpdate,
    LeadMensajeEntrante,
    LeadOut,
)
from app.schemas.servicio import ServicioOut
from app.services.estados import LEAD_TRANSICIONES, validar_transicion
from app.services.numbering import generar_numero
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])

ROLES_LEADS = ("superadmin", "comercial")


def verificar_webhook_token(x_webhook_token: str = Header(default="")) -> None:
    if not settings.whatsapp_webhook_token or x_webhook_token != settings.whatsapp_webhook_token:
        raise HTTPException(status_code=401, detail="Token de webhook inválido")


@router.post("/whatsapp-webhook", response_model=APIResponse[LeadOut], status_code=201)
def recibir_mensaje_whatsapp(
    payload: LeadMensajeEntrante,
    db: Session = Depends(get_db),
    _: None = Depends(verificar_webhook_token),
):
    """Punto de entrada del puente de WhatsApp Web. Crea el lead si es un
    contacto nuevo, o le agrega el mensaje si ya existe uno abierto
    (no convertido ni marcado como no atendido)."""
    lead = db.scalar(
        select(Lead)
        .where(Lead.telefono == payload.telefono, Lead.estado.notin_(["convertido", "no_atendido"]))
        .order_by(Lead.creado_en.desc())
    )
    if not lead:
        lead = Lead(
            telefono=payload.telefono,
            nombre_contacto=payload.nombre_contacto,
            estado="nuevo",
        )
        db.add(lead)
        db.flush()
    elif payload.nombre_contacto and not lead.nombre_contacto:
        lead.nombre_contacto = payload.nombre_contacto

    db.add(LeadMensaje(lead_id=lead.id, direccion="entrante", texto=payload.texto))
    db.commit()
    db.refresh(lead)
    return APIResponse(data=LeadOut.model_validate(lead), message="Mensaje recibido")


@router.get("", response_model=APIResponse[PaginatedResponse[LeadOut]])
def listar(
    page: int = 1,
    size: int = 20,
    estado: str | None = None,
    canal: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Lead).order_by(Lead.creado_en.desc())
    if estado:
        stmt = stmt.where(Lead.estado == estado)
    if canal:
        stmt = stmt.where(Lead.canal == canal)

    items, total, pages = paginate(db, stmt, page, size)
    return APIResponse(
        data=PaginatedResponse(items=[LeadOut.model_validate(i) for i in items], total=total, page=page, pages=pages)
    )


@router.get("/{lead_id}", response_model=APIResponse[LeadDetalle])
def obtener(lead_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    cliente = db.get(Cliente, lead.cliente_id) if lead.cliente_id else None
    detalle = LeadDetalle(
        **LeadOut.model_validate(lead).model_dump(),
        cliente=ClienteOut.model_validate(cliente) if cliente else None,
        mensajes=list(lead.mensajes),
    )
    return APIResponse(data=detalle)


@router.patch("/{lead_id}/estado", response_model=APIResponse[LeadOut])
def cambiar_estado(
    lead_id: int,
    payload: LeadEstadoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_LEADS)),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    if not validar_transicion(LEAD_TRANSICIONES, lead.estado, payload.estado_nuevo):
        raise HTTPException(
            status_code=400,
            detail=f"Transición inválida: {lead.estado} → {payload.estado_nuevo}",
        )
    lead.estado = payload.estado_nuevo
    if payload.tipo_interes:
        lead.tipo_interes = payload.tipo_interes
    if payload.nota:
        lead.notas = ((lead.notas + "\n") if lead.notas else "") + payload.nota
    db.commit()
    db.refresh(lead)
    return APIResponse(data=LeadOut.model_validate(lead), message="Estado actualizado")


@router.patch("/{lead_id}/asignar", response_model=APIResponse[LeadOut])
def asignar(
    lead_id: int,
    payload: LeadAsignar,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_LEADS)),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    if not db.get(Usuario, payload.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    lead.asignado_a = payload.usuario_id
    db.commit()
    db.refresh(lead)
    return APIResponse(data=LeadOut.model_validate(lead), message="Lead asignado")


@router.post("/{lead_id}/convertir", response_model=APIResponse[ServicioOut], status_code=201)
def convertir(
    lead_id: int,
    payload: LeadConvertir,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_LEADS)),
):
    """Convierte un lead clasificado (cotizacion | servicio_directo) en
    Cliente (si no existe, por NIT) + Servicio en estado 'cotizado'."""
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    if lead.estado not in ("cotizacion", "servicio_directo"):
        raise HTTPException(
            status_code=400,
            detail="El lead debe estar clasificado como 'cotizacion' o 'servicio_directo' antes de convertirlo",
        )

    cliente = db.scalar(select(Cliente).where(Cliente.nit == payload.nit))
    if not cliente:
        cliente = Cliente(
            razon_social=payload.razon_social,
            nit=payload.nit,
            direccion=payload.direccion,
            ciudad=payload.ciudad,
            telefono=lead.telefono,
            email=payload.email,
            contacto_nombre=payload.contacto_nombre or lead.nombre_contacto,
            creado_por=current_user.id,
        )
        db.add(cliente)
        db.flush()

    servicio = Servicio(
        numero=generar_numero(db, Servicio, "SRV"),
        cliente_id=cliente.id,
        fecha_programada=payload.fecha_programada,
        descripcion=payload.descripcion or f"Lead WhatsApp — {lead.tipo_interes or 'sin clasificar'}",
        creado_por=current_user.id,
    )
    db.add(servicio)
    db.flush()

    lead.estado = "convertido"
    lead.cliente_id = cliente.id
    lead.servicio_id = servicio.id
    db.commit()
    db.refresh(servicio)
    return APIResponse(data=ServicioOut.model_validate(servicio), message="Lead convertido en servicio")
