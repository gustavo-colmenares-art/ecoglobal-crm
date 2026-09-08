from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.cliente import Cliente
from app.models.servicio import Servicio
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.servicio import ServicioOut
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/clientes", tags=["clientes"])

ROLES_ESCRITURA = ("superadmin", "comercial")


@router.get("", response_model=APIResponse[PaginatedResponse[ClienteOut]])
def listar(
    page: int = 1,
    size: int = 20,
    nombre: str | None = None,
    nit: str | None = None,
    ciudad: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Cliente)
    if nombre:
        stmt = stmt.where(Cliente.razon_social.ilike(f"%{nombre}%"))
    if nit:
        stmt = stmt.where(Cliente.nit.ilike(f"%{nit}%"))
    if ciudad:
        stmt = stmt.where(Cliente.ciudad.ilike(f"%{ciudad}%"))
    items, total, pages = paginate(db, stmt, page, size)
    return APIResponse(
        data=PaginatedResponse(items=[ClienteOut.model_validate(i) for i in items], total=total, page=page, pages=pages)
    )


@router.post("", response_model=APIResponse[ClienteOut], status_code=status.HTTP_201_CREATED)
def crear(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    if db.scalar(select(Cliente).where(Cliente.nit == payload.nit)):
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese NIT")
    cliente = Cliente(**payload.model_dump(), creado_por=current_user.id)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return APIResponse(data=ClienteOut.model_validate(cliente), message="Cliente creado")


@router.get("/{cliente_id}", response_model=APIResponse[ClienteOut])
def obtener(cliente_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return APIResponse(data=ClienteOut.model_validate(cliente))


@router.put("/{cliente_id}", response_model=APIResponse[ClienteOut])
def actualizar(
    cliente_id: int,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*ROLES_ESCRITURA)),
):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return APIResponse(data=ClienteOut.model_validate(cliente), message="Cliente actualizado")


@router.get("/{cliente_id}/servicios", response_model=APIResponse[list[ServicioOut]])
def servicios_del_cliente(cliente_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    if not db.get(Cliente, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    servicios = db.scalars(
        select(Servicio).where(Servicio.cliente_id == cliente_id).order_by(Servicio.creado_en.desc())
    ).all()
    return APIResponse(data=[ServicioOut.model_validate(s) for s in servicios])
