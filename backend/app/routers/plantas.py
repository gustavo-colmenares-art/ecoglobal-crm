from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.planta_certificadora import PlantaCertificadora
from app.models.usuario import Usuario
from app.schemas.common import APIResponse
from app.schemas.planta_certificadora import PlantaCreate, PlantaOut, PlantaUpdate

router = APIRouter(prefix="/api/v1/plantas", tags=["plantas"])


@router.get("", response_model=APIResponse[list[PlantaOut]])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    items = db.scalars(select(PlantaCertificadora).order_by(PlantaCertificadora.nombre)).all()
    return APIResponse(data=[PlantaOut.model_validate(i) for i in items])


@router.post("", response_model=APIResponse[PlantaOut], status_code=status.HTTP_201_CREATED)
def crear(
    payload: PlantaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    planta = PlantaCertificadora(**payload.model_dump())
    db.add(planta)
    db.commit()
    db.refresh(planta)
    return APIResponse(data=PlantaOut.model_validate(planta), message="Planta creada")


@router.put("/{planta_id}", response_model=APIResponse[PlantaOut])
def actualizar(
    planta_id: int,
    payload: PlantaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("superadmin")),
):
    planta = db.get(PlantaCertificadora, planta_id)
    if not planta:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(planta, field, value)
    db.commit()
    db.refresh(planta)
    return APIResponse(data=PlantaOut.model_validate(planta), message="Planta actualizada")
