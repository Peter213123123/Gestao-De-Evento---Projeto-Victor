from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from core.email_service import _smtp_configurado, enviar_email_certificado
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
def criar_certificado(
    certificado: CertificadoCreate,
    background_tasks: BackgroundTasks,
    usuario: dict = Depends(permissao("emitir_certificados")),
):
    # 1. Verifica existência do usuário e do evento
    usuario_doc = db.collection("usuarios").document(certificado.id_usuario).get()
    if not usuario_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    evento_doc = db.collection("eventos").document(certificado.id_evento).get()
    if not evento_doc.exists:
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

    usuario_data = usuario_doc.to_dict() or {}
    evento_data = evento_doc.to_dict() or {}
    background_tasks.add_task(
        enviar_email_certificado,
        email_destino=usuario_data.get("email", ""),
        nome_participante=usuario_data.get("nome", "Participante"),
        titulo_evento=evento_data.get("titulo", "Evento Acadêmico"),
        codigo_validacao=dados["codigo_validacao"],
        emitido_em=dados["emitido_em"],
    )

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


@router.post(
    "/{certificado_id}/reenviar",
    summary="Reenviar certificado por e-mail",
    description="Reenvia o certificado já emitido para o e-mail do participante. Restrito a Admin e Organizador.",
    responses={
        200: {"description": "Certificado reenviado com sucesso"},
        400: {"description": "SMTP não configurado ou participante sem e-mail"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Perfil sem permissão"},
        404: {"description": "Certificado ou usuário não encontrado"},
        500: {"description": "Falha ao enviar e-mail"},
    },
)
def reenviar_certificado(certificado_id: str, usuario: dict = Depends(permissao("emitir_certificados"))):
    cert_doc = db.collection("certificados").document(certificado_id).get()
    if not cert_doc.exists:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    cert_data = cert_doc.to_dict() or {}

    usuario_doc = db.collection("usuarios").document(cert_data.get("id_usuario", "")).get()
    if not usuario_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário do certificado não encontrado")
    usuario_data = usuario_doc.to_dict() or {}
    email_destino = (usuario_data.get("email") or "").strip()
    if not email_destino:
        raise HTTPException(status_code=400, detail="O participante não possui e-mail cadastrado.")

    if not _smtp_configurado():
        raise HTTPException(
            status_code=400,
            detail="Envio de e-mail não configurado. Defina SMTP_HOST, SMTP_USER, SMTP_PASSWORD e SMTP_FROM_EMAIL no .env.",
        )

    evento_id = cert_data.get("id_evento", "")
    evento_doc = db.collection("eventos").document(evento_id).get() if evento_id else None
    evento_data = evento_doc.to_dict() if (evento_doc and evento_doc.exists) else {}

    enviado = enviar_email_certificado(
        email_destino=email_destino,
        nome_participante=usuario_data.get("nome", "Participante"),
        titulo_evento=evento_data.get("titulo", "Evento Acadêmico"),
        codigo_validacao=cert_data.get("codigo_validacao", ""),
        emitido_em=cert_data.get("emitido_em", ""),
    )
    if not enviado:
        raise HTTPException(status_code=500, detail="Falha ao enviar e-mail. Verifique as credenciais SMTP.")

    return {"message": f"Certificado reenviado para {email_destino}!"}
