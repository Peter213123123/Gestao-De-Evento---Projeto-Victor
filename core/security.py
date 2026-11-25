from datetime import datetime, timedelta, timezone
import uuid

import jwt
from passlib.context import CryptContext

from core.config import settings

# Configura o passlib para usar o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_RESET_EXPIRE_MINUTES = 15


def get_password_hash(password: str) -> str:
    """Recebe a senha informada no cadastro e retorna o hash criptografado."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara a senha digitada no login com o hash salvo no Firestore."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Gera um token JWT de sessão assinado com expiração configurada."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_password_reset_token(
    email: str,
    usuario_id: str,
    jti: str | None = None,
    expires_minutes: int = PASSWORD_RESET_EXPIRE_MINUTES,
) -> str:
    """Gera um token JWT de uso único específico para redefinição de senha."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": email,
        "usuario_id": usuario_id,
        "purpose": "password_reset",
        "jti": jti or str(uuid.uuid4()),
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> dict:
    """Valida o token de recuperação de senha e retorna seu payload."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("purpose") != "password_reset" or not payload.get("sub"):
        raise jwt.InvalidTokenError("Finalidade de token inválida.")
    return payload
