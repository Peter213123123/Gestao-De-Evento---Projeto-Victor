# Controle de Acesso nas Rotas — Evidências

Atividade: **Aplicação de Controle de Acesso nas Rotas** (2ª Unidade)

## 1. Dependências de acesso aplicadas (Passo 1)

Os endpoints usam `Depends(permissao("acao"))` (arquivo `core/permissoes.py`). A ação aponta para o dicionário `MATRIZ`, que define quais perfis podem executá-la. Sem token, a resposta é **401**; com token de um perfil sem permissão, **403**.

| Endpoint | Ação na `MATRIZ` | Perfis autorizados |
| :--- | :--- | :--- |
| `POST /api/v1/eventos/` | `criar_editar_eventos` | admin, organizador |
| `PUT /api/v1/eventos/{id}` | `criar_editar_eventos` | admin, organizador |
| `DELETE /api/v1/eventos/{id}` | `excluir_eventos` | admin |
| `GET /api/v1/usuarios/` | `gerenciar_usuarios` | admin |
| `PATCH /api/v1/usuarios/{id}/perfil` | `gerenciar_usuarios` | admin |
| `DELETE /api/v1/usuarios/{id}` | `gerenciar_usuarios` | admin |
| `POST /api/v1/inscricoes/` | `inscrever_se` | participante (em nome próprio) |
| `GET /api/v1/inscricoes/` | `listar_inscritos` | admin, organizador |
| `PUT /api/v1/inscricoes/{id}` | `cancelar_inscricao_propria` / `registrar_presenca` | participante (a própria) / admin, organizador |
| `DELETE /api/v1/inscricoes/{id}` | `cancelar_inscricao_propria` | participante (a própria) |
| `POST /api/v1/certificados/` | `emitir_certificados` | admin, organizador |
| `DELETE /api/v1/certificados/{id}` | `emitir_certificados` | admin, organizador |

## 2. Operações incompatíveis com o perfil (Passo 2)

- Participante criando evento → 403
- Organizador excluindo evento → 403
- Participante listando usuários → 403
- Admin ou organizador se inscrevendo em evento → 403
- Participante cancelando a inscrição de outra pessoa → 403
- Qualquer rota protegida sem token ou com token inválido → 401

Esses cenários também são verificados pelos testes automáticos (`python -m pytest -v`).

## 3. Requisições executadas (Passo 3)

Ambiente: API iniciada com `python rodar_sem_firebase.py` (Firestore em memória), testada no Swagger (`http://127.0.0.1:8000/docs`).
Contas de teste (senha `senha12345`): `admin@teste.com`, `org@teste.com`, `aluno@teste.com`.

| # | Usuário | Requisição | Esperado | Obtido | Print |
| :-: | :--- | :--- | :-: | :-: | :--- |
| 1 | Sem login | `GET /api/v1/eventos/` | 401 | _preencher_ | `img/01-sem-login-401.png` |
| 2 | Participante | `POST /api/v1/eventos/` | 403 | _preencher_ | `img/02-participante-cria-evento-403.png` |
| 3 | Organizador | `POST /api/v1/eventos/` | 201 | _preencher_ | `img/03-organizador-cria-evento-201.png` |
| 4 | Organizador | `DELETE /api/v1/eventos/{id}` | 403 | _preencher_ | `img/04-organizador-exclui-evento-403.png` |
| 5 | Admin | `DELETE /api/v1/eventos/{id}` | 200 | _preencher_ | `img/05-admin-exclui-evento-200.png` |
| 6 | Participante | `GET /api/v1/usuarios/` | 403 | _preencher_ | `img/06-participante-lista-usuarios-403.png` |

### Prints

![01 - Sem login (401)](img/01-sem-login-401.png)

![02 - Participante criando evento (403)](img/02-participante-cria-evento-403.png)

![03 - Organizador criando evento (201)](img/03-organizador-cria-evento-201.png)

![04 - Organizador excluindo evento (403)](img/04-organizador-exclui-evento-403.png)

![05 - Admin excluindo evento (200)](img/05-admin-exclui-evento-200.png)

![06 - Participante listando usuários (403)](img/06-participante-lista-usuarios-403.png)

## 4. Resultado dos testes automáticos

Comando: `python -m pytest -v`

Resultado: _preencher (ex.: 62 passed)_ — print em `img/07-pytest-verbose.png`.

![07 - pytest -v](img/07-pytest-verbose.png)
