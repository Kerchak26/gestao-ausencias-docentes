# Fase 1 — Levantamento e requisitos

> Documento de especificação de requisitos. Versão inicial elaborada a partir da proposta da demanda; deve ser revisada após as entrevistas com a secretaria e os coordenadores (ver seção 6).

## 1. Stakeholders

| Papel | Interesse no módulo |
|---|---|
| Secretaria de coordenação | Registrar faltas rapidamente, encontrar substituto no mesmo dia, guardar atestados |
| Coordenador acadêmico | Acompanhar indicadores, preparar reuniões com professores, cobrar reposições |
| Professor | Enviar atestados e comprovantes de reposição pelo celular, consultar seu histórico |
| Alunos (indiretos) | Menos aulas vagas, carga horária cumprida |
| Orientadores do projeto | Acompanhar entregas e validar o resultado |

## 2. Processo atual (AS-IS)

1. O professor avisa a falta (WhatsApp, e-mail, telefone ou nem avisa).
2. A secretaria anota em planilha ou caderno.
3. A secretaria liga ou manda mensagem para professores que talvez estejam livres.
4. Se ninguém assume, a turma fica sem aula e o registro muitas vezes se perde.
5. Atestados chegam em papel ou foto e ficam em pastas ou no celular de alguém.
6. Para reuniões, o coordenador monta o histórico manualmente.

**Pontos de melhoria identificados**

| Problema | Consequência | Como o módulo resolve |
|---|---|---|
| Registro em planilha/caderno | Retrabalho, perda de informação | Lançamento único com dados da grade (RF01) |
| Busca de substituto por telefone | Atraso, aula perdida | Lista automática de disponíveis (RF03) |
| Não se sabe quais aulas ficaram vagas | Carga horária não cumprida | Classificação automática (RF04) |
| Atestados em papel | Extravio, falta de evidência | Upload e aprovação digital (RF05) |
| Relatórios manuais | Tempo do coordenador | Dashboard e PDF (RF08, RF09) |

## 3. Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF01 | Registrar ausência com professor, disciplina, turma, data, horário e motivo | Alta |
| RF02 | Registrar várias ausências do dia a partir da grade horária | Alta |
| RF03 | Sugerir substitutos disponíveis no horário e atribuir substituto | Alta |
| RF04 | Classificar automaticamente as aulas afetadas (substituída, aguardando, reposição agendada, reposta, vaga) | Alta |
| RF05 | Anexar atestados e declarações (PDF/JPG/PNG) à ausência | Alta |
| RF06 | Aprovar ou recusar documentos enviados | Média |
| RF07 | Agendar reposições e registrar sua realização, com envio de comprovante pelo professor | Alta |
| RF08 | Dashboard com indicadores e filtros por período, professor e turma | Alta |
| RF09 | Gerar relatório em PDF com histórico de ausências e reposições | Alta |
| RF10 | Professor consulta suas ausências e envia documentos | Média |
| RF11 | Manter histórico (auditoria) de todas as ações por ausência | Média |
| RF12 | Cadastrar professores, disciplinas, turmas e grade; importar grade via CSV | Média |
| RF13 | Disponibilizar API de consulta para integração com o sistema da instituição | Baixa |

## 4. Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF01 | Interface responsiva, utilizável em celulares a partir de 360 px de largura |
| RNF02 | Acesso autenticado; permissões por perfil (secretaria, coordenador, professor) |
| RNF03 | Professor só acessa as próprias ausências e documentos |
| RNF04 | Anexos limitados a PDF/JPG/PNG de até 5 MB, armazenados com nome aleatório |
| RNF05 | Lançamento de uma ausência em até 3 cliques a partir da grade do dia |
| RNF06 | Páginas devem responder em menos de 2 s com até 10 mil ausências |
| RNF07 | Código documentado, com testes automatizados executados a cada push |
| RNF08 | Banco trocável (SQLite em desenvolvimento, PostgreSQL/MySQL em produção) |
| RNF09 | Conformidade com a LGPD: atestados são dados sensíveis de saúde, acesso restrito à gestão e ao próprio professor |

## 5. Regras de negócio

- **RN01** Não pode haver duas ausências do mesmo professor em horários sobrepostos no mesmo dia.
- **RN02** Um professor é sugerido como substituto somente se estiver ativo, sem aula na grade, sem ausência e sem outra substituição no mesmo horário.
- **RN03** Na lista de substitutos, quem leciona a mesma disciplina aparece primeiro; depois, quem fez menos substituições no mês.
- **RN04** A ausência é considerada *justificada* quando tem atestado ou declaração aprovados.
- **RN05** Aprovar o comprovante de uma reposição marca a reposição como realizada.
- **RN06** Toda ação relevante (lançamento, substituição, documento, reposição, exclusão) é registrada no histórico com usuário e data.

## 6. Roteiro de entrevistas (a aplicar)

**Secretaria**
1. Como você fica sabendo de uma falta? Com quanta antecedência?
2. Como registra hoje? Quanto tempo leva por falta?
3. Como encontra um substituto? Quais critérios usa?
4. O que acontece quando não há substituto?
5. Como recebe e guarda atestados? Já houve perda?
6. Quais informações a coordenação pede com mais frequência?

**Coordenação**
1. Quais indicadores são importantes nas reuniões com professores?
2. Com que frequência precisa de relatórios? Em que formato?
3. Qual o fluxo esperado para reposições?
4. Quem pode aprovar atestados?

**Registro das entrevistas:** anotar data, entrevistado e respostas em `docs/entrevistas/` e atualizar este documento.

## 7. Validação

| Data | Participantes | Resultado |
|---|---|---|
| _a definir_ | Secretaria, coordenação, equipe | _pendente_ |
