"""Certificados: só admin e organizador emitem/excluem/reenviam; exige presença confirmada; todos autenticados listam."""
from unittest.mock import patch
import pytest

from core.email_service import gerar_certificado_personalizado

BASE = "/api/v1/certificados/"


def test_certificados_sem_token_retorna_401(client):
    resp = client.get(BASE)
    assert resp.status_code == 401
    assert resp.json()["success"] is False


def test_participante_nao_emite_certificado(client, participante, novo_evento):
    dados = {"id_usuario": participante["id"], "id_evento": novo_evento(), "carga_horaria": 10}
    assert client.post(BASE, json=dados, headers=participante["headers"]).status_code == 403


@pytest.mark.parametrize("perfil", ["admin", "organizador"])
def test_admin_e_organizador_emitem_certificado(client, request, perfil, participante, novo_evento, nova_inscricao):
    evento_id = novo_evento()
    nova_inscricao(participante["id"], evento_id, status="presente")
    usuario = request.getfixturevalue(perfil)
    dados = {"id_usuario": participante["id"], "id_evento": evento_id, "carga_horaria": 10}
    resp = client.post(BASE, json=dados, headers=usuario["headers"])
    assert resp.status_code == 201
    assert len(resp.json()["codigo_validacao"]) == 8


def test_nao_emite_certificado_sem_presenca_confirmada(client, organizador, participante, novo_evento, nova_inscricao):
    evento_id = novo_evento()
    nova_inscricao(participante["id"], evento_id, status="confirmada")
    dados = {"id_usuario": participante["id"], "id_evento": evento_id, "carga_horaria": 10}
    resp = client.post(BASE, json=dados, headers=organizador["headers"])
    assert resp.status_code == 400
    assert resp.json()["success"] is False


def test_nao_emite_certificado_para_usuario_inexistente(client, organizador, novo_evento):
    dados = {"id_usuario": "naoexiste", "id_evento": novo_evento(), "carga_horaria": 10}
    assert client.post(BASE, json=dados, headers=organizador["headers"]).status_code == 404


def test_nao_emite_certificado_duplicado(client, organizador, participante, novo_evento, nova_inscricao):
    evento_id = novo_evento()
    nova_inscricao(participante["id"], evento_id, status="presente")
    dados = {"id_usuario": participante["id"], "id_evento": evento_id, "carga_horaria": 10}
    assert client.post(BASE, json=dados, headers=organizador["headers"]).status_code == 201
    assert client.post(BASE, json=dados, headers=organizador["headers"]).status_code == 400


def test_participante_nao_exclui_certificado(client, organizador, participante, novo_evento, nova_inscricao):
    evento_id = novo_evento()
    nova_inscricao(participante["id"], evento_id, status="presente")
    dados = {"id_usuario": participante["id"], "id_evento": evento_id, "carga_horaria": 10}
    certificado_id = client.post(BASE, json=dados, headers=organizador["headers"]).json()["id"]
    assert client.delete(f"{BASE}{certificado_id}", headers=participante["headers"]).status_code == 403
    assert client.delete(f"{BASE}{certificado_id}", headers=organizador["headers"]).status_code == 204


def test_participante_nao_reenvia_certificado(client, organizador, participante, novo_evento, nova_inscricao):
    evento_id = novo_evento()
    nova_inscricao(participante["id"], evento_id, status="presente")
    certificado_id = client.post(
        BASE,
        json={"id_usuario": participante["id"], "id_evento": evento_id, "carga_horaria": 10},
        headers=organizador["headers"],
    ).json()["id"]
    assert client.post(f"{BASE}{certificado_id}/reenviar", headers=participante["headers"]).status_code == 403


def test_reenviar_certificado_inexistente_retorna_404(client, admin):
    assert client.post(f"{BASE}naoexiste/reenviar", headers=admin["headers"]).status_code == 404


def test_admin_reenvia_certificado_com_smtp_mockado(client, admin, participante, novo_evento, nova_inscricao):
    evento_id = novo_evento()
    nova_inscricao(participante["id"], evento_id, status="presente")
    certificado_id = client.post(
        BASE,
        json={"id_usuario": participante["id"], "id_evento": evento_id, "carga_horaria": 10},
        headers=admin["headers"],
    ).json()["id"]

    with patch("api.v1.routers.certificados._smtp_configurado", return_value=True), patch(
        "api.v1.routers.certificados.enviar_email_certificado", return_value=True
    ) as mock_envio:
        resp = client.post(f"{BASE}{certificado_id}/reenviar", headers=admin["headers"])
        assert resp.status_code == 200
        assert participante["email"] in resp.json()["message"]
        mock_envio.assert_called_once()


def test_gerar_certificado_personalizado_retorna_jpg_e_pdf():
    resultado = gerar_certificado_personalizado("Maria Eduarda", "Semana Tech", "ABCD1234")
    assert resultado is not None
    jpg_bytes, pdf_bytes = resultado
    assert jpg_bytes[:2] == b"\xff\xd8"
    assert pdf_bytes[:4] == b"%PDF"
