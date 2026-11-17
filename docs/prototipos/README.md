# Protótipos de baixa fidelidade

Wireframes das telas principais, usados para validar o fluxo com a secretaria e a coordenação antes do desenvolvimento. As telas finais implementadas estão em [../telas](../telas).

## 1. Lançamento diário de ausências (secretaria)

```
┌──────────────────────────────────────────────────────────────┐
│ Lançamento diário de ausências          [ 17/11/2026 ] [Ir]  │
├────────────────────────────────┬─────────────────────────────┤
│ GRADE DO DIA   [Professor ▼]   │ LANÇAMENTO MANUAL           │
│ ☐ 19:00 Ana · Algoritmos · 1A  │ Professor  [__________ ▼]   │
│ ☑ 19:00 Bruno · BD · 2A        │ Disciplina [__________ ▼]   │
│ ☐ 20:50 Carla · Web · 1A       │ Turma      [__________ ▼]   │
│ Motivo [Saúde ▼] Obs [_____]   │ Início [__:__] Fim [__:__]  │
│ [Registrar faltas selecionadas]│ Motivo [▼]  [Registrar]     │
├────────────────────────────────┴─────────────────────────────┤
│ AUSÊNCIAS DO DIA                                             │
│ 19:00 Bruno  BD  2A   (Aguardando substituto)   [Abrir]      │
│ [Alocar substitutos para este dia →]                         │
└──────────────────────────────────────────────────────────────┘
```

## 2. Substituições do dia

```
┌─────────────────────────────────────────┐
│ Substituições do dia     [17/11] [Ir]   │
├─────────────────────────────────────────┤
│ 19:00–20:40 · ADS-2A  (Aguardando)      │
│ Banco de Dados — ausente: Bruno         │
│ [Carla (mesma disciplina) ▼] [Atribuir] │
├─────────────────────────────────────────┤
│ 20:50–22:30 · ADS-1A  (Substituída)     │
│ Substituto: Diego          [Remover]    │
└─────────────────────────────────────────┘
```

## 3. Detalhe da ausência (secretaria e professor)

```
┌─────────────────────────────────────────┐
│ Ausência #12            (Vaga)          │
│ Professor, data, horário, turma, motivo │
├───────────────────┬─────────────────────┤
│ SUBSTITUIÇÃO      │ REPOSIÇÕES          │
│ [Disponíveis ▼]   │ 24/11 18:00 agendada│
│ [Atribuir]        │ [+ Agendar]         │
├───────────────────┴─────────────────────┤
│ ATESTADOS E COMPROVAÇÕES                │
│ atestado.pdf  (pendente) [Aprovar][Recusar]
│ Tipo [▼] Arquivo [Escolher] [Enviar]    │
├─────────────────────────────────────────┤
│ HISTÓRICO: 17/11 19:02 Ausência registrada — Secretaria
└─────────────────────────────────────────┘
```

## 4. Dashboard do coordenador

```
┌──────────────────────────────────────────────────────────────┐
│ Dashboard                                     [Exportar PDF] │
│ De [__] Até [__] Professor [▼] Turma [▼]           [Filtrar] │
├─────────┬─────────┬─────────┬─────────┬─────────┬────────────┤
│ 26      │ 34,6%   │ 53,8%   │ 7       │ 3 / 5   │ 40%        │
│ faltas  │ substit.│ cobertas│ vagas   │ reposiç.│ c/ atestado│
├─────────┴─────────┴────┬────┴─────────┴─────────┴────────────┤
│ Faltas por professor   │ Faltas por turma                    │
│ Diego ██████████ 10    │ ADS-1A ██████████ 10                │
│ Ana   █████ 5          │ GTI-1A ████████ 8                   │
├────────────────────────┼─────────────────────────────────────┤
│ Situação das aulas     │ Motivos                             │
└────────────────────────┴─────────────────────────────────────┘
```

## 5. Relatório PDF

```
Relatório de Ausências Docentes e Reposições
Filtros: período 01/11 a 30/11, professor Diego Rocha
[Indicadores: total | substituídas | taxa | vagas | reposições | documentos]
[Ausências por professor]
[Histórico: data | horário | professor | disciplina | turma | motivo | situação | substituto | reposições | docs]
```

## 6. Celular (professor)

```
┌──────────────────────┐
│ Ausências Docentes ☰ │
├──────────────────────┤
│ Minhas ausências     │
│ ┌──────────────────┐ │
│ │ 10/11 19:00–20:40│ │
│ │ Algoritmos · 1A  │ │
│ │ (Vaga) sem doc.  │ │
│ └──────────────────┘ │
│ → Enviar atestado    │
│ → Agendar reposição  │
└──────────────────────┘
```
