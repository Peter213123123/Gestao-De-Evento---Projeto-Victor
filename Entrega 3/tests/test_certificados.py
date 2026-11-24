"""Certificados: só admin e organizador emitem/excluem; exige presença confirmada; todos autenticados listam."""
import pytest

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
