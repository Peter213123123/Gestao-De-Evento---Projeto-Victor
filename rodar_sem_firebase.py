"""Sobe a API com um Firestore FALSO em memória, para testar no Swagger sem acesso ao Firebase.

Uso (na pasta do projeto):   python rodar_sem_firebase.py
Depois abra:                 http://127.0.0.1:8000/docs

Os dados somem ao parar o servidor. Contas criadas (senha de todas: senha12345):
  admin@teste.com (admin)  |  org@teste.com (organizador)  |  aluno@teste.com (participante)
"""
import os
import sys
import types
from datetime import date, timedelta

os.environ.setdefault("SECRET_KEY", "chave-apenas-para-demonstracao")

from tests.fake_firestore import FakeFirestore  # noqa: E402

fake_db = FakeFirestore()
_modulo = types.ModuleType("core.database")
_modulo.db = fake_db
sys.modules["core.database"] = _modulo  # substitui o módulo que lê o firebase.json

from core.security import get_password_hash  # noqa: E402

hash_senha = get_password_hash("senha12345")
for nome, email, perfil in [
    ("Admin", "admin@teste.com", "admin"),
    ("Organizador", "org@teste.com", "organizador"),
    ("Participante", "aluno@teste.com", "participante"),
]:
    fake_db.collection("usuarios").add({"nome": nome, "email": email, "senha": hash_senha, "tipo_perfil": perfil})

fake_db.collection("eventos").add({
    "titulo": "Semana de Tecnologia",
    "descricao": "Evento de demonstração",
    "data_evento": (date.today() + timedelta(days=15)).isoformat(),
    "capacidade": 30,
    "status": "ativo",
})

import uvicorn  # noqa: E402
from main import app  # noqa: E402

if __name__ == "__main__":
    print("\nModo SEM Firebase (dados em memória). Swagger: http://127.0.0.1:8000/docs")
    print("Contas (senha senha12345): admin@teste.com | org@teste.com | aluno@teste.com\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
