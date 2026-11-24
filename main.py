import os
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from api.api import api_router
from core.exceptions import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

openapi_tags = [
    {"name": "Usuários", "description": "Cadastro público, login OAuth2/JWT, perfil próprio e administração de perfis."},
    {"name": "Eventos", "description": "Listagem, criação, edição e exclusão de eventos acadêmicos."},
    {"name": "Inscrições", "description": "Inscrição de participantes, listagem de inscritos, cancelamento e check-in."},
    {"name": "Certificados", "description": "Emissão, listagem e exclusão de certificados para participantes presentes."},
    {"name": "Infraestrutura", "description": "Endpoints de verificação de saúde da API."},
]

app = FastAPI(
    title="API de Gestão de Eventos Acadêmicos",
    description=(
        "Sistema REST para gerenciamento de eventos acadêmicos, usuários, inscrições e certificados, "
        "integrado ao Cloud Firestore.\n\n"
        "### Autenticação\n"
        "1. Cadastre um usuário em `POST /api/v1/usuarios/` ou use uma conta existente.\n"
        "2. Clique em **Authorize** e informe e-mail (`username`) e senha (`password`) para obter o token JWT."
    ),
    version="2.0.0",
    openapi_tags=openapi_tags,
)

# Padroniza respostas de erro
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra todas as rotas da API v1
app.include_router(api_router, prefix="/api/v1")

# Monta o diretório de arquivos estáticos
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health", tags=["Infraestrutura"], summary="Healthcheck da API")
def healthcheck():
    """Retorna o status operacional da aplicação."""
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    """Redireciona a raiz diretamente para a tela de login."""
    return RedirectResponse(url="/login")


@app.get("/login", include_in_schema=False)
def pagina_login():
    """Entrega a tela de login e cadastro."""
    return FileResponse(os.path.join(STATIC_DIR, "login.html"))


@app.get("/dashboard", include_in_schema=False)
def pagina_dashboard():
    """Entrega o painel pós-autenticação."""
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))
