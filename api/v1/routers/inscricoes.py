from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from core.database import db
from core.permissoes import exigir_permissao, permissao
from schemas.inscricao_schema import InscricaoCreate, InscricaoUpdate, InscricaoResponse

router = APIRouter()


def _exigir_dono(inscricao: dict, usuario: dict):
    """Participante só mexe nas próprias inscrições (403 se for de outra pessoa)."""
    if inscricao.get("id_usuario") != usuario.get("usuario_id"):
        raise HTTPException(status_code=403, detail="Você só pode alterar as suas próprias inscrições.")


@router.get("/", response_model=list[InscricaoResponse])
def listar_inscricoes(usuario: dict = Depends(permissao("listar_inscritos"))):
    docs = db.collection("inscricoes").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.post("/", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
def criar_inscricao(inscricao: InscricaoCreate, usuario: dict = Depends(permissao("inscrever_se"))):
    # O participante só se inscreve em seu próprio nome (o id vem do token, não do corpo)
    if inscricao.id_usuario != usuario.get("usuario_id"):
        raise HTTPException(status_code=403, detail="Você só pode realizar inscrições em seu próprio nome.")

    # 1. Verifica se o evento existe no Firestore
    evento_doc = db.collection("eventos").document(inscricao.id_evento).get()
    if not evento_doc.exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    evento_data = evento_doc.to_dict()

    # 2. Verifica se o usuário existe no Firestore
    usuario_doc = db.collection("usuarios").document(inscricao.id_usuario).get()
    if not usuario_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # 3. Verifica se o evento está ativo
    if evento_data.get("status", "ativo") != "ativo":
        raise HTTPException(status_code=400, detail="Inscrições só podem ser realizadas em eventos ativos")

    # 4. Verifica duplicidade e capacidade máxima do evento
    inscricoes_evento = db.collection("inscricoes").where("id_evento", "==", inscricao.id_evento).stream()
    total_ativas = 0
    for doc in inscricoes_evento:
        reg = doc.to_dict()
        if reg.get("status") != "cancelada":
            total_ativas += 1
            if reg.get("id_usuario") == inscricao.id_usuario:
                raise HTTPException(status_code=400, detail="O participante já está inscrito neste evento")

    capacidade = int(evento_data.get("capacidade", 0))
    if capacidade > 0 and total_ativas >= capacidade:
        raise HTTPException(status_code=400, detail="Não é possível realizar a inscrição. O evento atingiu sua capacidade máxima.")

    dados = inscricao.model_dump()
    dados["status"] = "confirmada"
    dados["data_inscricao"] = datetime.now(timezone.utc).isoformat()
    novo_doc = db.collection("inscricoes").add(dados)
    return {"id": novo_doc[1].id, **dados}

@router.put("/{inscricao_id}", response_model=InscricaoResponse)
def atualizar_inscricao(inscricao_id: str, dados_atualizacao: InscricaoUpdate, usuario: dict = Depends(get_current_user)):
    novo_status = dados_atualizacao.status

    # 1. Perfil: quem pode fazer cada tipo de alteração
    if novo_status == "cancelada":
        exigir_permissao(usuario, "cancelar_inscricao_propria")  # participante
    elif novo_status == "presente":
        exigir_permissao(usuario, "registrar_presenca")  # admin/organizador (check-in)
    else:
        raise HTTPException(status_code=400, detail="Status inválido. Use 'cancelada' ou 'presente'.")

    # 2. Existência
    doc_ref = db.collection("inscricoes").document(inscricao_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    # 3. Dono: cancelar só a própria inscrição
    if novo_status == "cancelada":
        _exigir_dono(doc.to_dict(), usuario)

    doc_ref.update({"status": novo_status})
    dados_atualizados = doc_ref.get().to_dict()
    return {"id": inscricao_id, **dados_atualizados}

@router.delete("/{inscricao_id}")
def excluir_inscricao(inscricao_id: str, usuario: dict = Depends(permissao("cancelar_inscricao_propria"))):
    doc_ref = db.collection("inscricoes").document(inscricao_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
    _exigir_dono(doc.to_dict(), usuario)
    doc_ref.delete()
    return {"mensagem": "Inscrição excluída com sucesso!"}
