from typing import Optional
from pydantic import BaseModel, Field


class EmailHistoricoResponse(BaseModel):
    id: str = Field(..., description="Identificador único do registro de envio")
    destinatario: str = Field(..., description="E-mail do destinatário")
    assunto: str = Field(..., description="Assunto do e-mail")
    tipo: str = Field(..., description="Categoria do envio (confirmacao_inscricao, certificado, recuperacao_senha, geral)")
    status: str = Field(..., description="Status do envio (enviado, erro, ignorado)")
    erro: Optional[str] = Field(None, description="Detalhes de falha, caso ocorra")
    enviado_em: str = Field(..., description="Data e hora do registro em ISO 8601")
