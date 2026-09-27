Aslley Emanuel Da Costa Mariano - 01878630
Edson Rodrigues Cardoso Dos Santos - 01351404
Fábio Luis Damasceno da Silva - 012212500
João Paulo Romão Sampaio de Melo - 01871330
Pedro Felipe Santiago Neto - 01891949
Sandrielly Maria Farias da Silva Alves Bezerra - 01904552
Caio Victor Barbosa Monteiro - 01882905
# Gerenciador de Eventos Acadêmicos
---

1. Contexto do Problema

    Qual problema o sistema resolve? Atualmente, a gestão de eventos acadêmicos na instituição é feita de forma manual e descentralizada (planilhas, formulários soltos), o que gera retrabalho, perda de dados, inscrições duplicadas e lentidão na emissão de certificados.

    Quem vai usar? Alunos (participantes), Professores/Coordenadores (organizadores) e a Secretaria/TI da instituição (administradores).

    Qual o objetivo da API? Centralizar todo o fluxo de eventos acadêmicos, desde a criação da atividade e controle de capacidade, até a gestão de inscrições e, no futuro, a emissão automatizada de certificados.

    Qual o escopo da primeira versão? O MVP (Minimum Viable Product) focará no CRUD de Usuários, criação de Eventos e processamento de Inscrições, com persistência em banco de dados e documentação Swagger ativa.

2. Definição dos Perfis de Usuário
Perfil	Descrição
Admin	Possui controle total. Gerencia todos os usuários, eventos do sistema e configurações globais.
Organizador	Professores ou coordenadores. Podem criar, editar e gerenciar apenas os próprios eventos e listar os inscritos neles.
Participante	Alunos ou visitantes. Podem visualizar eventos disponíveis, realizar e cancelar a própria inscrição.
3. Regras de Negócio

(10 regras essenciais para o funcionamento do sistema)

    Um usuário não pode se inscrever duas vezes no mesmo evento.

    Um evento não pode aceitar novas inscrições se a capacidade_maxima for atingida.

    Não é permitido o cadastro de um evento com data_evento no passado.

    O e-mail de um usuário deve ser único em todo o sistema.

    Um participante só pode cancelar a sua própria inscrição; ele não pode alterar inscrições de terceiros.

    Apenas usuários com perfil "Admin" ou "Organizador" podem criar novos eventos.

    Um evento não pode ser excluído se já houver inscrições vinculadas a ele (deve ser inativado ou as inscrições canceladas primeiro).

    A senha do usuário não pode trafegar ou ser salva em texto plano (deve utilizar hash).

    Inscrições só podem ser realizadas em eventos que estejam com o status "Ativo".

    A emissão de certificado (escopo futuro) será bloqueada para participantes que não tiverem o status de "Presença Confirmada".

4. Entidades Principais do Sistema

    Usuário: Necessário para identificar quem está acessando o sistema, permitindo autenticação e divisão de papéis.

    Evento: O núcleo do sistema. Armazena as informações das atividades acadêmicas oferecidas.

    Inscrição: Tabela intermediária (tabela associativa) que conecta o Usuário ao Evento, registrando a data da inscrição e o status.

5. Modelo de Dados / DER

    Usuário (1) --- (N) Inscrição (Um usuário pode ter várias inscrições).

    Evento (1) --- (N) Inscrição (Um evento pode ter várias inscrições).

Estrutura Relacional Inicial:

    usuarios (id [PK], nome, email, senha_hash, tipo_perfil, criado_em)

    eventos (id [PK], titulo, descricao, data_evento, capacidade, status, organizador_id [FK -> usuarios.id])

    inscricoes (id [PK], usuario_id [FK -> usuarios.id], evento_id [FK -> eventos.id], data_inscricao, status)

6. Dicionário de Dados
Entidade	Campo	Tipo	Obrigatório	Regra / Restrição
Usuário	email	string	Sim	Único, formato de e-mail válido.
Usuário	tipo_perfil	string	Sim	Apenas: "admin", "organizador", "participante".
Evento	capacidade	int	Sim	Deve ser maior que 0.
Evento	data_evento	date	Sim	Não pode ser menor que a data atual.
Evento	status	string	Sim	Apenas: "ativo", "concluido", "cancelado".
Inscrição	status	string	Sim	Apenas: "confirmada", "cancelada", "presente".
7. Contratos de Entrada e Saída da API

POST /api/v1/usuarios (Criação de Usuário)
Entrada (Request):
JSON

{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "senhaforte123",
  "tipo_perfil": "participante"
}

Saída (Response 201):
JSON

{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "tipo_perfil": "participante",
  "criado_em": "2026-09-24T10:00:00"
}

(Nota: A senha nunca retorna no payload de saída).
8. Definição dos Status Codes
Situação	Status HTTP
Registro criado com sucesso (Usuário, Evento, Inscrição)	201 Created
Consulta realizada com sucesso (Listagens)	200 OK
Exclusão realizada com sucesso	204 No Content
Erro de validação de dados (Pydantic/Schema)	422 Unprocessable Entity
Registro não encontrado (ex: buscar ID inexistente)	404 Not Found
Erro de regra de negócio (ex: evento lotado)	400 Bad Request
Usuário não autenticado (Falta de token)	401 Unauthorized
Sem permissão (ex: Participante tentando criar evento)	403 Forbidden
9. Padrão de Resposta e Erro

Foi adotado um envelope padrão para garantir que o front-end saiba exatamente como ler as respostas.

Exemplo de Erro (Regra de Negócio / 400):
JSON

{
  "success": false,
  "error": "CapacidadeMaximaAtingida",
  "message": "Não é possível realizar a inscrição. O evento atingiu sua capacidade máxima."
}

10. Matriz de Permissões
Funcionalidade	Admin	Organizador	Participante
Criar/Editar Eventos	Sim	Sim	Não
Excluir Eventos	Sim	Não	Não
Listar Eventos	Sim	Sim	Sim
Inscrever-se em Eventos	Não	Não	Sim
Listar Inscritos no Evento	Sim	Sim	Não
Cancelar Inscrição (Própria)	Não	Não	Sim
11. Estrutura Inicial do Projeto

Organizada para escalabilidade, separando responsabilidades:
Plaintext

app/
├── api/
│   └── v1/
│       ├── routers/
│       │   ├── usuarios.py
│       │   ├── eventos.py
│       │   └── inscricoes.py
├── core/
│   ├── config.py (Variáveis de ambiente)
│   └── database.py (Conexão e Sessão)
├── models/ (Classes SQLAlchemy)
├── schemas/ (Classes Pydantic para I/O)
└── main.py (Instância do FastAPI)

12. Tecnologias Escolhidas e Justificativa
Tecnologia	Uso no projeto
Python 3 / FastAPI	Construção da API REST. Escolhido pela alta performance, tipagem estática e geração automática do Swagger.
SQLite / SQL Server	SQLite será usado no MVP para desenvolvimento rápido. A arquitetura permitirá migração fácil para SQL Server em produção.
SQLAlchemy	Mapeamento ORM, evitando queries manuais e protegendo contra SQL Injection.
Alembic	Controle de versão do banco de dados (Migrations), garantindo que a equipe mantenha o esquema sincronizado.
Pydantic	Validação rigorosa dos dados de entrada e saída, retornando erros claros caso o usuário envie JSON inválido.
13. Estratégia de Banco e Migrations

    Banco MVP: SQLite (arquivo local).

    Migrations: Controladas via Alembic.

    Comando inicial utilizado:
    alembic init alembic
    alembic revision --autogenerate -m "criacao_tabelas_iniciais_usuario_evento_inscricao"
    alembic upgrade head

14. Backlog do Projeto
ID	História de Usuário (User Story)	Prioridade
US01	Como usuário, quero me cadastrar no sistema para poder acessá-lo.	Alta
US02	Como administrador, quero visualizar todos os usuários cadastrados.	Média
US03	Como organizador, quero criar um evento definindo data e limite de vagas.	Alta
US04	Como organizador, quero editar as informações de um evento criado por mim.	Média
US05	Como participante, quero listar todos os eventos ativos para escolher qual participar.	Alta
US06	Como participante, quero me inscrever em um evento específico.	Alta
US07	Como participante, quero cancelar minha inscrição caso eu desista.	Média
US08	Como organizador, quero listar todos os participantes inscritos no meu evento.	Alta
US09	Como admin, quero inativar um evento que foi cancelado pela instituição.	Baixa
US10	Como organizador, quero dar "check-in" na presença dos inscritos.	Baixa (V2)
15. Critérios de Aceitação

Funcionalidades principais

Para Cadastro de Evento (US03):

    O sistema deve exigir título, data e capacidade.

    A data do evento não pode ser salva se for anterior ao dia de hoje.

    A capacidade deve ser um número inteiro maior que 0.

    O sistema deve atribuir automaticamente o status "ativo" na criação.

    O sistema deve retornar status 201 Created em caso de sucesso.

Para Inscrição em Evento (US06):
6. O sistema deve vincular o ID do participante logado ao ID do evento.
7. O sistema deve rejeitar a inscrição e retornar erro 400 se a capacidade máxima já foi atingida.
8. O sistema deve rejeitar a inscrição se o participante já estiver inscrito no mesmo evento.
9. O sistema deve retornar status 201 Created e os dados da inscrição (data e hora).
10. Se o ID do evento fornecido não existir, o sistema deve retornar 404 Not Found.
16. Protótipo Inicial da API

 O MVP técnico inicial já possui:

    Projeto FastAPI configurado e rodando localmente na porta 8000.

    Documentação interativa Swagger (OAS 3.1) operando na rota /docs.

    Rotas estruturadas e modularizadas (ex: /api/v1/usuarios/, /api/v1/eventos/).

    Schemas de validação Pydantic aplicados (ex: validando o body da requisição POST de usuários).
