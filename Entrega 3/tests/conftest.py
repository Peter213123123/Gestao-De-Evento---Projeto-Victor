"""Configuração do Pytest: roda a API inteira SEM Firebase.

1. Define as variáveis de ambiente de teste (antes de importar o app).
2. Troca o módulo core.database (que lê o firebase.json) por um Firestore falso em memória.
3. Cria fixtures: client, um usuário de cada perfil, eventos e inscrições de apoio.
"""
import itertools
import os
import sys
import types
from datetime import date, timedelta

# ---- 1) variáveis de ambiente de teste ------------------------------------
SECRET_KEY_TESTE = "chave-secreta-apenas-para-testes"
os.environ["SECRET_KEY"] = SECRET_KEY_TESTE
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

# ---- 2) Firestore falso no lugar de core.database --------------------------
from tests.fake_firestore import FakeFirestore  # noqa: E402

fake_db = FakeFirestore()
_modulo_falso = types.ModuleType("core.database")
_modulo_falso.db = fake_db
sys.modules["core.database"] = _modulo_falso

# ---- 3) agora é seguro importar o app --------------------------------------
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from core.security import create_access_token, get_password_hash  # noqa: E402
from main import app  # noqa: E402

SENHA_PADRAO = "senha12345"
_HASH_PADRAO = get_password_hash(SENHA_PADRAO)  # calculado uma vez (bcrypt é lento)
_sequencia = itertools.count(1)


@pytest.fixture(autouse=True)
def banco_limpo():
    """Cada teste começa com o banco vazio (um teste não depende do outro)."""
    fake_db.limpar()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def criar_usuario():
    """Fábrica: cria um usuário no banco falso e devolve o token pronto (como no login)."""
    def _criar(perfil, email=None, nome=None):
        email = email or f"{perfil}{next(_sequencia)}@teste.com"
        _, ref = fake_db.collection("usuarios").add({
            "nome": nome or perfil.capitalize(),
            "email": email,
            "senha": _HASH_PADRAO,
            "tipo_perfil": perfil,
        })
        token = create_access_token({"sub": email, "usuario_id": ref.id, "tipo_perfil": perfil})
        return {
            "id": ref.id,
            "email": email,
            "perfil": perfil,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"},
        }
    return _criar


@pytest.fixture
def admin(criar_usuario):
    return criar_usuario("admin")


@pytest.fixture
def organizador(criar_usuario):
    return criar_usuario("organizador")


@pytest.fixture
def participante(criar_usuario):
    return criar_usuario("participante")


@pytest.fixture
def outro_participante(criar_usuario):
    return criar_usuario("participante")


@pytest.fixture
def novo_evento():
    """Fábrica: grava um evento ativo (futuro) direto no banco falso e devolve o id."""
    def _criar(**campos):
        dados = {
            "titulo": "Semana de Tecnologia",
            "descricao": "Evento de teste",
            "data_evento": (date.today() + timedelta(days=10)).isoformat(),
            "capacidade": 10,
            "status": "ativo",
        }
        dados.update(campos)
        _, ref = fake_db.collection("eventos").add(dados)
        return ref.id
    return _criar


@pytest.fixture
def nova_inscricao():
    """Fábrica: grava uma inscrição direto no banco falso e devolve o id."""
    def _criar(id_usuario, id_evento, status="confirmada"):
        _, ref = fake_db.collection("inscricoes").add({
            "id_usuario": id_usuario,
            "id_evento": id_evento,
            "status": status,
            "data_inscricao": "2026-11-01T10:00:00+00:00",
        })
        return ref.id
    return _criar
