import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from api.api import api_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="API de Gestão de Eventos Acadêmicos",
    description="Sistema para gerenciar eventos, usuários, inscrições e certificados integrado ao Cloud Firestore.",
    version="2.0.0"
)

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

@app.get("/")
def root():
    """Redireciona a raiz diretamente para a tela de login."""
    return RedirectResponse(url="/login")

@app.get("/login")
def pagina_login():
    """Entrega a tela de login e cadastro."""
    return FileResponse(os.path.join(STATIC_DIR, "login.html"))

@app.get("/dashboard")
def pagina_dashboard():
    """Entrega o painel pós-autenticação."""
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))
