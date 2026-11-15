"""Certificados: só admin e organizador emitem/excluem; todos autenticados listam."""
import pytest

BASE = "/api/v1/certificados/"
DADOS = {"id_usuario": "u1", "id_evento": "e1", "carga_horaria": 10}


def test_certificados_sem_token_retorna_401(client):
    assert client.get(BASE).status_code == 401


def test_participante_nao_emite_certificado(client, participante):
    assert client.post(BASE, json=DADOS, headers=participante["headers"]).status_code == 403


@pytest.mark.parametrize("perfil", ["admin", "organizador"])
def test_admin_e_organizador_emitem_certificado(client, request, perfil):
    usuario = request.getfixturevalue(perfil)
    resp = client.post(BASE, json=DADOS, headers=usuario["headers"])
    assert resp.status_code == 201
    assert len(resp.json()["codigo_validacao"]) == 8


def test_participante_nao_exclui_certificado(client, organizador, participante):
    certificado_id = client.post(BASE, json=DADOS, headers=organizador["headers"]).json()["id"]
    assert client.delete(f"{BASE}{certificado_id}", headers=participante["headers"]).status_code == 403
    assert client.delete(f"{BASE}{certificado_id}", headers=organizador["headers"]).status_code == 200
