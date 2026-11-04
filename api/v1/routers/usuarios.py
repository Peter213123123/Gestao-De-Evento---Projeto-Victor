from fastapi import APIRouter
from schemas.usuario_schema import UsuarioCriar
from core.database import db 
from core.security import get_password_hash

# Cria a variável router que estava faltando!
router = APIRouter()

@router.post("/")
def criar_usuario(usuario: UsuarioCriar):
    # 1. Criptografar a senha
    senha_criptografada = get_password_hash(usuario.senha)
    
    # 2. Preparar os dados como dicionário
    dados_usuario = {
        "nome": usuario.nome,
        "email": usuario.email,
        "senha": senha_criptografada,
        "tipo_perfil": usuario.tipo_perfil
    }
    
    # 3. Guardar no Firebase!
    novo_doc = db.collection("usuarios").add(dados_usuario)
    
    return {
        "id": novo_doc[1].id, # Isto vai devolver o ID alfanumérico do Firebase
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo_perfil": usuario.tipo_perfil
    }
