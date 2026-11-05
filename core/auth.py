from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from core.config import settings

# Instancia o OAuth2PasswordBearer para habilitar o botão "Authorize" no Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/usuarios/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Captura o token do cabeçalho, decodifica e valida a expiração."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Alias para manter compatibilidade com importações existentes
obter_usuario_atual = get_current_user

# Bloqueia se não for Admin ou Organizador
def verificar_admin_organizador(usuario: dict = Depends(get_current_user)):
    if str(usuario.get("tipo_perfil", "")).lower() not in ["admin", "organizador"]:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas Admin e Organizador.")
    return usuario

# Bloqueia se não for Admin
def verificar_admin(usuario: dict = Depends(get_current_user)):
    if str(usuario.get("tipo_perfil", "")).lower() != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas Administradores.")
    return usuario
