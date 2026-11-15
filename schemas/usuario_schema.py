from typing import Literal
from pydantic import BaseModel

# Perfis aceitos pelo sistema (mesmos de core/permissoes.py)
Perfil = Literal["admin", "organizador", "participante"]


class UsuarioCriar(BaseModel):
    nome: str
    email: str
    senha: str
    # Sem tipo_perfil: o cadastro público sempre cria "participante".
    # Quem muda o perfil é o Admin, em PATCH /usuarios/{id}/perfil.


class UsuarioPerfilUpdate(BaseModel):
    tipo_perfil: Perfil


class UsuarioLogin(BaseModel):
    email: str
    senha: str


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    tipo_perfil: str
