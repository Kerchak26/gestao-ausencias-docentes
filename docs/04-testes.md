# Fase 4 — Testes e validação

## 1. Testes automatizados

```bash
pytest -v
```

Os testes rodam automaticamente no GitHub Actions a cada push e pull request (`.github/workflows/testes.yml`).

| Arquivo | Tipo | O que cobre |
|---|---|---|
| `tests/test_services.py` | Unitário | Classificação automática das aulas, sugestão e atribuição de substitutos, indicadores e filtros |
| `tests/test_rotas.py` | Integração (HTTP) | Login e permissões, lançamento manual e pela grade, substituição, upload e aprovação de atestados, reposição com comprovante, dashboard, PDF, API e importação CSV |

Situação atual: **29 testes passando**.

## 2. Testes de usabilidade (ambiente controlado)

Executar com a secretaria e os coordenadores usando o banco de demonstração (`flask --app run seed`).

**Preparação:** um notebook e um celular, cronômetro, este roteiro impresso. Um integrante conduz, outro anota.

| # | Tarefa | Perfil | Critério de sucesso | Tempo meta |
|---|---|---|---|---|
| T1 | Registrar a falta de um professor em duas aulas do dia pela grade | Secretaria | Ausências aparecem na lista do dia | < 1 min |
| T2 | Registrar uma falta manualmente (aula fora da grade) | Secretaria | Ausência registrada sem erro | < 1 min |
| T3 | Atribuir substituto para as aulas do dia | Secretaria | Situação muda para "Substituída" | < 1 min |
| T4 | Pelo celular, enviar a foto de um atestado | Professor | Documento aparece como pendente | < 2 min |
| T5 | Aprovar o atestado | Coordenador | Ausência fica "justificada" | < 30 s |
| T6 | Agendar uma reposição e marcar como realizada | Secretaria | Situação "Reposta" | < 1 min |
| T7 | Ver quantas faltas a turma ADS-1A teve no mês | Coordenador | Número correto informado | < 1 min |
| T8 | Gerar o PDF de um professor para reunião | Coordenador | PDF aberto com os dados do professor | < 1 min |

Após as tarefas, aplicar o questionário SUS (System Usability Scale, 10 perguntas, escala 1–5). Meta: nota ≥ 70.

## 3. Registro de execução

| Data | Participante (perfil) | Tarefas concluídas | Tempo total | Nota SUS | Problemas encontrados |
|---|---|---|---|---|---|
| | | | | | |

## 4. Problemas e correções

| ID | Descrição | Gravidade | Correção (commit/PR) | Situação |
|---|---|---|---|---|
| | | | | |

## 5. Checklist de aceitação dos requisitos

- [ ] RF01–RF13 validados com os usuários
- [ ] Interface testada em pelo menos um Android e um iPhone
- [ ] Importação da grade real do semestre funcionando
- [ ] Atestados acessíveis apenas à gestão e ao próprio professor
- [ ] Aprovação formal da secretaria e da coordenação
