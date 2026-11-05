from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import verificar_admin_organizador, verificar_admin, get_current_user
from core.database import db
from schemas.evento_schema import EventoCreate, EventoUpdate, EventoResponse

router = APIRouter()

@router.get("/", response_model=list[EventoResponse])
def listar_eventos(usuario: dict = Depends(get_current_user)):
    docs = db.collection("eventos").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(dados_evento: EventoCreate, usuario: dict = Depends(verificar_admin_organizador)):
    if dados_evento.capacidade <= 0:
        raise HTTPException(status_code=400, detail="A capacidade do evento deve ser maior que zero")
    if dados_evento.data_evento < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido cadastrar um evento com data no passado")

    payload = dados_evento.model_dump()
    payload["data_evento"] = payload["data_evento"].isoformat()
    payload["status"] = "ativo"
    novo_doc = db.collection("eventos").add(payload)
    return {"id": novo_doc[1].id, **payload}

@router.put("/{evento_id}", response_model=EventoResponse)
def atualizar_evento(evento_id: str, dados_evento: EventoUpdate, usuario: dict = Depends(verificar_admin_organizador)):
    doc_ref = db.collection("eventos").document(evento_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    atualizacoes = {k: v for k, v in dados_evento.model_dump().items() if v is not None}
    if "capacidade" in atualizacoes and atualizacoes["capacidade"] <= 0:
        raise HTTPException(status_code=400, detail="A capacidade do evento deve ser maior que zero")
    if "data_evento" in atualizacoes:
        if atualizacoes["data_evento"] < date.today():
            raise HTTPException(status_code=400, detail="A data do evento não pode estar no passado")
        atualizacoes["data_evento"] = atualizacoes["data_evento"].isoformat()

    if atualizacoes:
        doc_ref.update(atualizacoes)

    dados_atualizados = doc_ref.get().to_dict()
    return {"id": evento_id, **dados_atualizados}

@router.delete("/{evento_id}")
def excluir_evento(evento_id: str, usuario: dict = Depends(verificar_admin)):
    doc_ref = db.collection("eventos").document(evento_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    doc_ref.delete()
    return {"mensagem": "Evento excluído!"}
