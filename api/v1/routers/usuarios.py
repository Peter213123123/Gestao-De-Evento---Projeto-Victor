from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.usuario_schema import UsuarioCriar, UsuarioLogin, UsuarioPerfilUpdate, UsuarioResponse
from core.database import db
from core.security import get_password_hash, verify_password, create_access_token
from core.auth import get_current_user
from core.permissoes import ADMIN, PARTICIPANTE, permissao

router = APIRouter()

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCriar):
    # Verifica se o e-mail já está cadastrado no Firestore
    existente = db.collection("usuarios").where("email", "==", usuario.email).limit(1).get()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema")

    senha_criptografada = get_password_hash(usuario.senha)
    dados_usuario = {
        "nome": usuario.nome,
        "email": usuario.email,
        "senha": senha_criptografada,
        "tipo_perfil": PARTICIPANTE  # cadastro público nunca cria admin/organizador
    }
    novo_doc = db.collection("usuarios").add(dados_usuario)
    return {
        "id": novo_doc[1].id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo_perfil": PARTICIPANTE
    }

@router.get("/me", response_model=UsuarioResponse)
def obter_meu_perfil(current_user: dict = Depends(get_current_user)):
    """Rota obrigatória /usuarios/me que retorna os dados do próprio usuário autenticado."""
    usuario_id = current_user.get("usuario_id")
    if usuario_id:
        doc = db.collection("usuarios").document(usuario_id).get()
        if doc.exists:
            dados = doc.to_dict()
            return {
                "id": doc.id,
                "nome": dados.get("nome", ""),
                "email": dados.get("email", current_user.get("sub", "")),
                "tipo_perfil": dados.get("tipo_perfil", "participante")
            }

    email = current_user.get("sub")
    docs = db.collection("usuarios").where("email", "==", email).limit(1).get()
    if not docs:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    doc = docs[0]
    dados = doc.to_dict()
    return {
        "id": doc.id,
        "nome": dados.get("nome", ""),
        "email": dados.get("email", email),
        "tipo_perfil": dados.get("tipo_perfil", "participante")
    }

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(current_user: dict = Depends(permissao("gerenciar_usuarios"))):
    docs = db.collection("usuarios").stream()
    lista = []
    for doc in docs:
        dados = doc.to_dict()
        dados.pop("senha", None)
        lista.append({"id": doc.id, **dados})
    return lista

@router.delete("/{usuario_id}")
def excluir_usuario(usuario_id: str, current_user: dict = Depends(permissao("gerenciar_usuarios"))):
    doc_ref = db.collection("usuarios").document(usuario_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    doc_ref.delete()
    return {"mensagem": "Usuário excluído com sucesso!"}

@router.patch("/{usuario_id}/perfil", response_model=UsuarioResponse)
def alterar_perfil(
    usuario_id: str,
    dados: UsuarioPerfilUpdate,
    current_user: dict = Depends(permissao("gerenciar_usuarios")),
):
    """Somente Admin: promove ou rebaixa o perfil de um usuário (ex.: criar organizadores)."""
    if usuario_id == current_user.get("usuario_id") and dados.tipo_perfil != ADMIN:
        raise HTTPException(status_code=400, detail="Você não pode remover o seu próprio perfil de admin.")

    doc_ref = db.collection("usuarios").document(usuario_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    doc_ref.update({"tipo_perfil": dados.tipo_perfil})
    atual = doc.to_dict()
    return {
        "id": doc.id,
        "nome": atual.get("nome", ""),
        "email": atual.get("email", ""),
        "tipo_perfil": dados.tipo_perfil,
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint de Login usando OAuth2PasswordRequestForm (username recebe o email)."""
    docs = db.collection("usuarios").where("email", "==", form_data.username).limit(1).get()
    if not docs:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    doc = docs[0]
    usuario_db = doc.to_dict()
    if not verify_password(form_data.password, usuario_db.get("senha", "")):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    token = create_access_token({
        "sub": usuario_db["email"],
        "usuario_id": doc.id,
        "tipo_perfil": usuario_db.get("tipo_perfil")
    })
    return {"access_token": token, "token_type": "bearer"}
