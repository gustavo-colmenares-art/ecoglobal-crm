from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.tipo_residuo import TipoResiduo
from app.models.usuario import Usuario
from app.schemas.common import APIResponse
from app.schemas.tipo_residuo import TipoResiduoCreate, TipoResiduoOut, TipoResiduoUpdate

router = APIRouter(prefix="/api/v1/residuos", tags=["residuos"])


@router.get("", response_model=APIResponse[list[TipoResiduoOut]])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    items = db.scalars(select(TipoResiduo).order_by(TipoResiduo.nombre)).all()
    return APIResponse(data=[TipoResiduoOut.model_validate(i) for i in items])


@router.post("", response_model=APIResponse[TipoResiduoOut], status_code=status.HTTP_201_CREATED)
def crear(
    payload: TipoResiduoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    if db.scalar(select(TipoResiduo).where(TipoResiduo.codigo == payload.codigo)):
        raise HTTPException(status_code=400, detail="Ya existe un tipo de residuo con ese código")
    tipo = TipoResiduo(**payload.model_dump())
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return APIResponse(data=TipoResiduoOut.model_validate(tipo), message="Tipo de residuo creado")


@router.put("/{residuo_id}", response_model=APIResponse[TipoResiduoOut])
def actualizar(
    residuo_id: int,
    payload: TipoResiduoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    tipo = db.get(TipoResiduo, residuo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de residuo no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tipo, field, value)
    db.commit()
    db.refresh(tipo)
    return APIResponse(data=TipoResiduoOut.model_validate(tipo), message="Tipo de residuo actualizado")
