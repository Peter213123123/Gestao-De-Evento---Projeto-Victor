"""Controle de acesso: confere a MATRIZ de permissões e o 401 / 403 nas rotas protegidas."""
from core.permissoes import MATRIZ, PERFIS_VALIDOS, tem_permissao

PERFIS = {"admin", "organizador", "participante"}

# Matriz da 1ª Unidade (README, seção 10.1): ação -> perfis que podem executar
MATRIZ_ESPERADA = {
    "criar_editar_eventos": {"admin", "organizador"},
    "excluir_eventos": {"admin"},
    "listar_eventos": {"admin", "organizador", "participante"},
    "inscrever_se": {"participante"},
    "listar_inscritos": {"admin", "organizador"},
    "cancelar_inscricao_propria": {"participante"},
}

# (método, caminho) de todas as rotas que exigem token
ROTAS_PROTEGIDAS = [
    ("GET", "/api/v1/usuarios/me"),
    ("GET", "/api/v1/usuarios/"),
    ("PATCH", "/api/v1/usuarios/x/perfil"),
    ("DELETE", "/api/v1/usuarios/x"),
    ("GET", "/api/v1/eventos/"),
    ("POST", "/api/v1/eventos/"),
    ("PUT", "/api/v1/eventos/x"),
    ("DELETE", "/api/v1/eventos/x"),
    ("GET", "/api/v1/inscricoes/"),
    ("POST", "/api/v1/inscricoes/"),
    ("PUT", "/api/v1/inscricoes/x"),
    ("DELETE", "/api/v1/inscricoes/x"),
    ("GET", "/api/v1/certificados/"),
    ("POST", "/api/v1/certificados/"),
    ("DELETE", "/api/v1/certificados/x"),
]

EVENTO = {"titulo": "Teste", "descricao": "x", "data_evento": "2030-01-01", "capacidade": 10}
INSCRICAO = {"id_usuario": "doc1", "id_evento": "x"}
CERTIFICADO = {"id_usuario": "u1", "id_evento": "e1", "carga_horaria": 10}

# (método, caminho, corpo) que cada perfil NÃO pode executar -> deve dar 403
PROIBIDO_PARA_PARTICIPANTE = [
    ("POST", "/api/v1/eventos/", EVENTO),
    ("PUT", "/api/v1/eventos/x", {"titulo": "Novo"}),
    ("DELETE", "/api/v1/eventos/x", None),
    ("GET", "/api/v1/usuarios/", None),
    ("PATCH", "/api/v1/usuarios/x/perfil", {"tipo_perfil": "admin"}),
    ("DELETE", "/api/v1/usuarios/x", None),
    ("GET", "/api/v1/inscricoes/", None),
    ("POST", "/api/v1/certificados/", CERTIFICADO),
    ("DELETE", "/api/v1/certificados/x", None),
]
PROIBIDO_PARA_ORGANIZADOR = [
    ("DELETE", "/api/v1/eventos/x", None),
    ("GET", "/api/v1/usuarios/", None),
    ("PATCH", "/api/v1/usuarios/x/perfil", {"tipo_perfil": "admin"}),
    ("DELETE", "/api/v1/usuarios/x", None),
    ("POST", "/api/v1/inscricoes/", INSCRICAO),
    ("DELETE", "/api/v1/inscricoes/x", None),
]
PROIBIDO_PARA_ADMIN = [
    ("POST", "/api/v1/inscricoes/", INSCRICAO),
    ("DELETE", "/api/v1/inscricoes/x", None),
]


def _todas_devem_dar_403(client, usuario, rotas):
    for metodo, caminho, corpo in rotas:
        resp = client.request(metodo, caminho, json=corpo, headers=usuario["headers"])
        assert resp.status_code == 403, (
            f"{usuario['perfil']} em {metodo} {caminho} retornou {resp.status_code} (esperado 403)"
        )


def test_matriz_confere_com_a_primeira_unidade():
    for acao, perfis_permitidos in MATRIZ_ESPERADA.items():
        for perfil in PERFIS:
            esperado = perfil in perfis_permitidos
            assert tem_permissao({"tipo_perfil": perfil}, acao) == esperado, f"{acao} / {perfil}"


def test_existem_exatamente_tres_perfis():
    assert set(PERFIS_VALIDOS) == PERFIS


def test_matriz_so_cita_perfis_validos():
    for acao, perfis in MATRIZ.items():
        assert set(perfis) <= PERFIS, f"A ação {acao} cita perfil inexistente"


def test_perfil_desconhecido_nao_tem_nenhuma_permissao():
    for acao in MATRIZ:
        assert not tem_permissao({"tipo_perfil": "chefe"}, acao)
        assert not tem_permissao({}, acao)


def test_todas_as_rotas_protegidas_exigem_token_401(client):
    for metodo, caminho in ROTAS_PROTEGIDAS:
        resp = client.request(metodo, caminho)
        assert resp.status_code == 401, f"{metodo} {caminho} sem token retornou {resp.status_code}"


def test_participante_recebe_403_nas_rotas_proibidas(client, participante):
    _todas_devem_dar_403(client, participante, PROIBIDO_PARA_PARTICIPANTE)


def test_organizador_recebe_403_nas_rotas_proibidas(client, organizador):
    _todas_devem_dar_403(client, organizador, PROIBIDO_PARA_ORGANIZADOR)


def test_admin_recebe_403_nas_rotas_proibidas(client, admin):
    _todas_devem_dar_403(client, admin, PROIBIDO_PARA_ADMIN)
