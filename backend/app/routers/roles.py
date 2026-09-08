from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.common import APIResponse
from app.schemas.usuario import RolOut

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


@router.get("", response_model=APIResponse[list[RolOut]])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    roles = db.scalars(select(Rol).order_by(Rol.nombre)).all()
    return APIResponse(data=[RolOut.model_validate(r) for r in roles])
