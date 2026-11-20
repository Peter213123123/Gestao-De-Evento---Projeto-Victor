from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Response, status
from core.permissoes import permissao
from core.database import db
from schemas.evento_schema import EventoCreate, EventoUpdate, EventoResponse

router = APIRouter()


@router.get(
    "/",
    response_model=list[EventoResponse],
    summary="Listar eventos",
    description="Lista todos os eventos cadastrados. Disponível para todos os perfis autenticados.",
    responses={401: {"description": "Token ausente ou inválido"}},
)
def listar_eventos(usuario: dict = Depends(permissao("listar_eventos"))):
    docs = db.collection("eventos").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


@router.post(
    "/",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar evento",
    description="Cria um novo evento acadêmico com status inicial 'ativo'. Restrito a Admin e Organizador.",
    responses={
        400: {"description": "Capacidade <= 0 ou data do evento no passado"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Perfil sem permissão"},
    },
)
def criar_evento(dados_evento: EventoCreate, usuario: dict = Depends(permissao("criar_editar_eventos"))):
    if dados_evento.capacidade <= 0:
        raise HTTPException(status_code=400, detail="A capacidade do evento deve ser maior que zero")
    if dados_evento.data_evento < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido cadastrar um evento com data no passado")

    payload = dados_evento.model_dump()
    payload["data_evento"] = payload["data_evento"].isoformat()
    payload["status"] = "ativo"
    novo_doc = db.collection("eventos").add(payload)
    return {"id": novo_doc[1].id, **payload}


@router.put(
    "/{evento_id}",
    response_model=EventoResponse,
    summary="Atualizar evento",
    description="Atualiza dados de um evento existente. Restrito a Admin e Organizador.",
    responses={
        400: {"description": "Capacidade <= 0 ou data no passado"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Perfil sem permissão"},
        404: {"description": "Evento não encontrado"},
    },
)
def atualizar_evento(evento_id: str, dados_evento: EventoUpdate, usuario: dict = Depends(permissao("criar_editar_eventos"))):
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


@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir evento",
    description="Exclui um evento sem inscrições ativas vinculadas. Restrito a Admin.",
    responses={
        204: {"description": "Evento excluído com sucesso"},
        400: {"description": "Evento possui inscrições ativas vinculadas"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Acesso restrito a Admin"},
        404: {"description": "Evento não encontrado"},
    },
)
def excluir_evento(evento_id: str, usuario: dict = Depends(permissao("excluir_eventos"))):
    doc_ref = db.collection("eventos").document(evento_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    inscricoes = db.collection("inscricoes").where("id_evento", "==", evento_id).stream()
    if any(doc.to_dict().get("status") != "cancelada" for doc in inscricoes):
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir um evento com inscrições ativas vinculadas.",
        )

    doc_ref.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
