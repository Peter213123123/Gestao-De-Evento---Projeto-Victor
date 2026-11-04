from fastapi import HTTPException, Header, Depends
import jwt
from core.config import settings

# Extrai o perfil do token enviado no cabeçalho
def obter_usuario_atual(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload # Retorna os dados do utilizador, incluindo o 'tipo_perfil'
    except:
        raise HTTPException(status_code=401, detail="Token inválido ou ausente")

# Bloqueia se não for Admin ou Organizador
def verificar_admin_organizador(usuario: dict = Depends(obter_usuario_atual)):
    if usuario.get("tipo_perfil") not in ["admin", "organizador"]:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas Admin e Organizador.")
    return usuario

# Bloqueia se não for Admin
def verificar_admin(usuario: dict = Depends(obter_usuario_atual)):
    if usuario.get("tipo_perfil") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas Administradores.")
    return usuario
