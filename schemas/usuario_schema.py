from pydantic import BaseModel


class UsuarioCriar(BaseModel):
    nome: str
    email: str
    senha: str
    tipo_perfil: str


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    tipo_perfil: str