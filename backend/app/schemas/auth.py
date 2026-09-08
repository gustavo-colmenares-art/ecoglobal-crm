from pydantic import BaseModel, EmailStr

from app.schemas.usuario import UsuarioOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioOut


class ChangePasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str
