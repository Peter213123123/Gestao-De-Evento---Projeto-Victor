from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import verificar_admin_organizador, verificar_admin, obter_usuario_atual
from core.database import db
from schemas.evento_schema import EventoCreate, EventoResponse

router = APIRouter()

@router.get("/", response_model=list[EventoResponse])
def listar_eventos(usuario: dict = Depends(obter_usuario_atual)):
    docs = db.collection("eventos").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(dados_evento: EventoCreate, usuario: dict = Depends(verificar_admin_organizador)):
    payload = dados_evento.model_dump()
    payload["data_evento"] = payload["data_evento"].isoformat()  # Converte date para string no Firestore
    payload["status"] = "ativo"
    novo_doc = db.collection("eventos").add(payload)
    return {"id": novo_doc[1].id, **payload}

@router.delete("/{evento_id}")
def excluir_evento(evento_id: str, usuario: dict = Depends(verificar_admin)):
    doc_ref = db.collection("eventos").document(evento_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    doc_ref.delete()
    return {"mensagem": "Evento excluído!"}
