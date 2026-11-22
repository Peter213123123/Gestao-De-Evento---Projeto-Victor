# 📅 Gerenciador de Eventos Acadêmicos

API REST para centralizar a gestão de eventos acadêmicos: cadastro e autenticação de usuários, criação e gestão de eventos, controle de capacidade, inscrições e emissão de certificados, com persistência no Cloud Firestore.

![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Firestore](https://img.shields.io/badge/Cloud_Firestore-FFCA28?logo=firebase&logoColor=black)
![Swagger](https://img.shields.io/badge/Swagger-OAS_3.1-85EA2D?logo=swagger&logoColor=black)

---

## 👥 Equipe

| Nome | Matrícula |
| :--- | :--- |
| Aslley Emanuel Da Costa Mariano | 01878630 |
| Caio Victor Barbosa Monteiro | 01882905 |
| Edson Rodrigues Cardoso Dos Santos | 01351404 |
| Fábio Luis Damasceno da Silva | 01212500 |
| João Paulo Romão Sampaio de Melo | 01871330 |
| Pedro Felipe Santiago Neto | 01891949 |
| Sandrielly Maria Farias da Silva Alves Bezerra | 01904552 |

---

## 📑 Sumário

1. [Contexto do Problema](#1-contexto-do-problema)
2. [Perfis de Usuário](#2-perfis-de-usuário)
3. [Regras de Negócio](#3-regras-de-negócio)
4. [Entidades Principais](#4-entidades-principais)
5. [Modelo de Dados](#5-modelo-de-dados)
6. [Dicionário de Dados](#6-dicionário-de-dados)
7. [Contratos e Endpoints da API](#7-contratos-e-endpoints-da-api)
8. [Status Codes](#8-status-codes)
9. [Padrão de Resposta e Erro](#9-padrão-de-resposta-e-erro)
10. [Matriz de Permissões](#10-matriz-de-permissões)
11. [Estrutura do Projeto](#11-estrutura-do-projeto)
12. [Tecnologias](#12-tecnologias)
13. [Persistência, Instalação e Execução](#13-persistência-instalação-e-execução)
14. [Backlog](#14-backlog)
15. [Critérios de Aceitação](#15-critérios-de-aceitação)
16. [Implementações Realizadas](#16-implementações-realizadas)
17. [Testes Automatizados e Evidências](#17-testes-automatizados-e-evidências)

---

## 1. Contexto do Problema

**Qual problema o sistema resolve?**
A gestão manual e descentralizada de eventos acadêmicos (planilhas e formulários soltos) gera retrabalho, perda de dados, inscrições duplicadas e lentidão na emissão de certificados.

**Quem vai usar?**
Alunos (participantes), professores/coordenadores (organizadores) e a Secretaria/TI da instituição (administradores).

**Qual o objetivo da API?**
Centralizar todo o fluxo de eventos acadêmicos, desde a criação da atividade e o controle de capacidade até a gestão de inscrições, registro de presença e emissão de certificados.

---

## 2. Perfis de Usuário

| Perfil | Descrição |
| :--- | :--- |
| **Admin** | Controle total. Gerencia usuários, perfis, eventos, inscrições e certificados. |
| **Organizador** | Professores ou coordenadores. Criam e editam eventos, listam inscritos, registram presença e emitem certificados. |
| **Participante** | Alunos ou visitantes. Visualizam eventos disponíveis, realizam e cancelam a própria inscrição e consultam certificados. |

---

## 3. Regras de Negócio

1. Um usuário não pode se inscrever duas vezes no mesmo evento.
2. Um evento não aceita novas inscrições se a capacidade máxima for atingida.
3. Não é permitido cadastrar ou atualizar um evento com `data_evento` no passado ou `capacidade <= 0`.
4. O e-mail de um usuário deve ser único em todo o sistema.
5. Um participante só pode criar, cancelar ou excluir a própria inscrição, sem alterar inscrições de terceiros.
6. Apenas usuários com perfil **Admin** ou **Organizador** podem criar/editar eventos; apenas **Admin** pode excluir eventos.
7. Um evento não pode ser excluído se houver inscrições ativas vinculadas.
8. A senha do usuário não pode trafegar em retornos da API nem ser salva em texto plano (utiliza hash `bcrypt`).
9. Inscrições só podem ser feitas em eventos com status **`ativo`**.
10. A emissão de certificado é bloqueada para participantes sem o status **`presente`** (e impede emissão duplicada no mesmo evento).

---

## 4. Entidades Principais

- **Usuário (`usuarios`):** identifica quem acessa o sistema, permitindo autenticação JWT e controle de acesso por perfil.
- **Evento (`eventos`):** armazena as informações das atividades acadêmicas oferecidas (`titulo`, `descricao`, `data_evento`, `capacidade`, `status`).
- **Inscrição (`inscricoes`):** conecta o usuário ao evento, registrando `data_inscricao` e `status` (`confirmada`, `cancelada`, `presente`).
- **Certificado (`certificados`):** registra a emissão do certificado (`id_usuario`, `id_evento`, `carga_horaria`, `codigo_validacao`, `emitido_em`).

---

## 5. Modelo de Dados

**Relacionamentos:**

- Usuário (1) — (N) Inscrição: um usuário pode ter várias inscrições.
- Evento (1) — (N) Inscrição: um evento pode ter várias inscrições.
- Usuário (1) — (N) Certificado e Evento (1) — (N) Certificado.

**Coleções no Cloud Firestore:**

```text
usuarios     (id, nome, email, senha [hash bcrypt], tipo_perfil)
eventos      (id, titulo, descricao, data_evento, capacidade, status)
inscricoes   (id, id_usuario, id_evento, data_inscricao, status)
certificados (id, id_usuario, id_evento, carga_horaria, codigo_validacao, emitido_em)
```

---

## 6. Dicionário de Dados

| Entidade | Campo | Tipo | Obrigatório | Regra / Restrição |
| :--- | :--- | :--- | :---: | :--- |
| Usuário | `email` | string | Sim | Único no sistema. |
| Usuário | `senha` | string | Sim | Mínimo 6 caracteres; armazenada com hash `bcrypt`. |
| Usuário | `tipo_perfil` | string | Sim | Apenas: `admin`, `organizador`, `participante`. |
| Evento | `titulo` | string | Sim | Mínimo 3 caracteres. |
| Evento | `capacidade` | int | Sim | Deve ser maior que `0`. |
| Evento | `data_evento` | date | Sim | Não pode ser anterior à data atual. |
| Evento | `status` | string | Sim | Inicial `ativo` (`ativo`, `concluido`, `cancelado`). |
| Inscrição | `status` | string | Sim | `confirmada`, `cancelada` ou `presente`. |
| Certificado | `carga_horaria` | int | Sim | Deve ser maior que `0`. |

---

## 7. Contratos e Endpoints da API

### Resumo dos Endpoints

| Recurso | Método | Rota | Descrição |
| :--- | :---: | :--- | :--- |
| Infraestrutura | `GET` | `/health` | Healthcheck operacional da API |
| Usuários | `POST` | `/api/v1/usuarios/` | Cadastro público (sempre cria `participante`) |
| Usuários | `POST` | `/api/v1/usuarios/login` | Login OAuth2 (`username` = e-mail) com retorno de JWT |
| Usuários | `GET` | `/api/v1/usuarios/me` | Dados do próprio usuário autenticado |
| Usuários | `GET` | `/api/v1/usuarios/` | Lista todos os usuários sem expor senha (Admin) |
| Usuários | `PATCH` | `/api/v1/usuarios/{usuario_id}/perfil` | Altera o perfil do usuário (Admin) |
| Usuários | `DELETE` | `/api/v1/usuarios/{usuario_id}` | Remove um usuário (Admin) |
| Eventos | `GET` | `/api/v1/eventos/` | Lista todos os eventos |
| Eventos | `POST` | `/api/v1/eventos/` | Cria evento com status inicial `ativo` |
| Eventos | `PUT` | `/api/v1/eventos/{evento_id}` | Atualiza evento existente |
| Eventos | `DELETE` | `/api/v1/eventos/{evento_id}` | Exclui evento sem inscrições ativas |
| Inscrições | `GET` | `/api/v1/inscricoes/` | Lista todas as inscrições |
| Inscrições | `POST` | `/api/v1/inscricoes/` | Inscreve o participante autenticado em um evento ativo |
| Inscrições | `PUT` | `/api/v1/inscricoes/{inscricao_id}` | Atualiza status para `cancelada` ou `presente` |
| Inscrições | `DELETE` | `/api/v1/inscricoes/{inscricao_id}` | Exclui a própria inscrição |
| Certificados | `GET` | `/api/v1/certificados/` | Lista certificados emitidos |
| Certificados | `POST` | `/api/v1/certificados/` | Emite certificado para participante `presente` |
| Certificados | `DELETE` | `/api/v1/certificados/{certificado_id}` | Exclui certificado |

### Exemplo: `POST /api/v1/usuarios/` — Criação de usuário

**Request:**

```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "senhaforte123"
}
```

> **Nota:** o perfil não é enviado no cadastro. Todo cadastro público cria um `participante`; somente um Admin altera o perfil em `PATCH /api/v1/usuarios/{id}/perfil`.

**Response `201 Created`:**

```json
{
  "id": "usr_123",
  "nome": "João Silva",
  "email": "joao@email.com",
  "tipo_perfil": "participante"
}
```

> **Nota:** a senha nunca retorna no payload de saída.

---

## 8. Status Codes

| Situação | Status HTTP |
| :--- | :--- |
| Consulta ou atualização realizada com sucesso | `200 OK` |
| Registro criado com sucesso (usuário, evento, inscrição, certificado) | `201 Created` |
| Exclusão realizada com sucesso | `204 No Content` |
| Erro de regra de negócio (ex.: evento lotado, data no passado) | `400 Bad Request` |
| Usuário não autenticado (token ausente, inválido ou expirado) | `401 Unauthorized` |
| Sem permissão ou tentativa de alterar recurso de terceiros | `403 Forbidden` |
| Registro não encontrado (ex.: ID inexistente) | `404 Not Found` |
| Erro de validação de dados (Pydantic / Schema) | `422 Unprocessable Entity` |
| Erro interno inesperado no servidor | `500 Internal Server Error` |

---

## 9. Padrão de Resposta e Erro

Todas as exceções são tratadas globalmente em `core/exceptions.py`, retornando um envelope padronizado:

**Exemplo de erro de regra de negócio (`400`):**

```json
{
  "success": false,
  "error": "BadRequest",
  "message": "Não é possível realizar a inscrição. O evento atingiu sua capacidade máxima."
}
```

**Exemplo de erro de validação (`422`):**

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Erro de validação nos dados enviados.",
  "details": []
}
```

---

## 10. Matriz de Permissões

### 10.1 Matriz por funcionalidade (definida na 1ª Unidade)

| Funcionalidade | Admin | Organizador | Participante |
| :--- | :---: | :---: | :---: |
| Criar/Editar eventos | ✅ | ✅ | ❌ |
| Excluir eventos | ✅ | ❌ | ❌ |
| Listar eventos | ✅ | ✅ | ✅ |
| Inscrever-se em eventos | ❌ | ❌ | ✅ |
| Listar inscritos no evento | ✅ | ✅ | ❌ |
| Cancelar inscrição (própria) | ❌ | ❌ | ✅ |

### 10.2 Matriz final por endpoint (implementada)

Legenda: 🌐 público · 🔒 exige token (sem token → `401`) · ✅ permitido · ❌ negado (`403 Forbidden`)

| Endpoint | Acesso | Admin | Organizador | Participante | Regra adicional |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `POST /api/v1/usuarios/` | 🌐 | — | — | — | O cadastro público sempre cria `participante` |
| `POST /api/v1/usuarios/login` | 🌐 | — | — | — | Retorna o JWT |
| `GET /api/v1/usuarios/me` | 🔒 | ✅ | ✅ | ✅ | Retorna apenas os dados do próprio usuário |
| `GET /api/v1/usuarios/` | 🔒 | ✅ | ❌ | ❌ | — |
| `PATCH /api/v1/usuarios/{id}/perfil` | 🔒 | ✅ | ❌ | ❌ | Admin não pode remover o próprio perfil de admin |
| `DELETE /api/v1/usuarios/{id}` | 🔒 | ✅ | ❌ | ❌ | — |
| `GET /api/v1/eventos/` | 🔒 | ✅ | ✅ | ✅ | — |
| `POST /api/v1/eventos/` | 🔒 | ✅ | ✅ | ❌ | — |
| `PUT /api/v1/eventos/{id}` | 🔒 | ✅ | ✅ | ❌ | — |
| `DELETE /api/v1/eventos/{id}` | 🔒 | ✅ | ❌ | ❌ | Bloqueado se houver inscrições ativas |
| `POST /api/v1/inscricoes/` | 🔒 | ❌ | ❌ | ✅ | O `id_usuario` precisa ser o do token |
| `GET /api/v1/inscricoes/` | 🔒 | ✅ | ✅ | ❌ | Lista os inscritos |
| `PUT /api/v1/inscricoes/{id}` (`cancelada`) | 🔒 | ❌ | ❌ | ✅ | Somente a própria inscrição |
| `PUT /api/v1/inscricoes/{id}` (`presente`) | 🔒 | ✅ | ✅ | ❌ | Registro de presença (check-in) |
| `DELETE /api/v1/inscricoes/{id}` | 🔒 | ❌ | ❌ | ✅ | Somente a própria inscrição |
| `GET /api/v1/certificados/` | 🔒 | ✅ | ✅ | ✅ | — |
| `POST /api/v1/certificados/` | 🔒 | ✅ | ✅ | ❌ | Exige presença confirmada e impede duplicidade |
| `DELETE /api/v1/certificados/{id}` | 🔒 | ✅ | ✅ | ❌ | — |

### 10.3 Como a matriz está no código

- Os três perfis (`admin`, `organizador`, `participante`) e o dicionário `MATRIZ` ficam em `core/permissoes.py`.
- Cada endpoint usa `Depends(permissao("nome_da_acao"))`.
- O perfil `tipo_perfil` é validado em `schemas/usuario_schema.py` e `models/usuario.py`.

### 10.4 Como criar o primeiro Admin

1. Cadastre o usuário normalmente em `POST /api/v1/usuarios/`.
2. No console do Firebase, abra o Firestore, coleção `usuarios`, e altere o campo `tipo_perfil` desse documento para `admin`.
3. Faça login novamente em `POST /api/v1/usuarios/login` para gerar um novo token com o perfil atualizado.

Depois disso, o Admin pode promover outros usuários via `PATCH /api/v1/usuarios/{id}/perfil`.

---

## 11. Estrutura do Projeto

```text
Entrega-3/
├── api/
│   ├── api.py                      # Registro central dos routers v1
│   └── v1/
│       └── routers/
│           ├── usuarios.py         # Cadastro, login JWT, /me e gestão de perfis
│           ├── eventos.py          # CRUD de eventos acadêmicos
│           ├── inscricoes.py       # Inscrições, cancelamento e check-in
│           └── certificados.py     # Emissão, listagem e exclusão de certificados
├── core/
│   ├── auth.py                     # OAuth2PasswordBearer e validação de JWT
│   ├── config.py                   # Leitura de variáveis de ambiente (.env)
│   ├── database.py                 # Inicialização do Firebase Admin e cliente Firestore
│   ├── exceptions.py               # Handlers globais e padronização de erros
│   ├── permissoes.py               # Matriz de permissões RBAC
│   └── security.py                 # Hash bcrypt e criação de tokens JWT
├── models/                         # Modelos de domínio auxiliares
│   ├── evento.py
│   ├── inscricao.py
│   └── usuario.py
├── schemas/                        # Contratos Pydantic de entrada e saída
│   ├── certificado_schema.py
│   ├── evento_schema.py
│   ├── inscricao_schema.py
│   └── usuario_schema.py
├── static/                         # Interface web básica (login e dashboard)
│   ├── dashboard.html
│   └── login.html
├── tests/                          # Suíte de testes automatizados (Pytest)
│   ├── conftest.py
│   ├── fake_firestore.py
│   ├── test_auth.py
│   ├── test_certificados.py
│   ├── test_eventos.py
│   ├── test_inscricoes.py
│   └── test_usuarios.py
├── Dockerfile                      # Containerização para deploy
├── Procfile                        # Comando de inicialização web
├── render.yaml                     # Blueprint de deploy no Render
├── pytest.ini                      # Configuração do Pytest
├── requirements.txt                # Dependências do projeto
└── main.py                         # Instância FastAPI, Swagger, CORS e rotas estáticas
```

---

## 12. Tecnologias

| Tecnologia | Uso no projeto |
| :--- | :--- |
| **Python 3 / FastAPI** | Construção da API REST, tipagem e documentação OpenAPI/Swagger automática. |
| **Uvicorn** | Servidor ASGI para execução local e em produção. |
| **Cloud Firestore (`firebase-admin`)** | Banco de dados NoSQL em nuvem para persistência de usuários, eventos, inscrições e certificados. |
| **Pydantic / pydantic-settings** | Validação de entrada/saída e schemas do OpenAPI. |
| **PyJWT** | Geração e validação de tokens de autenticação JWT (`Bearer`). |
| **Passlib + Bcrypt** | Hashing seguro de senhas. |
| **Pytest** | Suíte de testes automatizados (cenários positivos e negativos). |
| **Docker / Render** | Empacotamento e configuração de deploy em nuvem. |

---

## 13. Persistência, Instalação e Execução

### 13.1 Estratégia de Persistência e Variáveis de Ambiente

A aplicação utiliza **Cloud Firestore** (via `firebase-admin`). Em `core/database.py`, as credenciais podem ser fornecidas de três formas:

- `FIREBASE_CREDENTIALS_JSON`: conteúdo JSON da conta de serviço (ideal para deploy em nuvem como o Render).
- `FIREBASE_CREDENTIALS_BASE64`: conteúdo JSON codificado em Base64.
- `FIREBASE_CREDENTIALS_PATH`: caminho para o arquivo local `.json` da conta de serviço (ideal para desenvolvimento local).

Crie um arquivo `.env` na raiz do projeto com as variáveis:

```env
SECRET_KEY=sua_chave_secreta_forte
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FIREBASE_CREDENTIALS_PATH=caminho/para/firebase-adminsdk.json
```

### 13.2 Instalação e Execução Local

```bash
# 1. Clone o repositório e acesse a pasta
git clone https://github.com/Peter213123123/Entrega-3.git
cd Entrega-3

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor FastAPI
uvicorn main:app --reload
```

Após iniciar, acesse:

- **Swagger UI (OpenAPI):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Healthcheck:** `http://localhost:8000/health`
- **Tela de Login:** `http://localhost:8000/login`

### 13.3 Execução com Docker / Deploy (Render)

```bash
docker build -t entrega-3-api .
docker run -p 8000:8000 --env-file .env entrega-3-api
```

Para deploy no **Render**, o repositório já inclui `render.yaml` e `Procfile`, exigindo a configuração das variáveis `SECRET_KEY` e `FIREBASE_CREDENTIALS_JSON`.

---

## 14. Backlog

| ID | História de Usuário | Prioridade |
| :--- | :--- | :---: |
| US01 | Como usuário, quero me cadastrar no sistema para poder acessá-lo. | Alta |
| US02 | Como administrador, quero visualizar todos os usuários cadastrados. | Média |
| US03 | Como organizador, quero criar um evento definindo data e limite de vagas. | Alta |
| US04 | Como organizador, quero editar as informações de um evento criado por mim. | Média |
| US05 | Como participante, quero listar todos os eventos ativos para escolher qual participar. | Alta |
| US06 | Como participante, quero me inscrever em um evento específico. | Alta |
| US07 | Como participante, quero cancelar minha inscrição caso eu desista. | Média |
| US08 | Como organizador, quero listar todos os participantes inscritos no meu evento. | Alta |
| US09 | Como admin, quero excluir ou inativar um evento que foi cancelado pela instituição. | Baixa |
| US10 | Como organizador, quero dar "check-in" na presença dos inscritos e emitir certificados. | Média |

---

## 15. Critérios de Aceitação

### Cadastro de Evento (US03)

1. O sistema deve exigir título, data e capacidade.
2. A data do evento não pode ser salva se for anterior ao dia de hoje.
3. A capacidade deve ser um número inteiro maior que `0`.
4. O sistema deve atribuir automaticamente o status `ativo` na criação.
5. O sistema deve retornar `201 Created` em caso de sucesso.

### Inscrição em Evento (US06)

1. O sistema deve vincular o ID do participante autenticado ao ID do evento.
2. O sistema deve rejeitar a inscrição e retornar `400` se a capacidade máxima já foi atingida ou se houver duplicidade.
3. O sistema deve rejeitar a inscrição se o evento não estiver ativo.
4. O sistema deve retornar `201 Created` e os dados da inscrição (data e hora).
5. Se o ID do evento fornecido não existir, o sistema deve retornar `404 Not Found`.

---

## 16. Implementações Realizadas

- [x] **1.** Configuração inicial e infraestrutura do Firebase (Cloud Firestore)
- [x] **2.** Conexão e carregamento flexível de credenciais na API (`core/database.py`)
- [x] **3.** Models e schemas Pydantic com documentação OpenAPI
- [x] **4.** CRUDs completos de Usuários, Eventos, Inscrições e Certificados
- [x] **5.** Segurança, hash de senhas (`bcrypt`) e autenticação JWT (`OAuth2PasswordBearer`)
- [x] **6.** Controle de acesso baseado em perfis (`core/permissoes.py`) e restrição de dono
- [x] **7.** Padronização global de exceções e status codes (`core/exceptions.py`)
- [x] **8.** Configurações de deploy (`Dockerfile`, `Procfile`, `render.yaml`)
- [x] **9.** Suíte de testes automatizados com Pytest (`68` testes)

---

## 17. Testes Automatizados e Evidências

### 17.1 Cobertura da Suíte (Pytest)

**Status:** ✅ **68/68 testes aprovados (100% PASSED)** utilizando `FakeFirestore` (`tests/fake_firestore.py`) para isolar o banco de dados durante os testes.

| Arquivo | Cobertura |
| :--- | :--- |
| `tests/test_auth.py` | Login válido e inválido, `/usuarios/me`, tokens ausentes, inválidos, expirados e assinados com outra chave (`401` e `403`). |
| `tests/test_usuarios.py` | Cadastro público, hash de senha, e-mail duplicado, listagem sem expor senha, alteração de perfil e exclusão por Admin. |
| `tests/test_eventos.py` | Criação, listagem, edição e exclusão por perfil, data no passado, capacidade `<= 0` e bloqueio de exclusão com inscrições ativas. |
| `tests/test_inscricoes.py` | Inscrição, duplicidade, lotação máxima, evento inativo/inexistente, restrição de dono, cancelamento, exclusão e check-in (`presente`). |
| `tests/test_certificados.py` | Emissão por Admin/Organizador, bloqueio para participante, exigência de presença confirmada, bloqueio de duplicidade e exclusão. |

Para executar todos os testes:

```bash
pytest -v
```
