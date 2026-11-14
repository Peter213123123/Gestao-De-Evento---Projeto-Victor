
from fastapi import APIRouter, HTTPException
from schemas.usuario_schema import UsuarioCriar
from core.database import db
from core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/")
def criar_usuario(usuario: UsuarioCriar):
    senha_criptografada = get_password_hash(usuario.senha)

    dados_usuario = {
        "nome": usuario.nome,
        "email": usuario.email,
        "senha": senha_criptografada,
        "tipo_perfil": usuario.tipo_perfil
    }

    novo_doc = db.collection("usuarios").add(dados_usuario)

    return {
        "id": novo_doc[1].id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo_perfil": usuario.tipo_perfil
    }


@router.post("/login")
def login(dados: dict):
    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        raise HTTPException(
            status_code=400,
            detail="Informe o e-mail e a senha."
        )

    usuarios = db.collection("usuarios").where(
        "email", "==", email
    ).limit(1).stream()

    usuario_encontrado = None

    for documento in usuarios:
        usuario_encontrado = documento.to_dict()
        break

    if not usuario_encontrado:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos."
        )

    if not verify_password(senha, usuario_encontrado["senha"]):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos."
        )

    token = create_access_token({
        "sub": email,
        "tipo_perfil": usuario_encontrado["tipo_perfil"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

