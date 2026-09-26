# 🎓 API de Gestão de Eventos Acadêmicos
> **Substituição de controles manuais por uma solução centralizada.**

⚠️ **Atenção:** Este documento trata do cenário de **EVENTOS ACADÊMICOS** — inscrições, submissão de artigos, comitê científico e certificados. Não deve ser confundido com o outro documento do grupo, sobre a API de gerenciamento de PROJETOS acadêmicos (cadastro de usuários, projetos, participantes e status). São dois cenários distintos.

**Síntese do problema:** A instituição precisa de uma API para gerenciar eventos acadêmicos, inscrições, usuários e emissão de certificados, substituindo controles manuais por uma solução centralizada.

---

## 1. Contexto do Problema

### 1.1 Qual problema o sistema resolve?
A organização de um evento acadêmico (congresso, simpósio, jornada científica) envolve vários processos que, quando feitos manualmente, ficam espalhados entre planilhas, e-mails e controles isolados de cada setor: inscrições, pagamento, submissão de artigos, avaliação pelo comitê científico, controle de presença e emissão de certificados. Isso gera retrabalho, atraso na comunicação entre setores e risco de erro por exemplo, emitir um certificado sem confirmar a frequência mínima, ou perder o controle de qual artigo já foi avaliado.

### 1.2 Quem vai usar?
A plataforma atende dois grupos: as equipes internas que organizam o evento e os participantes externos. Cada perfil tem acesso mapeado às suas próprias responsabilidades:

| Perfil | Papel no evento |
| :--- | :--- |
| **Participante** | Inscreve-se, submete artigos, faz check-in e emite certificados e recibos. |
| **Comitê Científico** | Avalia artigos em fluxo duplo-cego e define o status de aprovação. |
| **Marketing** | Criar cupons e campanhas, acompanhar a conversão de inscrições. |
| **Tecnologia / Logística** | Configura salas, check-in e suporte técnico durante o evento. |
| **Secretaria** | Confere dados cadastrais e presta atendimento aos participantes. |
| **Organizador** | Configura lotes, cupons, delega artigos e dispara certificados. |
| **Administrador da Plataforma** | Gerencia integrações globais, segurança e contas de organizadores de múltiplos eventos. |

### 1.3 Qual o objetivo da plataforma?
**Objetivo geral:** Centralizar, em uma solução única, o fluxo completo de um evento acadêmico inscrição, submissão e avaliação de trabalhos, controle de presença e emissão de certificados — aplicando de forma automática as regras de acesso de cada perfil, do participante ao administrador da plataforma.

**Critérios de aceitação**: o objetivo é considerado atingido quando o sistema permitir:
- [x] Inscrição, submissão e pagamento integrados em um único fluxo, sem controle manual paralelo;
- [x] Avaliação de artigos em duplo-cego, sem exposição de identidade entre autor e avaliador;
- [x] Emissão de certificado bloqueada automaticamente quando a frequência mínima não é atingida;
- [x] Verificação pública da autenticidade de qualquer certificado emitido.

### 1.4 Qual o escopo da primeira versão?
*   ✅ **Incluído na v1:** Inscrição com categorias de público e lotes financeiros; formulário de dados logísticos (acessibilidade e restrições alimentares); submissão de artigos integrada ao pagamento; avaliação duplo-cega pelo comitê científico; check-in por QR Code ou tempo de login; emissão de certificados com trava de frequência mínima e autenticação antifraude; perfis de Participante, Organizador e Administrador da Plataforma.
*   ❌ **Fora do escopo da v1:** Emissão automática de nota fiscal, aplicativo mobile dedicado, transmissão ao vivo nativa e interface multilíngue funcionalidades previstas para versões futuras.

### 1.5 Cadastro e gerenciamento de contas de usuário
Além de definir o que cada perfil pode fazer dentro do sistema, a plataforma também define como a conta de cada perfil é criada:
*   **Participante:** A conta é criada automaticamente no momento da inscrição, a partir dos dados preenchidos no formulário não exige cadastro prévio separado.
*   **Comitê Científico, Marketing, Tecnologia/Logística e Secretaria:** Contas internas criadas pelo Organizador do evento, já vinculadas ao perfil funcional correspondente.
*   **Organizador:** Conta criada pelo Administrador da Plataforma, que define o evento (ou eventos) sob sua responsabilidade.
*   **Administrador da Plataforma:** Perfil inicial criado na implantação do sistema; novos administradores só podem ser incluídos por um administrador já existente.

---

## 2. Estrutura de Setores
A plataforma substitui planilhas, e-mails avulsos e controles manuais por módulos integrados, cada um atendendo a um setor específico da organização do evento, com dados compartilhados em tempo real entre eles:

| Setor | Como a plataforma atende |
| :--- | :--- |
| **Coordenação Geral** | Painel executivo consolidado: número de inscritos por lote, receita acumulada, ocupação de salas e taxa de conversão. Aprova decisões estratégicas e delegue permissões de organizador. |
| **Comitê Científico** | Módulo de avaliação de artigos com fluxo duplo-cego: distribuição automática ou manual de submissões, registro de pareceres e notas, cálculo de status sem que autor e avaliador se identifiquem. |
| **Marketing** | Criação de cupons e campanhas promocionais, geração de páginas de divulgação, acompanhamento de métricas de conversão e integração com ferramentas externas. |
| **Tecnologia / Logística**| Configuração da infraestrutura do evento: capacidade de salas, check-in por QR Code, emissão de crachás, monitoramento em tempo real e suporte técnico. |
| **Secretaria** | Conferência de dados, emissão de recibos e comprovantes, atendimento a solicitações e suporte na emissão manual de documentos. |

> 💡 **Ponto central:** Nenhum setor opera de forma isolada. Uma inscrição atualiza o painel da Coordenação, uma aprovação do Comitê libera o certificado, e um check-in da Logística reflete na frequência da Secretaria.

---

## 3. Fluxo de Inscrições Online

### 3.1 Categorias de público
O sistema permite parametrizar categorias distintas (ex.: aluno, profissional, convidado, palestrante), cada uma com valor, cota de vagas e regras próprias de acesso às atividades.

### 3.2 Viradas de lote financeiro
Os lotes de preço são configurados com regras de virada automática, disparadas por data-limite ou por esgotamento de vagas. Ao atingir a condição, o sistema atualiza o valor cobrado nas próximas inscrições sem intervenção manual, mantendo o histórico de qual lote cada participante pagou.

### 3.3 Formulários de dados logísticos
O formulário de inscrição inclui campos configuráveis para necessidades de acessibilidade (cadeirante, intérprete de Libras, etc.) e restrições alimentares, informações repassadas automaticamente à Logística para o dimensionamento de recursos do evento.

### 3.4 Integração pagamento × submissão de trabalhos
A confirmação de pagamento e o módulo de submissão de artigos trabalham de forma integrada: a submissão pode ser configurada como condicionada à inscrição paga, ou seguir em trilha paralela até um prazo definido. Em qualquer caso, o status financeiro e o status da submissão ficam visíveis lado a lado.

---

## 4. Permissões e Restrições de Usuários (Participantes)
O participante padrão tem acesso mapeado apenas ao que envolve a sua própria inscrição e submissão:

| ✅ Pode fazer | ❌ Não pode fazer |
| :--- | :--- |
| • Realizar inscrição em categorias de público<br>• Anexar e submeter artigos científicos<br>• Acompanhar status de aprovação de submissão<br>• Fazer check-in nas atividades via QR Code<br>• Emitir recibos e comprovantes de inscrição | • Alterar documentos após o encerramento dos prazos<br>• Acessar notas e identidade de avaliadores<br>• Gerar certificado sem atingir a presença mínima |

*As travas de "não pode" são regras sistêmicas (ex: o formulário de artigo é bloqueado após o prazo e o botão de certificado só ativa com a frequência mínima).*

---

## 5. Permissões e Restrições de Gestão

### 5.1 Organizador
Tem controle operacional do evento, mas não tem acesso à camada estrutural.

| ✅ Pode fazer | ❌ Não pode fazer |
| :--- | :--- |
| • Configurar lotes de inscrição e datas<br>• Criar e gerenciar cupons de desconto<br>• Delegar artigos ao comitê científico<br>• Acessar listas completas de inscritos<br>• Disparar emissão de certificados | • Alterar taxas fixas cobradas pelo gateway<br>• Apagar logs de auditoria financeira<br>• Alterar o código-fonte da plataforma |

### 5.2 Administrador da Plataforma (Superusuário)
Opera a infraestrutura, mas segue restrições de conformidade.

| ✅ Pode fazer | ❌ Não pode fazer |
| :--- | :--- |
| • Gerenciar integrações globais (pagamento, analytics)<br>• Acessar logs de segurança e auditoria<br>• Gerenciar contas e permissões de organizadores<br>• Atuar em suporte técnico de nível 2 | • Visualizar dados sensíveis de cartão de crédito (PCI-DSS)<br>• Adulterar pareceres ou notas do comitê científico |

---

## 6. Emissão e Validação de Certificados

### 6.1 Controle de presença
A frequência é apurada por dois métodos:
*   **Presencial:** Check-in por meio da leitura de QR Code individual em cada atividade.
*   **On-line/híbrido:** Tempo de login registrado automaticamente na sessão, comparado com a duração total da atividade.

### 6.2 Trava de frequência mínima
O sistema soma a presença registrada em cada atividade e compara ao percentual mínimo configurado (ex: 75%). Abaixo do limite, a opção de emitir certificado permanece bloqueada automaticamente.

### 6.3 Geração dinâmica do documento
Uma vez liberado, o certificado é montado dinamicamente a partir de um *template*, preenchido com o nome do participante, carga horária, título das atividades e data, gerando um arquivo individual.

### 6.4 Autenticação antifraude
Cada certificado recebe um código hash único e um link/QR Code de verificação pública. Qualquer pessoa pode confirmar a autenticidade diretamente na base da plataforma, impedindo falsificações.
