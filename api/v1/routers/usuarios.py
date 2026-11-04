from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.usuario import Usuario
from schemas.usuario_schema import UsuarioCreate, UsuarioResponse

router = APIRouter()

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    
    # Exemplo simples. Em produção, a senha deve ser criptografada.
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=usuario.senha,
        tipo_perfil=usuario.tipo_perfil
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario