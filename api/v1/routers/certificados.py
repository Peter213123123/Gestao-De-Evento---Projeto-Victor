from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import uuid
from core.permissoes import permissao
from core.database import db
from schemas.certificado_schema import CertificadoCreate, CertificadoResponse

router = APIRouter()

@router.get("/", response_model=list[CertificadoResponse])
def listar_certificados(usuario: dict = Depends(permissao("listar_certificados"))):
    docs = db.collection("certificados").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.post("/", response_model=CertificadoResponse, status_code=status.HTTP_201_CREATED)
def criar_certificado(certificado: CertificadoCreate, usuario: dict = Depends(permissao("emitir_certificados"))):
    dados = certificado.model_dump()
    dados["codigo_validacao"] = str(uuid.uuid4())[:8].upper()
    dados["emitido_em"] = datetime.now().isoformat()
    novo_doc = db.collection("certificados").add(dados)
    return {"id": novo_doc[1].id, **dados}

@router.delete("/{certificado_id}")
def excluir_certificado(certificado_id: str, usuario: dict = Depends(permissao("emitir_certificados"))):
    doc_ref = db.collection("certificados").document(certificado_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    doc_ref.delete()
    return {"mensagem": "Certificado excluído com sucesso!"}
