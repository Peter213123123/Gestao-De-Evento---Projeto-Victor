from pydantic import BaseModel

class UsuarioCriar(BaseModel):
    nome: str
    email: str
    senha: str
    tipo_perfil: str  # "admin", "organizador" ou "participante"

class UsuarioLogin(BaseModel):
    email: str
    senha: str

class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    tipo_perfil: str
