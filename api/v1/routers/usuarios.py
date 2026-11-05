from fastapi import APIRouter, HTTPException, status
from schemas.usuario_schema import UsuarioCriar, UsuarioLogin, UsuarioResponse
from core.database import db
from core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
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

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios():
    docs = db.collection("usuarios").stream()
    lista = []
    for doc in docs:
        dados = doc.to_dict()
        dados.pop("senha", None)
        lista.append({"id": doc.id, **dados})
    return lista

@router.delete("/{usuario_id}")
def excluir_usuario(usuario_id: str):
    doc_ref = db.collection("usuarios").document(usuario_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    doc_ref.delete()
    return {"mensagem": "Usuário excluído com sucesso!"}

@router.post("/login")
def login(credenciais: UsuarioLogin):
    docs = db.collection("usuarios").where("email", "==", credenciais.email).limit(1).get()
    if not docs:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    
    doc = docs[0]
    usuario_db = doc.to_dict()
    if not verify_password(credenciais.senha, usuario_db.get("senha", "")):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    token = create_access_token({
        "sub": usuario_db["email"],
        "usuario_id": doc.id,
        "tipo_perfil": usuario_db.get("tipo_perfil")
    })
    return {"access_token": token, "token_type": "bearer"}
