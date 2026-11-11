"""Autenticação: login, JWT, 401 (sem token / inválido / expirado), 403 e /usuarios/me.

Usa as fixtures do tests/conftest.py: o app roda com um Firestore falso em memória,
então os usuários de teste são criados por `criar_usuario` (e não vêm de um banco real).
"""
from datetime import datetime, timedelta, timezone

import jwt

from tests.conftest import SECRET_KEY_TESTE, SENHA_PADRAO

LOGIN = "/api/v1/usuarios/login"
EVENTOS = "/api/v1/eventos/"
EVENTO = {"titulo": "Evento Teste", "descricao": "x", "data_evento": "2030-01-01", "capacidade": 100}


def test_login_sucesso(client, admin):
    response = client.post(LOGIN, data={"username": admin["email"], "password": SENHA_PADRAO})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_falha_senha_incorreta(client, admin):
    response = client.post(LOGIN, data={"username": admin["email"], "password": "senha_errada"})

    # O sistema deve rejeitar retornando 401
    assert response.status_code == 401


def test_acesso_sem_token_retorna_401(client):
    # Tentando acessar uma rota protegida (criar evento) sem enviar o token no cabeçalho
    response = client.post(EVENTOS, json=EVENTO)

    # Deve retornar erro de não autenticado
    assert response.status_code == 401


def test_participante_acessando_rota_proibida_retorna_403(client, participante):
    # 1. Login real, pela API, com um usuário de perfil "participante"
    login_response = client.post(LOGIN, data={"username": participante["email"], "password": SENHA_PADRAO})
    assert login_response.status_code == 200, "O login do participante falhou no teste."
    token = login_response.json()["access_token"]

    # 2. Com o token válido, tenta uma rota que só admin e organizador podem usar
    response = client.post(EVENTOS, json=EVENTO, headers={"Authorization": f"Bearer {token}"})

    # Autenticado, mas sem permissão: 403 (e não 401)
    assert response.status_code == 403


def test_login_retorna_jwt_com_expiracao(client, participante):
    resp = client.post(LOGIN, data={"username": participante["email"], "password": SENHA_PADRAO})
    corpo = resp.json()

    assert corpo["token_type"] == "bearer"
    dados = jwt.decode(corpo["access_token"], SECRET_KEY_TESTE, algorithms=["HS256"])
    assert dados["sub"] == participante["email"]
    assert dados["tipo_perfil"] == "participante"
    assert "exp" in dados


def test_login_com_email_inexistente_retorna_401(client):
    resp = client.post(LOGIN, data={"username": "ninguem@teste.com", "password": SENHA_PADRAO})
    assert resp.status_code == 401


def test_token_invalido_retorna_401(client):
    resp = client.get(EVENTOS, headers={"Authorization": "Bearer token-invalido"})
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
    resp = client.get(EVENTOS, headers={"Authorization": f"Bearer {expirado}"})
    assert resp.status_code == 401


def test_token_assinado_com_outra_chave_retorna_401(client, participante):
    falso = jwt.encode(
        {
            "sub": participante["email"],
            "usuario_id": participante["id"],
            "tipo_perfil": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        "outra-chave-qualquer-com-mais-de-32-caracteres",
        algorithm="HS256",
    )
    resp = client.get(EVENTOS, headers={"Authorization": f"Bearer {falso}"})
    assert resp.status_code == 401


def test_me_retorna_os_dados_do_usuario_autenticado(client, organizador):
    resp = client.get("/api/v1/usuarios/me", headers=organizador["headers"])

    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["email"] == organizador["email"]
    assert corpo["tipo_perfil"] == "organizador"
    assert "senha" not in corpo
