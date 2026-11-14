
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
import jwt

from core.config import settings


security = HTTPBearer(auto_error=False)


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credenciais is None:
        raise HTTPException(
            status_code=401,
            detail="Token não informado."
        )

    try:
        token = credenciais.credentials

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        return payload

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado."
        )


def verificar_admin_organizador(usuario: dict = Depends(obter_usuario_atual)):
    if usuario.get("tipo_perfil") not in ["admin", "organizador"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas Admin e Organizador."
        )
    return usuario


def verificar_admin(usuario: dict = Depends(obter_usuario_atual)):
    if usuario.get("tipo_perfil") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas Administradores."
        )
    return usuario

