from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.usuario import Usuario
from app.schemas.auth import ChangePasswordRequest, LoginRequest, TokenResponse
from app.schemas.common import APIResponse
from app.schemas.usuario import UsuarioOut

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")

    user.ultimo_acceso = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return APIResponse(data=TokenResponse(access_token=token, user=UsuarioOut.model_validate(user)))


@router.post("/logout", response_model=APIResponse[None])
def logout(current_user: Usuario = Depends(get_current_user)):
    return APIResponse(message="Sesión cerrada")


@router.get("/me", response_model=APIResponse[UsuarioOut])
def me(current_user: Usuario = Depends(get_current_user)):
    return APIResponse(data=UsuarioOut.model_validate(current_user))


@router.put("/change-password", response_model=APIResponse[None])
def change_password(
    payload: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.password_actual, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no es correcta",
        )
    current_user.password_hash = hash_password(payload.password_nueva)
    db.commit()
    return APIResponse(message="Contraseña actualizada")
