from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.evento import Evento
from schemas.evento_schema import EventoCreate, EventoResponse

router = APIRouter()

@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    novo_evento = Evento(**evento.model_dump())
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)
    return novo_evento