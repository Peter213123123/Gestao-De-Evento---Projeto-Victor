# 📅 Gerenciador de Eventos Acadêmicos

API REST para centralizar a gestão de eventos acadêmicos: criação de eventos, controle de capacidade, inscrições e, futuramente, emissão automatizada de certificados.

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
7. [Contratos da API](#7-contratos-da-api)
8. [Status Codes](#8-status-codes)
9. [Padrão de Resposta e Erro](#9-padrão-de-resposta-e-erro)
10. [Matriz de Permissões](#10-matriz-de-permissões)
11. [Estrutura do Projeto](#11-estrutura-do-projeto)
12. [Tecnologias](#12-tecnologias)
13. [Persistência e Instalação / Execução](#13-persistência-e-instalação--execução)
14. [Backlog](#14-backlog)
15. [Critérios de Aceitação](#15-critérios-de-aceitação)
16. [Protótipo Inicial](#16-protótipo-inicial)
17. [Implementações Realizadas](#17-implementações-realizadas)
18. [Entregáveis e Evidências](#18-entregáveis-e-evidências)
19. [Melhorias de Arquitetura, Organização e Qualidade de Código](#19-melhorias-de-arquitetura-organização-e-qualidade-de-código)
20. [Principais Decisões Técnicas e Dificuldades Enfrentadas](#20-principais-decisões-técnicas-e-dificuldades-enfrentadas)
21. [Versionamento e Publicação em Produção (HTTPS)](#21-versionamento-e-publicação-em-produção-https)

---

## 1. Contexto do Problema

**Qual problema o sistema resolve?**
Hoje a gestão de eventos acadêmicos na instituição é manual e descentralizada (planilhas e formulários soltos), o que gera retrabalho, perda de dados, inscrições duplicadas e lentidão na emissão de certificados.

**Quem vai usar?**
Alunos (participantes), professores/coordenadores (organizadores) e a Secretaria/TI da instituição (administradores).

**Qual o objetivo da API?**
Centralizar todo o fluxo de eventos acadêmicos, desde a criação da atividade e o controle de capacidade até a gestão de inscrições e, no futuro, a emissão automatizada de certificados.

**Qual o escopo da primeira versão?**
O MVP (Minimum Viable Product) foca no CRUD de usuários, na criação de eventos e no processamento de inscrições, com persistência em banco de dados e documentação Swagger ativa.

---

## 2. Perfis de Usuário

| Perfil | Descrição |
| :--- | :--- |
| **Admin** | Controle total. Gerencia todos os usuários, eventos e configurações globais. |
| **Organizador** | Professores ou coordenadores. Criam, editam e gerenciam apenas os próprios eventos e listam os inscritos neles. |
| **Participante** | Alunos ou visitantes. Visualizam eventos disponíveis, realizam e cancelam a própria inscrição. |

---

## 3. Regras de Negócio

1. Um usuário não pode se inscrever duas vezes no mesmo evento.
2. Um evento não aceita novas inscrições se a capacidade máxima for atingida.
3. Não é permitido cadastrar um evento com `data_evento` no passado.
4. O e-mail de um usuário deve ser único em todo o sistema.
5. Um participante só pode cancelar a própria inscrição, sem alterar inscrições de terceiros.
6. Apenas usuários com perfil **Admin** ou **Organizador** podem criar novos eventos.
7. Um evento não pode ser excluído se houver inscrições vinculadas (deve ser inativado, ou as inscrições canceladas primeiro).
8. A senha do usuário não pode trafegar nem ser salva em texto plano (deve usar hash).
9. Inscrições só podem ser feitas em eventos com status **"ativo"**.
10. A emissão de certificado (escopo futuro) será bloqueada para participantes sem o status **"Presença Confirmada"**.

---

## 4. Entidades Principais

- **Usuário:** identifica quem acessa o sistema, permitindo autenticação e divisão de papéis.
- **Evento:** núcleo do sistema. Armazena as informações das atividades acadêmicas oferecidas.
- **Inscrição:** tabela associativa que conecta o usuário ao evento, registrando a data da inscrição e o status.

---

## 5. Modelo de Dados

**Relacionamentos (DER):**

- Usuário (1) — (N) Inscrição: um usuário pode ter várias inscrições.
- Evento (1) — (N) Inscrição: um evento pode ter várias inscrições.

**Estrutura relacional inicial:**

```text
usuarios   (id [PK], nome, email, senha_hash, tipo_perfil, criado_em)
eventos    (id [PK], titulo, descricao, data_evento, capacidade, status, organizador_id [FK -> usuarios.id])
inscricoes (id [PK], usuario_id [FK -> usuarios.id], evento_id [FK -> eventos.id], data_inscricao, status)
```

---

## 6. Dicionário de Dados

| Entidade | Campo | Tipo | Obrigatório | Regra / Restrição |
| :--- | :--- | :--- | :---: | :--- |
| Usuário | email | string | Sim | Único, formato de e-mail válido. |
| Usuário | tipo_perfil | string | Sim | Apenas: `admin`, `organizador`, `participante`. |
| Evento | capacidade | int | Sim | Deve ser maior que 0. |
| Evento | data_evento | date | Sim | Não pode ser menor que a data atual. |
| Evento | status | string | Sim | Apenas: `ativo`, `concluido`, `cancelado`. |
| Inscrição | status | string | Sim | Apenas: `confirmada`, `cancelada`, `presente`. |

---

## 7. Contratos da API

### `POST /api/v1/usuarios` — Criação de usuário

**Request:**

```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "senhaforte123"
}
```

> **Nota:** o perfil não é enviado no cadastro. Todo cadastro público cria um `participante`; somente um Admin altera o perfil.

**Response `201 Created`:**

```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "tipo_perfil": "participante",
  "criado_em": "2026-09-24T10:00:00"
}
```

> **Nota:** a senha nunca retorna no payload de saída.

---

## 8. Status Codes

| Situação | Status HTTP |
| :--- | :--- |
| Registro criado com sucesso (usuário, evento, inscrição) | `201 Created` |
| Consulta realizada com sucesso (listagens) | `200 OK` |
| Exclusão realizada com sucesso | `204 No Content` |
| Erro de validação de dados (Pydantic/Schema) | `422 Unprocessable Entity` |
| Registro não encontrado (ex.: ID inexistente) | `404 Not Found` |
| Erro de regra de negócio (ex.: evento lotado) | `400 Bad Request` |
| Usuário não autenticado (falta de token) | `401 Unauthorized` |
| Sem permissão (ex.: participante tentando criar evento) | `403 Forbidden` |

---

## 9. Padrão de Resposta e Erro

Foi adotado um envelope padrão para que o front-end saiba exatamente como ler as respostas.

**Exemplo de erro de regra de negócio (`400`):**

```json
{
  "success": false,
  "error": "CapacidadeMaximaAtingida",
  "message": "Não é possível realizar a inscrição. O evento atingiu sua capacidade máxima."
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
| `DELETE /api/v1/eventos/{id}` | 🔒 | ✅ | ❌ | ❌ | — |
| `POST /api/v1/inscricoes/` | 🔒 | ❌ | ❌ | ✅ | O `id_usuario` precisa ser o do token |
| `GET /api/v1/inscricoes/` | 🔒 | ✅ | ✅ | ❌ | Lista os inscritos |
| `PUT /api/v1/inscricoes/{id}` (`cancelada`) | 🔒 | ❌ | ❌ | ✅ | Somente a própria inscrição |
| `PUT /api/v1/inscricoes/{id}` (`presente`) | 🔒 | ✅ | ✅ | ❌ | Registro de presença (check-in) com emissão e envio automático do certificado |
| `DELETE /api/v1/inscricoes/{id}` | 🔒 | ❌ | ❌ | ✅ | Somente a própria inscrição |
| `GET /api/v1/certificados/` | 🔒 | ✅ | ✅ | ✅ | — |
| `POST /api/v1/certificados/` | 🔒 | ✅ | ✅ | ❌ | Emite certificado e envia PDF/JPG por e-mail |
| `POST /api/v1/certificados/{id}/reenviar` | 🔒 | ✅ | ✅ | ❌ | Reenvia o certificado por e-mail ao participante |
| `DELETE /api/v1/certificados/{id}` | 🔒 | ✅ | ✅ | ❌ | — |

### 10.3 Erros de acesso

| Situação | Status |
| :--- | :---: |
| Sem token, token inválido ou token expirado | `401 Unauthorized` |
| Token válido, mas o perfil não tem permissão para a ação | `403 Forbidden` |
| Token válido, perfil correto, mas o recurso pertence a outro usuário | `403 Forbidden` |

### 10.4 Como a matriz está no código

- Os três perfis (`admin`, `organizador`, `participante`) e a matriz ficam em `core/permissoes.py`, no dicionário `MATRIZ` (ação → perfis autorizados).
- Cada endpoint declara a ação com `Depends(permissao("nome_da_acao"))`. Para mudar uma permissão, edita-se somente o `MATRIZ`.
- O perfil `tipo_perfil` é validado em `schemas/usuario_schema.py` (`Perfil`) e em `models/usuario.py`.

### 10.5 Como criar o primeiro Admin

O cadastro público cria apenas participantes. Para criar o primeiro admin:

1. Cadastre o usuário normalmente em `POST /api/v1/usuarios/`.
2. No console do Firebase, abra o Firestore, coleção `usuarios`, e altere o campo `tipo_perfil` desse documento para `admin`.
3. Faça login de novo (o perfil fica gravado no token).

Depois disso, o admin promove organizadores por `PATCH /api/v1/usuarios/{id}/perfil` com o corpo `{"tipo_perfil": "organizador"}`.

---

## 11. Estrutura do Projeto

Organizada em camadas com separação de responsabilidades:

```text
.
├── api/
│   ├── api.py                        # Agregador dos routers da v1
│   └── v1/
│       └── routers/
│           ├── usuarios.py           # Cadastro, login OAuth2/JWT, /me e gestão de perfis
│           ├── eventos.py            # CRUD de eventos acadêmicos
│           ├── inscricoes.py         # Inscrições, check-in e emissão automática de certificado
│           └── certificados.py       # Emissão, listagem, reenvio por e-mail e exclusão
├── core/
│   ├── auth.py                       # Validação de token JWT (OAuth2PasswordBearer)
│   ├── config.py                     # Carregamento de variáveis de ambiente (.env)
│   ├── database.py                   # Inicialização do Firebase Admin + Cloud Firestore
│   ├── email_service.py              # Envio SMTP transacional e certificado PDF/JPG (Pillow)
│   ├── exceptions.py                 # Handlers globais de resposta de erro padronizada
│   ├── permissoes.py                 # Matriz centralizada de permissões RBAC (MATRIZ)
│   └── security.py                   # Hash bcrypt (Passlib) e criação de tokens JWT
├── models/                           # Representações de domínio (usuário, evento, inscrição)
├── schemas/                          # Schemas Pydantic de entrada e saída
├── static/
│   ├── login.html                    # Tela de autenticação e cadastro público
│   ├── dashboard.html                # Painel web administrativo e de participantes
│   └── certificado_modelo.jpg        # Modelo visual oficial do certificado
├── tests/                            # Suíte automatizada com Pytest e FakeFirestore
│   ├── conftest.py
│   ├── fake_firestore.py
│   ├── test_auth.py
│   ├── test_certificados.py
│   ├── test_eventos.py
│   ├── test_inscricoes.py
│   └── test_usuarios.py
├── main.py                           # Instância FastAPI, Swagger/OpenAPI e arquivos estáticos
├── Dockerfile                        # Imagem Docker pronta para produção
├── Procfile                          # Comando de inicialização web
├── render.yaml                       # Blueprint de deploy no Render
├── pytest.ini                        # Configuração da suíte de testes
└── requirements.txt                  # Dependências Python
```

---

## 12. Tecnologias

| Tecnologia | Uso no projeto |
| :--- | :--- |
| **Python 3 / FastAPI** | Construção da API REST com tipagem estática, alta performance e Swagger/OpenAPI 3.1 automático. |
| **Uvicorn** | Servidor ASGI para execução local e em produção. |
| **Google Cloud Firestore** | Banco de dados NoSQL em nuvem (`firebase-admin`), garantindo persistência real fora do container. |
| **Pydantic / pydantic-settings** | Validação rigorosa de entrada/saída e leitura tipada de configurações. |
| **PyJWT** | Geração e verificação de tokens JWT (`HS256`) com expiração configurável (`exp`). |
| **Passlib + Bcrypt** | Hashing seguro de senhas antes da persistência no banco. |
| **Pillow + smtplib** | Preenchimento dinâmico do modelo de certificado em PDF/JPG e envio por e-mail via SMTP. |
| **Pytest + HTTPX** | Suíte de testes automatizados cobrindo autenticação, RBAC, CRUDs e regras de negócio. |
| **Docker / Render** | Empacotamento e configuração para publicação em ambiente HTTPS. |

---

## 13. Persistência e Instalação / Execução

### 13.1 Persistência em Nuvem (Cloud Firestore)

A aplicação utiliza **Cloud Firestore** (coleções `usuarios`, `eventos`, `inscricoes` e `certificados`). As credenciais são carregadas por `core/database.py` a partir de uma das três fontes (em ordem de prioridade):

1. `FIREBASE_CREDENTIALS_JSON` — conteúdo JSON completo da conta de serviço (ideal para Render/cloud).
2. `FIREBASE_CREDENTIALS_BASE64` — JSON codificado em Base64.
3. `FIREBASE_CREDENTIALS_PATH` — caminho local para o arquivo `firebase.json`.

### 13.2 Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto (nunca versionado no Git):

```env
SECRET_KEY="sua-chave-secreta-forte"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
FIREBASE_CREDENTIALS_PATH="firebase.json"

# Opcional: envio de e-mails transacionais (confirmação e certificado)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="seu-email@gmail.com"
SMTP_PASSWORD="sua-senha-de-app"
SMTP_FROM_EMAIL="seu-email@gmail.com"
SMTP_FROM_NAME="Gestão de Eventos Acadêmicos"
SMTP_USE_TLS=true
```

### 13.3 Execução Local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- **Painel Web:** `http://127.0.0.1:8000/login` e `http://127.0.0.1:8000/dashboard`
- **Swagger / OpenAPI:** `http://127.0.0.1:8000/docs`
- **Healthcheck:** `http://127.0.0.1:8000/health`

### 13.4 Execução via Docker

```bash
docker build -t eventos-api .
docker run -p 8000:8000 --env-file .env eventos-api
```

### 13.5 Execução dos Testes Automatizados

Os testes utilizam `FakeFirestore` em memória (`tests/conftest.py`), dispensando credenciais reais do Firebase durante a execução:

```bash
pytest -v
```

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
| US09 | Como admin, quero inativar um evento que foi cancelado pela instituição. | Baixa |
| US10 | Como organizador, quero dar "check-in" na presença dos inscritos. | Baixa (V2) |

---

## 15. Critérios de Aceitação

### Cadastro de Evento (US03)

1. O sistema deve exigir título, data e capacidade.
2. A data do evento não pode ser salva se for anterior ao dia de hoje.
3. A capacidade deve ser um número inteiro maior que 0.
4. O sistema deve atribuir automaticamente o status `ativo` na criação.
5. O sistema deve retornar `201 Created` em caso de sucesso.

### Inscrição em Evento (US06)

1. O sistema deve vincular o ID do participante logado ao ID do evento.
2. O sistema deve rejeitar a inscrição e retornar `400` se a capacidade máxima já foi atingida.
3. O sistema deve rejeitar a inscrição se o participante já estiver inscrito no mesmo evento.
4. O sistema deve retornar `201 Created` e os dados da inscrição (data e hora).
5. Se o ID do evento fornecido não existir, o sistema deve retornar `404 Not Found`.

---

## 16. Protótipo Inicial

O MVP técnico já possui:

- [x] Projeto FastAPI configurado e rodando localmente na porta `8000`.
- [x] Documentação interativa Swagger (OAS 3.1) na rota `/docs`.
- [x] Rotas estruturadas e modularizadas (ex.: `/api/v1/usuarios/`, `/api/v1/eventos/`).
- [x] Schemas de validação Pydantic aplicados (ex.: body do POST de usuários).

---

## 17. Implementações Realizadas

- [x] **1.** Configuração inicial e infraestrutura do Firebase
- [x] **2.** Conexão e configuração do Firestore na API
- [x] **3.** Refatoração dos models e schemas
- [x] **4.** Adaptação dos CRUDs existentes (eventos e inscrições)
- [x] **5.** Segurança e criptografia (hashing)
- [x] **6.** Mecanismo de autenticação e JWT
- [x] **7.** Rotas de usuário (cadastro e login)
- [x] **8.** Proteção de rotas, revisão e evidências
- [x] **9.** Perfis de usuário e matriz de permissões aplicada aos endpoints (`core/permissoes.py`)
- [x] **10.** Módulo completo de Certificados (emissão manual, automática no check-in e reenvio por e-mail)
- [x] **11.** Envio transacional por SMTP com certificado personalizado em PDF/JPG (`core/email_service.py`)
- [x] **12.** Painel web completo (`static/login.html` e `static/dashboard.html`) e preparação para deploy (`render.yaml`, `Dockerfile`, `Procfile`)

## 18. Entregáveis e Evidências

### 18.1 Autenticação e Segurança (`401` / `403`)

**Status:** ✅ Concluído e testado.

O sistema valida tokens JWT, rejeita acessos sem autenticação com `401 Unauthorized` e bloqueia acessos indevidos por perfil com `403 Forbidden`.

**Evidência:** `tests/test_auth.py`.

### 18.2 Controle de Acesso Baseado em Perfis (RBAC)

**Status:** ✅ Concluído e testado.

Matriz de permissões separada entre `admin`, `organizador` e `participante`, implementada na API e coberta pelos testes automatizados de usuários, eventos e certificados.

### 18.3 Restrição de Recursos Próprios

**Status:** ✅ Concluído e testado.

Validação de propriedade ativa na rota de inscrições (`api/v1/routers/inscricoes.py`): o participante só consegue criar, cancelar ou excluir as **próprias** inscrições, sob pena de `403 Forbidden`.

### 18.4 Testes Automatizados (Pytest)

**Status:** ✅ Concluído — **75/75 testes aprovados (100% PASSED)**.

| Arquivo | Quantidade | Cobertura |
| :--- | :---: | :--- |
| `tests/test_auth.py` | 10 | Login válido, falhas de credencial (`401`), tokens expirados/inválidos, perfil proibido (`403`) e `/usuarios/me`. |
| `tests/test_eventos.py` | 16 | Criação, listagem, edição (com validação de título/status) e exclusão por perfil; bloqueio de data passada, capacidade `<= 0` e evento com inscritos. |
| `tests/test_inscricoes.py` | 22 | Regras de capacidade, duplicidade, dono do recurso, cancelamento, check-in (`presente`) e emissão automática de certificado. |
| `tests/test_certificados.py` | 12 | Emissão por Admin/Organizador, presença obrigatória, duplicidade, reenvio SMTP mockado e geração PDF/JPG com `Pillow`. |
| `tests/test_usuarios.py` | 15 | Cadastro público sempre `participante`, normalização de e-mail, hash bcrypt, e-mail único, alteração de perfil e exclusão restrita a Admin. |

Para executar:

```bash
pytest -v
```

### 18.5 Sincronização do Repositório (Git & GitHub)

**Status:** ✅ Concluído e atualizado (`main`, `SMTP`, `deploy-render` e tag `v2.0.0`).

---

## 19. Melhorias de Arquitetura, Organização e Qualidade de Código

1. **Matriz Centralizada de Permissões RBAC (`core/permissoes.py`):**
   Política de autorização concentrada no dicionário `MATRIZ` e aplicada declarativamente nas rotas via `Depends(permissao("nome_da_acao"))`, eliminando verificações duplicadas nos endpoints.
2. **Padronização Global de Erros (`core/exceptions.py` + `main.py`):**
   Handlers globais para `HTTPException`, `RequestValidationError` e `Exception`, garantindo que toda falha (`400`, `401`, `403`, `404`, `422`, `500`) siga o mesmo envelope JSON (`success`, `error`, `message`).
3. **Carregamento Flexível de Credenciais Firebase (`core/database.py`):**
   Suporte automático a `FIREBASE_CREDENTIALS_JSON`, `FIREBASE_CREDENTIALS_BASE64` e `FIREBASE_CREDENTIALS_PATH`, permitindo rodar localmente com arquivo e na nuvem (Render/Docker) via variáveis de ambiente sem versionar segredos.
4. **Serviço Desacoplado de E-mail e Certificados (`core/email_service.py`):**
   Envio assíncrono em `BackgroundTasks` com geração dinâmica de PDF/JPG sobre o modelo oficial (`Pillow`) e fallback seguro quando o SMTP não está configurado.

---

## 20. Principais Decisões Técnicas e Dificuldades Enfrentadas

### Decisões Técnicas
- **Migração para Cloud Firestore:** garante persistência real em nuvem independente de containers efêmeros (como no plano gratuito do Render), substituindo bancos locais em arquivo.
- **Cadastro público restrito a `participante`:** removeu-se a escolha de perfil da tela pública (`/login`), deixando a promoção para `organizador` ou `admin` exclusiva ao Administrador autenticado via `PATCH /api/v1/usuarios/{id}/perfil`.
- **SMTP com `BackgroundTasks` + `Pillow`:** evita dependência de plano pago no Firebase (Blaze/Cloud Functions) para disparo de e-mails e permite gerar o certificado personalizado na própria API.
- **Testes desacoplados com `FakeFirestore`:** permite validar todos os 73 cenários da API rapidamente e sem acesso à rede ou credenciais de produção.

### Dificuldades Enfrentadas
- **Compatibilidade `passlib` + `bcrypt`:** versões mais novas do pacote `bcrypt` causavam erro de leitura de atributo interno com `passlib`; resolvido fixando `bcrypt==4.0.1` no `requirements.txt`.
- **Credenciais do Firebase em Deploy Cloud:** a leitura exclusiva de `firebase.json` dificultava o deploy sem expor chaves no Git; resolvido com suporte a JSON/Base64 em variável de ambiente.
- **Consistência entre respostas de erro e front-end:** a padronização para `{"success": false, "error": ..., "message": ...}` exigiu atualizar o painel (`static/dashboard.html`) para ler `data.message || data.detail`, ajustar `z-index` dos toasts acima dos modais e incluir `carga_horaria` na emissão automática de certificados no check-in.

---

## 21. Versionamento e Publicação em Produção (HTTPS)

- **Repositório:** `https://github.com/Peter213123123/Gestao-De-Evento---Projeto-Victor.git`
- **Branches principais:** `main` (versão final integrada), `SMTP` e `deploy-render`.
- **Tag da versão entregue:** `v2.0.0`.
- **Deploy (Render):** configurado via `render.yaml` (`uvicorn main:app --host 0.0.0.0 --port $PORT`). No painel do Render, configure as variáveis `FIREBASE_CREDENTIALS_JSON`, `SECRET_KEY` e as variáveis `SMTP_*` para manter persistência real no Firestore e envio de e-mails ativo em HTTPS.
