from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.inscricao import Inscricao
from models.evento import Evento
from models.usuario import Usuario
from schemas.inscricao_schema import InscricaoCreate, InscricaoResponse

router = APIRouter()

@router.post("/", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
def criar_inscricao(inscricao: InscricaoCreate, db: Session = Depends(get_db)):
    evento = db.query(Evento).filter(Evento.id == inscricao.id_evento).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    
    usuario = db.query(Usuario).filter(Usuario.id == inscricao.id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    nova_inscricao = Inscricao(**inscricao.model_dump())
    db.add(nova_inscricao)
    db.commit()
    db.refresh(nova_inscricao)
    return nova_inscricao