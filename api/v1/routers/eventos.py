from fastapi import APIRouter, Depends
from core.auth import verificar_admin_organizador, verificar_admin, obter_usuario_atual

router = APIRouter()

# Qualquer utilizador logado pode listar
@router.get("/")
def listar_eventos(usuario: dict = Depends(obter_usuario_atual)):
    return {"mensagem": "Lista de eventos"}

# Apenas Admin e Organizador podem criar
@router.post("/")
def criar_evento(dados_evento: dict, usuario: dict = Depends(verificar_admin_organizador)):
    return {"mensagem": "Evento criado!"}

# Apenas Admin pode excluir
@router.delete("/{evento_id}")
def excluir_evento(evento_id: str, usuario: dict = Depends(verificar_admin)):
    return {"mensagem": "Evento excluído!"}
