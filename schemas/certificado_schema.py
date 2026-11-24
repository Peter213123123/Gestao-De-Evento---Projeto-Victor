from pydantic import BaseModel, Field


class CertificadoCreate(BaseModel):
    id_usuario: str = Field(..., description="ID do participante com presença confirmada", examples=["usr_123"])
    id_evento: str = Field(..., description="ID do evento", examples=["evt_456"])
    carga_horaria: int = Field(..., gt=0, description="Carga horária em horas", examples=[10])


class CertificadoResponse(BaseModel):
    id: str = Field(..., description="Identificador único do certificado")
    id_usuario: str = Field(..., description="ID do usuário certificado")
    id_evento: str = Field(..., description="ID do evento")
    carga_horaria: int = Field(10, description="Carga horária do certificado")
    codigo_validacao: str = Field(..., description="Código alfanumérico de 8 caracteres para validação")
    emitido_em: str = Field(..., description="Data/hora de emissão em ISO 8601")
