from fastapi import FastAPI
from api.api import api_router


app = FastAPI(
    title="API de Gestão de Eventos Acadêmicos",
    description="Sistema para gerenciar eventos, usuários, inscrições e certificados integrado ao Cloud Firestore.",
    version="2.0.0"
)

# Registra todas as rotas da API v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"mensagem": "API funcionando! Acesse a rota /docs para visualizar o Swagger."}
