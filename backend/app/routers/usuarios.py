from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, require_roles
from app.models.usuario import Usuario
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])


@router.get("", response_model=APIResponse[PaginatedResponse[UsuarioOut]])
def listar(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    items, total, pages = paginate(db, select(Usuario), page, size)
    return APIResponse(
        data=PaginatedResponse(items=[UsuarioOut.model_validate(i) for i in items], total=total, page=page, pages=pages)
    )


@router.post("", response_model=APIResponse[UsuarioOut], status_code=status.HTTP_201_CREATED)
def crear(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    if db.scalar(select(Usuario).where(Usuario.email == payload.email)):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")
    usuario = Usuario(
        nombre=payload.nombre,
        email=payload.email,
        password_hash=hash_password(payload.password),
        rol_id=payload.rol_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return APIResponse(data=UsuarioOut.model_validate(usuario), message="Usuario creado")


@router.get("/{usuario_id}", response_model=APIResponse[UsuarioOut])
def obtener(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return APIResponse(data=UsuarioOut.model_validate(usuario))


@router.put("/{usuario_id}", response_model=APIResponse[UsuarioOut])
def actualizar(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    return APIResponse(data=UsuarioOut.model_validate(usuario), message="Usuario actualizado")


@router.delete("/{usuario_id}", response_model=APIResponse[None])
def desactivar(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = False
    db.commit()
    return APIResponse(message="Usuario desactivado")
