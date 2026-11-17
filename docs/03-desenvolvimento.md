# Fase 3 — Desenvolvimento do módulo

## Rastreabilidade: requisito → código → teste

| Requisito | Implementação | Testes |
|---|---|---|
| RF01 lançamento manual | `routes/ausencias.py::lancamento`, `criar_ausencia` | `test_lancamento_manual_e_duplicidade`, `test_lancamento_horario_invalido` |
| RF02 lançamento pela grade | `routes/ausencias.py::lancamento` (campo `aula_ids`) | `test_lancamento_rapido_pela_grade` |
| RF03 substitutos | `services.sugerir_substitutos`, `services.atribuir_substituto`, `routes/substituicoes.py` | `TestSubstitutos`, `test_fluxo_substituicao` |
| RF04 classificação | `services.classificar` | `TestClassificacao` |
| RF05/RF06 atestados | `routes/documentos.py::enviar_anexo`, `avaliar_anexo` | `test_professor_envia_atestado_e_coordenacao_aprova`, `test_upload_formato_invalido` |
| RF07 reposições | `routes/documentos.py::agendar_reposicao`, `status_reposicao` | `test_reposicao_com_comprovante`, `test_reposicao_agendada_e_realizada` |
| RF08 dashboard | `services.indicadores`, `routes/dashboard.py` | `test_indicadores`, `test_dashboard_e_pdf` |
| RF09 PDF | `reports.gerar_pdf`, `routes/relatorios.py` | `test_dashboard_e_pdf` |
| RF10 área do professor | `routes/documentos.py::minhas_ausencias`, `ausencias.pode_ver` | `test_professor_nao_ve_ausencia_de_outro` |
| RF11 histórico | `models.Historico`, `services.registrar` | `test_lancamento_manual_e_duplicidade` |
| RF12 cadastros/CSV | `routes/cadastros.py`, `importacao.py` | `test_importacao_csv` |
| RF13 API | `routes/api.py` | `test_api_json` |
| RNF01 responsivo | `static/style.css` (mobile first, tabelas viram cartões abaixo de 720 px) | `test_paginas_responsivas_tem_viewport` + verificação manual |
| RNF02/03 permissões | `routes/auth.py::perfis` | `test_rotas_exigem_login`, `test_professor_nao_acessa_dashboard` |

## Divisão sugerida do trabalho na equipe

Cada área funcional está em um blueprint separado, então cada integrante pode evoluir uma parte com poucos conflitos:

| Área | Arquivos principais |
|---|---|
| Lançamento e histórico | `routes/ausencias.py`, `templates/ausencias/` |
| Substituições | `routes/substituicoes.py`, `services.sugerir_substitutos` |
| Atestados e reposições | `routes/documentos.py`, `templates/documentos/`, `templates/professor/` |
| Dashboard e relatórios | `routes/dashboard.py`, `reports.py`, `templates/dashboard/` |
| Cadastros, integração e implantação | `routes/cadastros.py`, `importacao.py`, `routes/api.py` |

## Próximas melhorias (backlog)

- Notificação por e-mail ao professor substituto e ao professor ausente.
- Login integrado ao sistema da instituição (SSO/LDAP).
- Edição de ausências já lançadas (hoje é excluir e lançar de novo).
- Gráficos de evolução mensal no dashboard.
- Migrações de banco com Flask-Migrate antes de ir para produção.
- Proteção CSRF nos formulários (Flask-WTF) antes da implantação.
