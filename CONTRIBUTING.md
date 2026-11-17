# Como contribuir

## Fluxo de trabalho

1. Atualize a `main`: `git pull origin main`
2. Crie uma branch por tarefa: `git checkout -b feature/nome-curto` (ou `fix/...`, `docs/...`)
3. Faça commits pequenos com mensagens claras em português: `Adiciona filtro por turno no dashboard`
4. Rode os testes antes de enviar: `pytest`
5. Envie e abra um Pull Request: `git push -u origin feature/nome-curto`
6. Pelo menos um colega revisa antes do merge. Os testes do GitHub Actions precisam passar.

## Padrões

- Código e nomes em português, seguindo o que já existe (`ausencia`, `professor`, `substituicao`).
- Regras de negócio ficam em `app/services.py`, não nas rotas, para poderem ser testadas.
- Toda funcionalidade nova vem com teste em `tests/`.
- Toda ação que altera uma ausência chama `services.registrar(...)` para manter o histórico.
- Atualize a documentação em `docs/` quando mudar um fluxo.

## Organização das tarefas

Use as *Issues* do GitHub com os rótulos das fases (`fase-1` ... `fase-6`) e um *Project* (quadro Kanban) para acompanhar quem está fazendo o quê.
