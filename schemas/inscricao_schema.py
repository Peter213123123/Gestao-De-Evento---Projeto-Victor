from pydantic import BaseModel
from typing import Optional

class InscricaoCreate(BaseModel):
    id_usuario: str
    id_evento: str

class InscricaoUpdate(BaseModel):
    status: str  # "confirmada", "cancelada" ou "presente"

class InscricaoResponse(BaseModel):
    id: str
    id_usuario: str
    id_evento: str
    status: str
    data_inscricao: Optional[str] = None
