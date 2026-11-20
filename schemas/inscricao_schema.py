from typing import Optional
from pydantic import BaseModel, Field


class InscricaoCreate(BaseModel):
    id_usuario: str = Field(..., description="ID do participante autenticado", examples=["usr_123"])
    id_evento: str = Field(..., description="ID do evento ativo", examples=["evt_456"])


class InscricaoUpdate(BaseModel):
    status: str = Field(..., description="Novo status da inscrição ('cancelada' ou 'presente')", examples=["presente"])


class InscricaoResponse(BaseModel):
    id: str = Field(..., description="Identificador único da inscrição")
    id_usuario: str = Field(..., description="ID do usuário inscrito")
    id_evento: str = Field(..., description="ID do evento")
    status: str = Field(..., description="Status da inscrição (confirmada, cancelada ou presente)")
    data_inscricao: Optional[str] = Field(None, description="Data e hora da inscrição em ISO 8601")
