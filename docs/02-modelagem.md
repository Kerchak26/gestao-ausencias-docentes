# Fase 2 — Modelagem e prototipação

## 1. Modelo de dados

```mermaid
erDiagram
    PROFESSOR ||--o{ AULA : "leciona (grade)"
    DISCIPLINA ||--o{ AULA : ""
    TURMA ||--o{ AULA : ""
    PROFESSOR ||--o{ AUSENCIA : "falta"
    DISCIPLINA ||--o{ AUSENCIA : ""
    TURMA ||--o{ AUSENCIA : ""
    AUSENCIA ||--o| SUBSTITUICAO : "coberta por"
    PROFESSOR ||--o{ SUBSTITUICAO : "substitui"
    AUSENCIA ||--o{ REPOSICAO : "reposta em"
    AUSENCIA ||--o{ ANEXO : "evidências"
    REPOSICAO ||--o{ ANEXO : "comprovante"
    AUSENCIA ||--o{ HISTORICO : "auditoria"
    USUARIO ||--o{ HISTORICO : "executou"
    USUARIO }o--o| PROFESSOR : "é (perfil professor)"

    PROFESSOR {
        int id PK
        string nome
        string email
        bool ativo
    }
    DISCIPLINA {
        int id PK
        string codigo UK
        string nome
    }
    TURMA {
        int id PK
        string nome
        string curso
        string turno
    }
    AULA {
        int id PK
        int professor_id FK
        int disciplina_id FK
        int turma_id FK
        int dia_semana
        time horario_inicio
        time horario_fim
    }
    AUSENCIA {
        int id PK
        int professor_id FK
        int disciplina_id FK
        int turma_id FK
        date data
        time horario_inicio
        time horario_fim
        string motivo
        text observacao
        int registrado_por_id FK
        datetime criado_em
    }
    SUBSTITUICAO {
        int id PK
        int ausencia_id FK
        int substituto_id FK
        text observacao
        datetime criado_em
    }
    REPOSICAO {
        int id PK
        int ausencia_id FK
        date data
        time horario_inicio
        time horario_fim
        string local
        string status
    }
    ANEXO {
        int id PK
        int ausencia_id FK
        int reposicao_id FK
        string tipo
        string nome_original
        string arquivo
        string status
        int enviado_por_id FK
    }
    HISTORICO {
        int id PK
        int ausencia_id FK
        int usuario_id FK
        string acao
        datetime criado_em
    }
    USUARIO {
        int id PK
        string nome
        string email UK
        string senha_hash
        string perfil
        int professor_id FK
    }
```

### Decisões de modelagem

- **Ausência guarda professor, disciplina, turma e horário** (e não só a aula da grade): permite registrar faltas em aulas extras ou fora da grade e preserva o histórico mesmo se a grade mudar no semestre seguinte.
- **A classificação da aula não é gravada**: é calculada a partir da substituição, das reposições e do horário (`services.classificar`). Assim nunca fica desatualizada.
- **Substituição é 1:1 com ausência** (restrição `unique`). Trocar o substituto substitui o registro e gera histórico.
- **Anexo único para atestados, declarações e comprovantes**, diferenciados por `tipo`, com fluxo de aprovação (`pendente → aprovado/recusado`).
- **Histórico** registra tudo o que acontece com cada ausência (rastreabilidade exigida pelo tema).

### Domínios

| Campo | Valores |
|---|---|
| `Usuario.perfil` | `secretaria`, `coordenador`, `professor` |
| `Ausencia.motivo` | `saude`, `pessoal`, `academico`, `transporte`, `nao_informado` |
| `Reposicao.status` | `agendada`, `realizada`, `cancelada` |
| `Anexo.tipo` | `atestado`, `declaracao`, `comprovante_reposicao` |
| `Anexo.status` | `pendente`, `aprovado`, `recusado` |
| `Aula.dia_semana` | 0 (segunda) a 6 (domingo) |

## 2. Arquitetura

```mermaid
flowchart LR
    subgraph Navegador["Navegador (desktop ou celular)"]
      UI[Telas HTML/CSS responsivas]
    end
    subgraph Flask["Aplicação Flask"]
      R[Blueprints<br/>ausencias · substituicoes · documentos<br/>dashboard · relatorios · cadastros · api]
      S[services.py<br/>regras de negócio]
      P[reports.py<br/>PDF]
      M[models.py<br/>SQLAlchemy]
    end
    DB[(Banco de dados<br/>SQLite / PostgreSQL)]
    FS[(Pasta de anexos)]
    SIS[Sistema acadêmico<br/>da instituição]

    UI --> R --> S --> M --> DB
    R --> P
    R --> FS
    SIS -- "CSV da grade horária" --> R
    R -- "API JSON /api/*" --> SIS
```

Camadas:

1. **Rotas (blueprints):** recebem a requisição, validam permissões e chamam os serviços. Um arquivo por área funcional facilita dividir o trabalho na equipe.
2. **Serviços:** regras de negócio puras, testadas de forma isolada.
3. **Modelos:** mapeamento das tabelas.

### Integração com o sistema existente

| Direção | Mecanismo | Uso |
|---|---|---|
| Sistema → módulo | Importação CSV da grade (`Cadastros` ou `flask importar-grade`) | Carregar professores, disciplinas, turmas e horários a cada semestre |
| Módulo → sistema | `GET /api/ausencias` e `GET /api/indicadores` (filtros `inicio`, `fim`, `professor_id`, `turma_id`) | Exibir ausências no portal ou integrar com folha/RH |
| Autenticação | Hoje própria; pode ser trocada por SSO/LDAP da instituição em `routes/auth.py` | Fase 5 |

## 3. Protótipos

Os protótipos de baixa fidelidade estão em [prototipos/](prototipos/README.md). As telas implementadas no MVP estão em [telas/](telas/).

## 4. Validação dos protótipos

| Data | Participantes | Ajustes solicitados |
|---|---|---|
| _a definir_ | Secretaria, coordenação | _pendente_ |
