from fastapi import APIRouter
from api.v1.routers import usuarios, eventos, inscricoes, certificados

api_router = APIRouter()

api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(eventos.router, prefix="/eventos", tags=["Eventos"])
api_router.include_router(inscricoes.router, prefix="/inscricoes", tags=["Inscrições"])
api_router.include_router(certificados.router, prefix="/certificados", tags=["Certificados"])
