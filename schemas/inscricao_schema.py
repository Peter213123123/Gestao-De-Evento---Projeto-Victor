from pydantic import BaseModel

class InscricaoCreate(BaseModel):
    id_usuario: int
    id_evento: int

class InscricaoResponse(BaseModel):
    id: int
    id_usuario: int
    id_evento: int
    status: str

    class Config:
        from_attributes = True