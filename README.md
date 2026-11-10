# 📅 Gerenciador de Eventos Acadêmicos

API REST para centralizar a gestão de eventos acadêmicos: criação de eventos, controle de capacidade, inscrições e, futuramente, emissão automatizada de certificados.

![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
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
13. [Banco de Dados e Migrations](#13-banco-de-dados-e-migrations)
14. [Backlog](#14-backlog)
15. [Critérios de Aceitação](#15-critérios-de-aceitação)
16. [Protótipo Inicial](#16-protótipo-inicial)
17. [Implementações Realizadas](#17-implementações-realizadas)

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
  "senha": "senhaforte123",
  "tipo_perfil": "participante"
}
```

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

| Funcionalidade | Admin | Organizador | Participante |
| :--- | :---: | :---: | :---: |
| Criar/Editar eventos | ✅ | ✅ | ✅ |
| Excluir eventos | ✅ | ✅  | ✅  |
| Listar eventos | ✅ | ✅ | ✅ |
| Inscrever-se em eventos | ✅  |✅  | ✅ |
| Listar inscritos no evento | ✅ | ✅ | ✅ |
| Cancelar inscrição (própria) | ✅  |✅  | ✅ |

---

## 11. Estrutura do Projeto

Organizada para escalabilidade, separando responsabilidades:

```text
app/
├── api/
│   └── v1/
│       └── routers/
│           ├── usuarios.py
│           ├── eventos.py
│           └── inscricoes.py
├── core/
│   ├── config.py        # Variáveis de ambiente
│   └── database.py      # Conexão e sessão
├── models/              # Classes SQLAlchemy
├── schemas/             # Classes Pydantic (entrada/saída)
└── main.py              # Instância do FastAPI
```

---

## 12. Tecnologias

| Tecnologia | Uso no projeto |
| :--- | :--- |
| **Python 3 / FastAPI** | Construção da API REST. Alta performance, tipagem estática e Swagger automático. |
| **SQLite / SQL Server** | SQLite no MVP para desenvolvimento rápido; a arquitetura permite migração fácil para SQL Server em produção. |
| **SQLAlchemy** | ORM, evitando queries manuais e protegendo contra SQL Injection. |
| **Alembic** | Versionamento do banco (migrations), mantendo o esquema sincronizado na equipe. |
| **Pydantic** | Validação rigorosa de entrada e saída, com erros claros para JSON inválido. |

---

## 13. Banco de Dados e Migrations

- **Banco do MVP:** SQLite (arquivo local).
- **Migrations:** controladas via Alembic.

Comandos iniciais utilizados:

```bash
alembic init alembic
alembic revision --autogenerate -m "criacao_tabelas_iniciais_usuario_evento_inscricao"
alembic upgrade head
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
