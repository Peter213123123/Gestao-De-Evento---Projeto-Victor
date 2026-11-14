from pydantic import BaseModel

class CertificadoCreate(BaseModel):
    id_usuario: str
    id_evento: str
    carga_horaria: int

class CertificadoResponse(BaseModel):
    id: str
    id_usuario: str
    id_evento: str
    carga_horaria: int
    codigo_validacao: str
    emitido_em: str
