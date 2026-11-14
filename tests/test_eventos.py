"""Eventos: matriz de permissões (admin / organizador / participante) e regras de negócio."""
from datetime import date, timedelta

import pytest

from tests.conftest import fake_db

BASE = "/api/v1/eventos/"


def payload(**campos):
    dados = {
        "titulo": "Semana de Tecnologia",
        "descricao": "Evento de teste",
        "data_evento": (date.today() + timedelta(days=10)).isoformat(),
        "capacidade": 50,
    }
    dados.update(campos)
    return dados


def test_criar_evento_sem_token_retorna_401(client):
    assert client.post(BASE, json=payload()).status_code == 401


def test_participante_nao_cria_evento(client, participante):
    assert client.post(BASE, json=payload(), headers=participante["headers"]).status_code == 403


@pytest.mark.parametrize("perfil", ["admin", "organizador"])
def test_admin_e_organizador_criam_evento(client, request, perfil):
    usuario = request.getfixturevalue(perfil)
    resp = client.post(BASE, json=payload(), headers=usuario["headers"])
    assert resp.status_code == 201
    assert resp.json()["status"] == "ativo"


def test_evento_com_data_no_passado_retorna_400(client, admin):
    passado = (date.today() - timedelta(days=1)).isoformat()
    assert client.post(BASE, json=payload(data_evento=passado), headers=admin["headers"]).status_code == 400


def test_evento_com_capacidade_zero_retorna_400(client, admin):
    assert client.post(BASE, json=payload(capacidade=0), headers=admin["headers"]).status_code == 400


@pytest.mark.parametrize("perfil", ["admin", "organizador", "participante"])
def test_todos_os_perfis_listam_eventos(client, request, perfil, novo_evento):
    novo_evento()
    usuario = request.getfixturevalue(perfil)
    resp = client.get(BASE, headers=usuario["headers"])
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_participante_nao_edita_evento(client, participante, novo_evento):
    evento_id = novo_evento()
    resp = client.put(f"{BASE}{evento_id}", json={"titulo": "Novo título"}, headers=participante["headers"])
    assert resp.status_code == 403


def test_organizador_edita_evento(client, organizador, novo_evento):
    evento_id = novo_evento()
    resp = client.put(f"{BASE}{evento_id}", json={"titulo": "Novo título"}, headers=organizador["headers"])
    assert resp.status_code == 200
    assert resp.json()["titulo"] == "Novo título"


@pytest.mark.parametrize("perfil", ["organizador", "participante"])
def test_somente_admin_exclui_evento(client, request, perfil, novo_evento):
    evento_id = novo_evento()
    usuario = request.getfixturevalue(perfil)
    assert client.delete(f"{BASE}{evento_id}", headers=usuario["headers"]).status_code == 403
    assert fake_db.collection("eventos").document(evento_id).get().exists  # continua no banco


def test_admin_exclui_evento(client, admin, novo_evento):
    evento_id = novo_evento()
    assert client.delete(f"{BASE}{evento_id}", headers=admin["headers"]).status_code == 200
    assert not fake_db.collection("eventos").document(evento_id).get().exists
