from fastapi import APIRouter

router = APIRouter()

# As linhas abaixo ficam comentadas até a equipa refazer a lógica para o Firebase
# from fastapi import Depends, status
# from sqlalchemy.orm import Session
# from core.database import db
# from models.inscricao import Inscricao
# from schemas.inscricao_schema import InscricaoCreate, InscricaoResponse

# @router.post("/", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
# def criar_inscricao(inscricao: InscricaoCreate, db: Session = Depends(get_db)):
#     nova_inscricao = Inscricao(**inscricao.model_dump())
#     db.add(nova_inscricao)
#     db.commit()
#     db.refresh(nova_inscricao)
#     return nova_inscricao
