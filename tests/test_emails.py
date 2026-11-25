"""Histórico de envios SMTP: acesso exclusivo ao admin admingest@gmail.com."""
from unittest.mock import MagicMock, patch
import pytest

from core.config import settings
from core.email_service import enviar_email

BASE = "/api/v1/emails/"


def test_historico_emails_sem_token_retorna_401(client):
    assert client.get(BASE).status_code == 401


@pytest.mark.parametrize("perfil", ["participante", "organizador", "admin"])
def test_outros_usuarios_e_outros_admins_recebem_403(client, request, perfil):
    usuario = request.getfixturevalue(perfil)
    assert client.get(BASE, headers=usuario["headers"]).status_code == 403


def test_admin_principal_lista_historico_e_registra_status(client, criar_usuario):
    admin_principal = criar_usuario("admin", email="admingest@gmail.com", nome="Administrador")

    # 1) SMTP não configurado -> registra "ignorado"
    with patch.object(settings, "SMTP_HOST", ""):
        ok_ignorado = enviar_email("aluno1@teste.com", "Assunto 1", "txt", "<p>txt</p>", tipo="confirmacao_inscricao")
        assert ok_ignorado is False

    # 2) SMTP configurado com sucesso -> registra "enviado"
    with (
        patch.object(settings, "SMTP_HOST", "smtp.gmail.com"),
        patch.object(settings, "SMTP_PORT", 587),
        patch.object(settings, "SMTP_USER", "pedrogamerr35@gmail.com"),
        patch.object(settings, "SMTP_PASSWORD", "app-pass"),
        patch.object(settings, "SMTP_FROM_EMAIL", "pedrogamerr35@gmail.com"),
        patch("core.email_service.smtplib.SMTP") as mock_smtp,
    ):
        server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = server
        ok_enviado = enviar_email("aluno2@teste.com", "Assunto 2", "txt", "<p>txt</p>", tipo="certificado")
        assert ok_enviado is True

    # 3) Falha SMTP -> registra "erro"
    with (
        patch.object(settings, "SMTP_HOST", "smtp.gmail.com"),
        patch.object(settings, "SMTP_PORT", 587),
        patch.object(settings, "SMTP_USER", "pedrogamerr35@gmail.com"),
        patch.object(settings, "SMTP_PASSWORD", "app-pass"),
        patch.object(settings, "SMTP_FROM_EMAIL", "pedrogamerr35@gmail.com"),
        patch("core.email_service.smtplib.SMTP", side_effect=RuntimeError("Falha de rede")),
    ):
        ok_erro = enviar_email("aluno3@teste.com", "Assunto 3", "txt", "<p>txt</p>", tipo="recuperacao_senha")
        assert ok_erro is False

    resp = client.get(BASE, headers=admin_principal["headers"])
    assert resp.status_code == 200
    dados = resp.json()
    assert len(dados) == 3
    # Ordenado do mais recente para o mais antigo
    assert dados[0]["status"] == "erro"
    assert "Falha de rede" in dados[0]["erro"]
    assert dados[1]["status"] == "enviado"
    assert dados[2]["status"] == "ignorado"
