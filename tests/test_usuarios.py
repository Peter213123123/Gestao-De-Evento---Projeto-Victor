"""Perfis de usuário: cadastro público, listagem, troca de perfil e exclusão."""
import pytest

from tests.conftest import fake_db

BASE = "/api/v1/usuarios/"


def test_cadastro_publico_sempre_cria_participante(client):
    resp = client.post(BASE, json={
        "nome": "Novo", "email": "novo@teste.com", "senha": "senha12345",
        "tipo_perfil": "admin",  # tentativa de se auto-promover: deve ser ignorada
    })
    assert resp.status_code == 201
    assert resp.json()["tipo_perfil"] == "participante"
    salvo = fake_db.collection("usuarios").document(resp.json()["id"]).get().to_dict()
    assert salvo["tipo_perfil"] == "participante"


def test_senha_e_salva_com_hash(client):
    resp = client.post(BASE, json={"nome": "Novo", "email": "novo@teste.com", "senha": "senha12345"})
    salvo = fake_db.collection("usuarios").document(resp.json()["id"]).get().to_dict()
    assert salvo["senha"] != "senha12345"
    assert salvo["senha"].startswith("$2")  # formato do bcrypt
    assert "senha" not in resp.json()


def test_cadastro_com_email_repetido_retorna_400(client, participante):
    resp = client.post(BASE, json={"nome": "Outro", "email": participante["email"], "senha": "senha12345"})
    assert resp.status_code == 400


def test_listar_usuarios_sem_token_retorna_401(client):
    assert client.get(BASE).status_code == 401


@pytest.mark.parametrize("perfil", ["participante", "organizador"])
def test_so_admin_lista_usuarios(client, request, perfil):
    usuario = request.getfixturevalue(perfil)
    assert client.get(BASE, headers=usuario["headers"]).status_code == 403


def test_admin_lista_usuarios_sem_expor_senha(client, admin, participante):
    resp = client.get(BASE, headers=admin["headers"])
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert all("senha" not in u for u in resp.json())


def test_admin_altera_perfil_de_usuario(client, admin, participante):
    resp = client.patch(f"{BASE}{participante['id']}/perfil", json={"tipo_perfil": "organizador"},
                        headers=admin["headers"])
    assert resp.status_code == 200
    assert resp.json()["tipo_perfil"] == "organizador"
    assert fake_db.collection("usuarios").document(participante["id"]).get().to_dict()["tipo_perfil"] == "organizador"


@pytest.mark.parametrize("perfil", ["participante", "organizador"])
def test_nao_admin_nao_altera_perfil(client, request, perfil, outro_participante):
    usuario = request.getfixturevalue(perfil)
    resp = client.patch(f"{BASE}{outro_participante['id']}/perfil", json={"tipo_perfil": "admin"},
                        headers=usuario["headers"])
    assert resp.status_code == 403


def test_perfil_invalido_retorna_422(client, admin, participante):
    resp = client.patch(f"{BASE}{participante['id']}/perfil", json={"tipo_perfil": "chefe"},
                        headers=admin["headers"])
    assert resp.status_code == 422


def test_admin_nao_pode_remover_o_proprio_perfil(client, admin):
    resp = client.patch(f"{BASE}{admin['id']}/perfil", json={"tipo_perfil": "participante"},
                        headers=admin["headers"])
    assert resp.status_code == 400


def test_alterar_perfil_de_usuario_inexistente_retorna_404(client, admin):
    resp = client.patch(f"{BASE}naoexiste/perfil", json={"tipo_perfil": "organizador"},
                        headers=admin["headers"])
    assert resp.status_code == 404


def test_so_admin_exclui_usuario(client, admin, participante, outro_participante):
    assert client.delete(f"{BASE}{outro_participante['id']}", headers=participante["headers"]).status_code == 403
    assert client.delete(f"{BASE}{outro_participante['id']}", headers=admin["headers"]).status_code == 200
