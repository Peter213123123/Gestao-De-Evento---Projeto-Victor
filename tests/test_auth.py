"""Autenticação: login, JWT, 401 (sem token / inválido / expirado) e /usuarios/me."""
from datetime import datetime, timedelta, timezone

import jwt

from tests.conftest import SECRET_KEY_TESTE, SENHA_PADRAO

LOGIN = "/api/v1/usuarios/login"
ROTA_PROTEGIDA = "/api/v1/eventos/"


def test_login_valido_retorna_jwt_com_expiracao(client, participante):
    resp = client.post(LOGIN, data={"username": participante["email"], "password": SENHA_PADRAO})
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["token_type"] == "bearer"
    dados = jwt.decode(corpo["access_token"], SECRET_KEY_TESTE, algorithms=["HS256"])
    assert dados["sub"] == participante["email"]
    assert dados["tipo_perfil"] == "participante"
    assert "exp" in dados


def test_login_com_senha_errada_retorna_401(client, participante):
    resp = client.post(LOGIN, data={"username": participante["email"], "password": "senha-errada"})
    assert resp.status_code == 401


def test_login_com_email_inexistente_retorna_401(client):
    resp = client.post(LOGIN, data={"username": "ninguem@teste.com", "password": SENHA_PADRAO})
    assert resp.status_code == 401


def test_rota_protegida_sem_token_retorna_401(client):
    assert client.get(ROTA_PROTEGIDA).status_code == 401


def test_token_invalido_retorna_401(client):
    resp = client.get(ROTA_PROTEGIDA, headers={"Authorization": "Bearer token-invalido"})
    assert resp.status_code == 401


def test_token_expirado_retorna_401(client, participante):
    expirado = jwt.encode(
        {
            "sub": participante["email"],
            "usuario_id": participante["id"],
            "tipo_perfil": "participante",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY_TESTE,
        algorithm="HS256",
    )
    resp = client.get(ROTA_PROTEGIDA, headers={"Authorization": f"Bearer {expirado}"})
    assert resp.status_code == 401


def test_token_assinado_com_outra_chave_retorna_401(client, participante):
    falso = jwt.encode(
        {
            "sub": participante["email"],
            "usuario_id": participante["id"],
            "tipo_perfil": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        "outra-chave-qualquer",
        algorithm="HS256",
    )
    resp = client.get(ROTA_PROTEGIDA, headers={"Authorization": f"Bearer {falso}"})
    assert resp.status_code == 401


def test_me_retorna_os_dados_do_usuario_autenticado(client, organizador):
    resp = client.get("/api/v1/usuarios/me", headers=organizador["headers"])
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["email"] == organizador["email"]
    assert corpo["tipo_perfil"] == "organizador"
    assert "senha" not in corpo
