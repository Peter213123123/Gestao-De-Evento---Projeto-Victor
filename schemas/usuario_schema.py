from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo_perfil: str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    tipo_perfil: str

    class Config:
        from_attributes = True