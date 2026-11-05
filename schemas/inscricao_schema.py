from pydantic import BaseModel

class InscricaoCreate(BaseModel):
    id_usuario: str
    id_evento: str

class InscricaoResponse(BaseModel):
    id: str
    id_usuario: str
    id_evento: str
    status: str
