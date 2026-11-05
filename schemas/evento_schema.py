from pydantic import BaseModel
from datetime import date
from typing import Optional

class EventoCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_evento: date
    capacidade: int

class EventoResponse(BaseModel):
    id: str
    titulo: str
    descricao: Optional[str] = None
    data_evento: date
    capacidade: int
    status: str = "ativo"
