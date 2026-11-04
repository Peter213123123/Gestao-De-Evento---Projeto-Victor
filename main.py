from fastapi import FastAPI
from models import base
from api.api import api_router


app = FastAPI(
    title="API de Gestão de Eventos Acadêmicos",
    description="Sistema para gerenciar eventos, usuários e inscrições.",
    version="1.0.0"
)

# Registra todas as rotas que criamos no Passo 5
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"mensagem": "API funcionando! Acesse a rota /docs para visualizar o Swagger."}