from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, status
from core.permissoes import permissao
from core.database import db
from schemas.certificado_schema import CertificadoCreate, CertificadoResponse

router = APIRouter()


@router.get(
    "/",
    response_model=list[CertificadoResponse],
    summary="Listar certificados",
    description="Lista os certificados emitidos. Disponível para todos os perfis autenticados.",
    responses={401: {"description": "Token ausente ou inválido"}},
)
def listar_certificados(usuario: dict = Depends(permissao("listar_certificados"))):
    docs = db.collection("certificados").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


@router.post(
    "/",
    response_model=CertificadoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Emitir certificado",
    description="Emite certificado para participante com presença confirmada ('presente') no evento. Restrito a Admin e Organizador.",
    responses={
        400: {"description": "Participante sem presença confirmada ou certificado já emitido"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Perfil sem permissão"},
        404: {"description": "Usuário ou evento não encontrado"},
    },
)
def criar_certificado(certificado: CertificadoCreate, usuario: dict = Depends(permissao("emitir_certificados"))):
    # 1. Verifica existência do usuário e do evento
    if not db.collection("usuarios").document(certificado.id_usuario).get().exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not db.collection("eventos").document(certificado.id_evento).get().exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # 2. Regra 10: exige inscrição com presença confirmada ("presente")
    inscricoes = db.collection("inscricoes").where("id_evento", "==", certificado.id_evento).stream()
    possui_presenca = any(
        doc.to_dict().get("id_usuario") == certificado.id_usuario
        and doc.to_dict().get("status") == "presente"
        for doc in inscricoes
    )
    if not possui_presenca:
        raise HTTPException(
            status_code=400,
            detail="Certificado só pode ser emitido para participantes com presença confirmada.",
        )

    # 3. Evita emissão duplicada para o mesmo usuário e evento
    existentes = db.collection("certificados").where("id_evento", "==", certificado.id_evento).stream()
    if any(doc.to_dict().get("id_usuario") == certificado.id_usuario for doc in existentes):
        raise HTTPException(
            status_code=400,
            detail="Certificado já emitido para este participante neste evento.",
        )

    dados = certificado.model_dump()
    dados["codigo_validacao"] = str(uuid.uuid4())[:8].upper()
    dados["emitido_em"] = datetime.now(timezone.utc).isoformat()
    novo_doc = db.collection("certificados").add(dados)
    return {"id": novo_doc[1].id, **dados}


@router.delete(
    "/{certificado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir certificado",
    description="Remove um certificado pelo ID. Restrito a Admin e Organizador.",
    responses={
        204: {"description": "Certificado excluído com sucesso"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Perfil sem permissão"},
        404: {"description": "Certificado não encontrado"},
    },
)
def excluir_certificado(certificado_id: str, usuario: dict = Depends(permissao("emitir_certificados"))):
    doc_ref = db.collection("certificados").document(certificado_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    doc_ref.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
