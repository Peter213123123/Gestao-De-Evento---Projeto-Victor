from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field

StatusEvento = Literal["ativo", "concluido", "cancelado"]


class EventoCreate(BaseModel):
    titulo: str = Field(..., min_length=3, description="Título do evento acadêmico", examples=["Semana de Tecnologia"])
    descricao: Optional[str] = Field(None, description="Descrição detalhada do evento", examples=["Palestras e oficinas práticas"])
    data_evento: date = Field(..., description="Data de realização do evento (não pode estar no passado)")
    capacidade: int = Field(..., description="Capacidade máxima de participantes (> 0)", examples=[50])


class EventoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, description="Novo título do evento", examples=["Semana de Computação"])
    descricao: Optional[str] = Field(None, description="Nova descrição do evento")
    data_evento: Optional[date] = Field(None, description="Nova data do evento")
    capacidade: Optional[int] = Field(None, description="Nova capacidade máxima (> 0)")
    status: Optional[StatusEvento] = Field(None, description="Status do evento (ativo, concluido, cancelado)", examples=["ativo"])


class EventoResponse(BaseModel):
    id: str = Field(..., description="Identificador único do evento")
    titulo: str = Field(..., description="Título do evento")
    descricao: Optional[str] = Field(None, description="Descrição do evento")
    data_evento: date = Field(..., description="Data do evento")
    capacidade: int = Field(..., description="Capacidade máxima de inscritos")
    status: str = Field("ativo", description="Status atual do evento")
