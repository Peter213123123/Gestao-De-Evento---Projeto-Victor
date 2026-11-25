# Evidências Obrigatórias — Entrega 3

Documento de comprovação técnica gerado a partir da inspeção direta do repositório `Entrega-3`.

---

## 1. GitHub com código atualizado e histórico de alterações

- **Repositório remoto (`origin`):** `https://github.com/Peter213123123/Gestao-De-Evento---Projeto-Victor.git`
- **Branch atual:** `deploy-render` (sincronizada com `origin/deploy-render`)
- **Outras branches:** `main`, `versao-corrigida`, `testes-autenticacao-pedro`

**Histórico recente de commits (`git log -n 20 --oneline`):**

```text
2df1bd1 (HEAD -> deploy-render, origin/deploy-render) Configura deploy no Render e carregamento flexivel de credenciais Firebase
59c8756 (origin/versao-corrigida, versao-corrigida) resolve conflitos do requiriments.txt
ca620f8 (versao-base-login-dashboard) Versao Base V2
7136ccc (origin/main) Merge pull request #6 from Peter213123123/feat/autenticacao-jwt-permissoes
a832b9f Merge branch 'main' into feat/autenticacao-jwt-permissoes
338e4f8 feat: implementa autenticacao JWT e controle de acesso
190775f Merge pull request #5 from Peter213123123/feat/controle-acesso-rotas
c42ca07 test: corrige test_auth.py com as rotas reais e adiciona testes de JWT e token
3f98dcb Merge pull request #4 from Peter213123123/testes-autenticacao-pedro
45f0601 Merge branch 'main' into testes-autenticacao-pedro
4171710 (origin/testes-autenticacao-pedro, testes-autenticacao-pedro) feat: adiciona suite de testes de autenticacao e autorizacao (401 e 403)
7e86bf3 Merge pull request #3 from Peter213123123/feat/perfis-e-matriz
5a2457b chore: ignora e remove arquivos de cache do versionamento
a1a16ce feat: perfis de usuário, matriz de permissões e testes com Pytest
df51321 Att_Readme_Pedro
cca34bf Update section title from 'Próximas Implementações' to 'Implementações Realizadas'
c96fc7b docs: adiciona documentação completa do Gerenciador de Eventos
f23b1db Add Firebase initial setup and infrastructure details
540992d (main) Instalando python-multipart e atualizando dependências
162f1b9 Adicionado as Entidades, POST DELETE e GET
```

> [!TIP]
> Se a entrega for avaliada pela branch `main`, faça o merge de `deploy-render` para `main` no GitHub (e aplique o `README.md` atualizado).

---

## 2. Execução dos testes automatizados

Comando executado: `.venv/bin/pytest -v`

**Resultado:** `85 passed` (100% aprovados).

| Arquivo de Teste | Quantidade | Cenários Cobertos |
| :--- | :---: | :--- |
| `tests/test_auth.py` | 15 | Login válido, senha/e-mail inválidos (`401`), sem token (`401`), token inválido/expirado/outra chave (`401`), perfil proibido (`403`), `/usuarios/me` (`200`), `esqueci-senha` e `redefinir-senha`. |
| `tests/test_certificados.py` | 12 | Emissão por Admin/Organizador (`201`), bloqueio para participante (`403`), sem presença (`400`), duplicidade (`400`), usuário inexistente (`404`), exclusão (`403`), reenvio SMTP mockado (`200`/`403`/`404`) e geração PDF/JPG (`Pillow`). |
| `tests/test_eventos.py` | 16 | Criação/edição por Admin/Organizador (status/título validados), exclusão apenas por Admin, data no passado (`400`), capacidade `<= 0` (`400`), exclusão com inscrições ativas (`400`). |
| `tests/test_inscricoes.py` | 22 | Inscrição de participante, bloqueio para Admin/Organizador (`403`), duplicidade (`400`), lotação (`400`), evento inativo (`400`) ou inexistente (`404`), restrição de dono (`403`), cancelamento, exclusão, check-in (`presente`) e emissão automática de certificado. |
| `tests/test_usuarios.py` | 15 | Cadastro público sempre `participante`, normalização de e-mail, hash bcrypt, e-mail repetido (`400`), listagem sem senha, alteração de perfil e exclusão restritos a Admin, perfil inválido (`422`), auto-remoção de Admin (`400`). |
| `tests/test_emails.py` | 5 | Histórico SMTP restrito a `admingest@gmail.com` (`401`, `403`, ordenação e status `enviado`/`erro`/`ignorado`). |

---

## 3. Swagger / OpenAPI atualizado

Inspeção direta do schema gerado por `app.openapi()` em `main.py`:

- **Título:** `API de Gestão de Eventos Acadêmicos`
- **Versão:** `2.0.0`
- **Tags configuradas:** `Usuários`, `Eventos`, `Inscrições`, `Certificados`, `E-mails`, `Infraestrutura`
- **Esquema de autenticação (`securitySchemes`):** `OAuth2PasswordBearer` (apontando para `/api/v1/usuarios/login`)
- **Rotas documentadas (`16`):**
  - `/api/v1/usuarios/`, `/api/v1/usuarios/login`, `/api/v1/usuarios/esqueci-senha`, `/api/v1/usuarios/redefinir-senha`, `/api/v1/usuarios/me`, `/api/v1/usuarios/{usuario_id}`, `/api/v1/usuarios/{usuario_id}/perfil`
  - `/api/v1/eventos/`, `/api/v1/eventos/{evento_id}`
  - `/api/v1/inscricoes/`, `/api/v1/inscricoes/{inscricao_id}`
  - `/api/v1/certificados/`, `/api/v1/certificados/{certificado_id}`, `/api/v1/certificados/{certificado_id}/reenviar`
  - `/api/v1/emails/`
  - `/health`
- **Schemas Pydantic expostos (`14`):** `UsuarioCriar`, `UsuarioPerfilUpdate`, `UsuarioResponse`, `EventoCreate`, `EventoUpdate`, `EventoResponse`, `InscricaoCreate`, `InscricaoUpdate`, `InscricaoResponse`, `CertificadoCreate`, `CertificadoResponse`, `Body_login_api_v1_usuarios_login_post`, `HTTPValidationError`, `ValidationError`.

*(Disponível em tempo de execução em `http://localhost:8000/docs` e `/openapi.json`.)*

---

## 4. README técnico

O `README.md` atualizado foi estruturado para cobrir todos os tópicos exigidos:

- Contexto, perfis, regras de negócio (1–10) e modelo/dicionário de dados.
- Contratos da API, status codes e padrão de resposta de erro.
- Matriz de permissões completa por perfil e por endpoint.
- **Estrutura real do projeto** (`main.py`, `api/v1/routers/`, `core/`, `schemas/`, `models/`, `static/`, `tests/`).
- **Stack tecnológica atual** (FastAPI, Uvicorn, Cloud Firestore, Pydantic, PyJWT, Passlib/Bcrypt, Pytest, Docker/Render).
- **Instalação, variáveis de ambiente, execução local, Docker e testes (`pytest -v`)**.

---

## 5. Demonstração das três melhorias realizadas

### Melhoria 1 — Matriz centralizada de permissões RBAC (`core/permissoes.py`)
Em vez de repetir verificações manuais de `tipo_perfil` dentro de cada rota, toda a política de autorização foi centralizada no dicionário `MATRIZ` e aplicada via dependência declarativa `Depends(permissao("nome_da_acao"))`. Isso facilita auditoria e manutenção de regras de acesso (`401` para não autenticado e `403` para perfil não autorizado).

### Melhoria 2 — Padronização global de erros e status codes (`core/exceptions.py` + `main.py`)
Foram criados handlers globais (`http_exception_handler`, `validation_exception_handler` e `generic_exception_handler`) registrados no `FastAPI` em `main.py`. Assim, qualquer erro (`400`, `401`, `403`, `404`, `422`, `500`) responde sempre no mesmo contrato JSON:
```json
{
  "success": false,
  "error": "BadRequest",
  "message": "Descrição clara do erro."
}
```

### Melhoria 3 — Carregamento flexível de credenciais Firebase e preparação para deploy (`core/database.py`, `render.yaml`, `Dockerfile`, `Procfile`)
A função `_load_firebase_credentials()` em `core/database.py` passou a aceitar três fontes (`FIREBASE_CREDENTIALS_JSON`, `FIREBASE_CREDENTIALS_BASE64` e `FIREBASE_CREDENTIALS_PATH`), permitindo rodar localmente com arquivo `.json` e em produção (Render/Docker) via variáveis de ambiente sem expor segredos no código.

---

## 6. Configurações de ambiente preparadas, sem exposição de credenciais

- **Proteção no `.gitignore`:** arquivos sensíveis estão explicitamente ignorados (`.env`, `firebase.json`, `*firebase-adminsdk*.json`).
- **Leitura via variáveis de ambiente (`core/config.py` e `core/database.py`):**
  - `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `FIREBASE_CREDENTIALS_PATH`, `FIREBASE_CREDENTIALS_JSON`, `FIREBASE_CREDENTIALS_BASE64`
- **Configuração de produção (`render.yaml`):**
  - `SECRET_KEY` com `generateValue: true`
  - `FIREBASE_CREDENTIALS_JSON` com `sync: false` (valor inserido apenas no painel do Render, nunca versionado no Git).
