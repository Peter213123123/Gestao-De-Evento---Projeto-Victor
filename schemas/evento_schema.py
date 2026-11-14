from pydantic import BaseModel
from datetime import date
from typing import Optional

class EventoCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_evento: date
    capacidade: int

class EventoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    data_evento: Optional[date] = None
    capacidade: Optional[int] = None
    status: Optional[str] = None

class EventoResponse(BaseModel):
    id: str
    titulo: str
    descricao: Optional[str] = None
    data_evento: date
    capacidade: int
    status: str = "ativo"
