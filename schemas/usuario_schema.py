<<<<<<< HEAD
from pydantic import BaseModel

class UsuarioCriar(BaseModel):
    nome: str
    email: str
    senha: str
    tipo_perfil: str
=======
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
>>>>>>> a74da1ea64f31085f4a655832efe774d7869f6ee
