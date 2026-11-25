from typing import Literal
from pydantic import BaseModel, Field

# Perfis aceitos pelo sistema (mesmos de core/permissoes.py)
Perfil = Literal["admin", "organizador", "participante"]


class UsuarioCriar(BaseModel):
    nome: str = Field(..., min_length=2, description="Nome completo do usuário", examples=["João Silva"])
    email: str = Field(..., description="E-mail único do usuário", examples=["joao@email.com"])
    senha: str = Field(..., min_length=6, description="Senha de acesso (armazenada com hash bcrypt)", examples=["senhaforte123"])
    # Sem tipo_perfil: o cadastro público sempre cria "participante".
    # Quem muda o perfil é o Admin, em PATCH /usuarios/{id}/perfil.


class UsuarioPerfilUpdate(BaseModel):
    tipo_perfil: Perfil = Field(..., description="Novo perfil do usuário", examples=["organizador"])


class UsuarioLogin(BaseModel):
    email: str = Field(..., description="E-mail cadastrado", examples=["joao@email.com"])
    senha: str = Field(..., description="Senha cadastrada", examples=["senhaforte123"])


class UsuarioResponse(BaseModel):
    id: str = Field(..., description="Identificador único do usuário no Firestore")
    nome: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="E-mail do usuário")
    tipo_perfil: str = Field(..., description="Perfil de acesso (admin, organizador ou participante)")


class EsqueciSenhaRequest(BaseModel):
    email: str = Field(..., description="E-mail cadastrado para receber o link de redefinição", examples=["joao@email.com"])


class RedefinirSenhaRequest(BaseModel):
    token: str = Field(..., description="Token JWT enviado por e-mail")
    nova_senha: str = Field(..., min_length=6, description="Nova senha com no mínimo 6 caracteres", examples=["novasenha123"])
