# Fase 5 — Implantação e treinamento

## 1. Preparação do ambiente de produção

Requisitos: servidor Linux (ou Windows) com Python 3.11+, acesso HTTPS e backup diário.

```bash
git clone https://github.com/Kerchak26/gestao-ausencias-docentes.git
cd gestao-ausencias-docentes
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt gunicorn
```

Variáveis de ambiente:

| Variável | Exemplo | Obrigatória |
|---|---|---|
| `SECRET_KEY` | uma string aleatória longa (`python -c "import secrets; print(secrets.token_hex(32))"`) | Sim |
| `DATABASE_URL` | `postgresql://usuario:senha@host/ausencias` (padrão: SQLite em `instance/`) | Recomendado |
| `UPLOAD_FOLDER` | `/var/ausencias/anexos` | Recomendado |

Executar:

```bash
gunicorn -w 3 -b 0.0.0.0:8000 "app:create_app()"
```

Coloque um proxy reverso (Nginx ou o servidor web da instituição) com HTTPS na frente.

## 2. Checklist de implantação

- [ ] `SECRET_KEY` definida e fora do repositório
- [ ] Banco de produção criado e testado
- [ ] Pasta de anexos com backup e acesso restrito (dados de saúde, LGPD)
- [ ] Grade do semestre importada (`flask --app run importar-grade grade.csv`)
- [ ] Usuários reais criados (`flask --app run criar-usuario`) e usuários demo removidos
- [ ] HTTPS ativo
- [ ] Proteção CSRF adicionada aos formulários (ver backlog em `03-desenvolvimento.md`)
- [ ] Teste de fumaça: login, lançamento, substituição, upload, PDF

## 3. Plano de treinamento

| Sessão | Público | Duração | Conteúdo |
|---|---|---|---|
| 1 | Secretaria | 1h30 | Lançamento diário, substituições, situação das aulas, atestados, reposições, cadastros e importação da grade |
| 2 | Coordenadores | 1h | Dashboard, filtros, indicadores, relatórios PDF, aprovação de documentos |
| 3 | Professores | 30 min (pode ser vídeo) | Acesso pelo celular, envio de atestado, agendamento de reposição e comprovante |

Material: [manual do usuário](manual-do-usuario.md) e banco de demonstração (`flask --app run seed`). Cada sessão termina com os participantes executando as tarefas do roteiro de usabilidade (`04-testes.md`).

**Lista de presença**

| Data | Sessão | Participantes |
|---|---|---|
| | | |

## 4. Acompanhamento pós-implantação

- Primeiras 2 semanas: um integrante da equipe de plantão em horário combinado com a secretaria.
- Canal de suporte: abrir *issue* no GitHub ou contato direto com a equipe.
- Reunião de acompanhamento após 15 e 30 dias para coletar feedback.

| Data | Ocorrência | Responsável | Solução |
|---|---|---|---|
| | | | |
