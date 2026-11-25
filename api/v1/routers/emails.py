from fastapi import APIRouter, Depends, HTTPException, status

from core.permissoes import ADMIN, get_current_user
from core.database import db
from schemas.email_schema import EmailHistoricoResponse

EMAIL_ADMIN_HISTORICO = "admingest@gmail.com"

router = APIRouter()


def exigir_admin_principal(usuario: dict = Depends(get_current_user)) -> dict:
    """Restringe o histórico de e-mails exclusivamente ao admin admingest@gmail.com."""
    perfil = str(usuario.get("tipo_perfil", "")).lower()
    email = str(usuario.get("sub", "")).strip().lower()
    if perfil != ADMIN or email != EMAIL_ADMIN_HISTORICO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Histórico restrito ao administrador {EMAIL_ADMIN_HISTORICO}.",
        )
    return usuario


@router.get(
    "/",
    response_model=list[EmailHistoricoResponse],
    summary="Listar histórico de envios SMTP",
    description="Lista todos os e-mails disparados pela API (confirmações, certificados e recuperações de senha). Restrito a admingest@gmail.com.",
    responses={
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Acesso restrito a admingest@gmail.com"},
    },
)
def listar_historico_emails(usuario: dict = Depends(exigir_admin_principal)):
    docs = db.collection("emails_enviados").stream()
    itens = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    itens.sort(key=lambda item: item.get("enviado_em", ""), reverse=True)
    return itens
