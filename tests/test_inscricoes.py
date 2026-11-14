"""Inscrições: quem pode se inscrever, listar inscritos, cancelar (só a própria) e check-in."""
import pytest

from tests.conftest import fake_db

BASE = "/api/v1/inscricoes/"


def corpo(usuario, evento_id):
    return {"id_usuario": usuario["id"], "id_evento": evento_id}


def status_no_banco(inscricao_id):
    return fake_db.collection("inscricoes").document(inscricao_id).get().to_dict()["status"]


# ---------- inscrever-se ----------
def test_participante_se_inscreve(client, participante, novo_evento):
    evento_id = novo_evento()
    resp = client.post(BASE, json=corpo(participante, evento_id), headers=participante["headers"])
    assert resp.status_code == 201
    assert resp.json()["status"] == "confirmada"


def test_inscricao_sem_token_retorna_401(client, participante, novo_evento):
    assert client.post(BASE, json=corpo(participante, novo_evento())).status_code == 401


@pytest.mark.parametrize("perfil", ["admin", "organizador"])
def test_admin_e_organizador_nao_se_inscrevem(client, request, perfil, novo_evento):
    usuario = request.getfixturevalue(perfil)
    resp = client.post(BASE, json=corpo(usuario, novo_evento()), headers=usuario["headers"])
    assert resp.status_code == 403


def test_participante_nao_inscreve_outra_pessoa(client, participante, outro_participante, novo_evento):
    resp = client.post(BASE, json=corpo(outro_participante, novo_evento()), headers=participante["headers"])
    assert resp.status_code == 403


def test_inscricao_duplicada_retorna_400(client, participante, novo_evento, nova_inscricao):
    evento_id = novo_evento()
    nova_inscricao(participante["id"], evento_id)
    resp = client.post(BASE, json=corpo(participante, evento_id), headers=participante["headers"])
    assert resp.status_code == 400


def test_evento_lotado_retorna_400(client, participante, outro_participante, novo_evento, nova_inscricao):
    evento_id = novo_evento(capacidade=1)
    nova_inscricao(outro_participante["id"], evento_id)
    resp = client.post(BASE, json=corpo(participante, evento_id), headers=participante["headers"])
    assert resp.status_code == 400


def test_evento_inexistente_retorna_404(client, participante):
    resp = client.post(BASE, json=corpo(participante, "naoexiste"), headers=participante["headers"])
    assert resp.status_code == 404


def test_evento_nao_ativo_retorna_400(client, participante, novo_evento):
    evento_id = novo_evento(status="cancelado")
    resp = client.post(BASE, json=corpo(participante, evento_id), headers=participante["headers"])
    assert resp.status_code == 400


# ---------- listar inscritos ----------
def test_participante_nao_lista_inscritos(client, participante):
    assert client.get(BASE, headers=participante["headers"]).status_code == 403


@pytest.mark.parametrize("perfil", ["admin", "organizador"])
def test_admin_e_organizador_listam_inscritos(client, request, perfil, participante, novo_evento, nova_inscricao):
    nova_inscricao(participante["id"], novo_evento())
    usuario = request.getfixturevalue(perfil)
    resp = client.get(BASE, headers=usuario["headers"])
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ---------- cancelar (só a própria) ----------
def test_participante_cancela_a_propria_inscricao(client, participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(participante["id"], novo_evento())
    resp = client.put(f"{BASE}{inscricao_id}", json={"status": "cancelada"}, headers=participante["headers"])
    assert resp.status_code == 200
    assert status_no_banco(inscricao_id) == "cancelada"


def test_participante_nao_cancela_inscricao_de_outro(client, participante, outro_participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(outro_participante["id"], novo_evento())
    resp = client.put(f"{BASE}{inscricao_id}", json={"status": "cancelada"}, headers=participante["headers"])
    assert resp.status_code == 403
    assert status_no_banco(inscricao_id) == "confirmada"


@pytest.mark.parametrize("perfil", ["admin", "organizador"])
def test_admin_e_organizador_nao_cancelam_inscricao(client, request, perfil, participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(participante["id"], novo_evento())
    usuario = request.getfixturevalue(perfil)
    resp = client.put(f"{BASE}{inscricao_id}", json={"status": "cancelada"}, headers=usuario["headers"])
    assert resp.status_code == 403


def test_participante_nao_exclui_inscricao_de_outro(client, participante, outro_participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(outro_participante["id"], novo_evento())
    assert client.delete(f"{BASE}{inscricao_id}", headers=participante["headers"]).status_code == 403
    assert fake_db.collection("inscricoes").document(inscricao_id).get().exists


def test_participante_exclui_a_propria_inscricao(client, participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(participante["id"], novo_evento())
    assert client.delete(f"{BASE}{inscricao_id}", headers=participante["headers"]).status_code == 200
    assert not fake_db.collection("inscricoes").document(inscricao_id).get().exists


# ---------- check-in (presente) ----------
def test_participante_nao_marca_presenca(client, participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(participante["id"], novo_evento())
    resp = client.put(f"{BASE}{inscricao_id}", json={"status": "presente"}, headers=participante["headers"])
    assert resp.status_code == 403


def test_organizador_marca_presenca(client, organizador, participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(participante["id"], novo_evento())
    resp = client.put(f"{BASE}{inscricao_id}", json={"status": "presente"}, headers=organizador["headers"])
    assert resp.status_code == 200
    assert status_no_banco(inscricao_id) == "presente"


def test_status_invalido_retorna_400(client, participante, novo_evento, nova_inscricao):
    inscricao_id = nova_inscricao(participante["id"], novo_evento())
    resp = client.put(f"{BASE}{inscricao_id}", json={"status": "qualquer"}, headers=participante["headers"])
    assert resp.status_code == 400
