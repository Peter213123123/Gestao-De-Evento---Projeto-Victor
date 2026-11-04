from pydantic import BaseModel
from datetime import date
from typing import Optional

class EventoCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_evento: date
    capacidade: int

class EventoResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    data_evento: date
    capacidade: int

    class Config:
        from_attributes = True