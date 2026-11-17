"""Regras de negócio do módulo.

Concentrar as regras aqui (e não nas rotas) facilita os testes unitários.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time

from flask import session

from .extensions import db
from .models import Anexo, Ausencia, Aula, Historico, Professor, Substituicao

# --------------------------------------------------------------------------
# Classificação automática das aulas afetadas por ausência
# --------------------------------------------------------------------------
CLASSIFICACOES = {
    "substituida": "Substituída",
    "pendente": "Vaga – aguardando substituto",
    "reposicao_agendada": "Vaga – reposição agendada",
    "reposta": "Reposta",
    "vaga": "Vaga – sem cobertura",
}

MOTIVOS = {
    "saude": "Saúde / atestado médico",
    "pessoal": "Motivo pessoal",
    "academico": "Evento acadêmico / congresso",
    "transporte": "Transporte / trânsito",
    "nao_informado": "Não informado",
}


def classificar(ausencia: Ausencia, agora: datetime | None = None) -> str:
    """Classifica automaticamente a aula afetada pela ausência.

    Ordem de prioridade:
    1. Há substituto atribuído                -> ``substituida``
    2. Alguma reposição já foi realizada      -> ``reposta``
    3. Existe reposição agendada              -> ``reposicao_agendada``
    4. A aula ainda não terminou              -> ``pendente`` (dá tempo de substituir)
    5. A aula terminou sem cobertura          -> ``vaga``
    """
    agora = agora or datetime.now()
    if ausencia.substituicao is not None:
        return "substituida"
    status_reposicoes = {r.status for r in ausencia.reposicoes}
    if "realizada" in status_reposicoes:
        return "reposta"
    if "agendada" in status_reposicoes:
        return "reposicao_agendada"
    fim_da_aula = datetime.combine(ausencia.data, ausencia.horario_fim)
    if agora < fim_da_aula:
        return "pendente"
    return "vaga"


def justificada(ausencia: Ausencia) -> bool:
    """Ausência é justificada quando possui atestado/declaração aprovado."""
    return any(a.tipo in ("atestado", "declaracao") and a.status == "aprovado" for a in ausencia.anexos)


def possui_documento(ausencia: Ausencia) -> bool:
    return any(a.tipo in ("atestado", "declaracao") for a in ausencia.anexos)


# --------------------------------------------------------------------------
# Substituições
# --------------------------------------------------------------------------
def _sobrepoe(ini1: time, fim1: time, ini2: time, fim2: time) -> bool:
    return ini1 < fim2 and ini2 < fim1


def sugerir_substitutos(ausencia: Ausencia) -> list[Professor]:
    """Lista professores disponíveis no horário da aula vaga.

    Um professor está disponível quando: está ativo, não é o ausente, não tem
    aula na grade no mesmo dia/horário, não está ausente no mesmo horário e
    não está substituindo outra aula no mesmo horário.
    Ordenação: quem leciona a mesma disciplina primeiro; depois quem fez
    menos substituições no mês (distribui a carga); depois nome.
    """
    dia = ausencia.data.weekday()
    ini, fim = ausencia.horario_inicio, ausencia.horario_fim
    ocupados: set[int] = {ausencia.professor_id}

    for aula in Aula.query.filter_by(dia_semana=dia).all():
        if _sobrepoe(ini, fim, aula.horario_inicio, aula.horario_fim):
            ocupados.add(aula.professor_id)

    for outra in Ausencia.query.filter_by(data=ausencia.data).all():
        if _sobrepoe(ini, fim, outra.horario_inicio, outra.horario_fim):
            ocupados.add(outra.professor_id)
            if outra.substituicao and outra.id != ausencia.id:
                ocupados.add(outra.substituicao.substituto_id)

    mesma_disciplina = {
        a.professor_id for a in Aula.query.filter_by(disciplina_id=ausencia.disciplina_id).all()
    }
    inicio_mes = ausencia.data.replace(day=1)
    carga = Counter(
        s.substituto_id
        for s in Substituicao.query.join(Ausencia).filter(Ausencia.data >= inicio_mes).all()
    )

    candidatos = [p for p in Professor.query.filter_by(ativo=True).all() if p.id not in ocupados]
    candidatos.sort(key=lambda p: (p.id not in mesma_disciplina, carga[p.id], p.nome))
    return candidatos


def atribuir_substituto(ausencia: Ausencia, substituto_id: int, observacao: str = "") -> Substituicao:
    disponiveis = {p.id for p in sugerir_substitutos(ausencia)}
    if ausencia.substituicao and ausencia.substituicao.substituto_id == substituto_id:
        return ausencia.substituicao
    if substituto_id not in disponiveis:
        raise ValueError("Professor indisponível no horário desta aula.")
    if ausencia.substituicao:
        db.session.delete(ausencia.substituicao)
        db.session.flush()
    sub = Substituicao(ausencia=ausencia, substituto_id=substituto_id, observacao=observacao)
    db.session.add(sub)
    db.session.flush()
    registrar(ausencia, f"Substituto atribuído: {db.session.get(Professor, substituto_id).nome}")
    return sub


# --------------------------------------------------------------------------
# Consulta, filtros e indicadores
# --------------------------------------------------------------------------
def filtrar_ausencias(inicio: date | None = None, fim: date | None = None, professor_id: int | None = None,
                      turma_id: int | None = None, classificacao: str | None = None,
                      agora: datetime | None = None) -> list[Ausencia]:
    q = Ausencia.query
    if inicio:
        q = q.filter(Ausencia.data >= inicio)
    if fim:
        q = q.filter(Ausencia.data <= fim)
    if professor_id:
        q = q.filter(Ausencia.professor_id == professor_id)
    if turma_id:
        q = q.filter(Ausencia.turma_id == turma_id)
    itens = q.order_by(Ausencia.data.desc(), Ausencia.horario_inicio).all()
    if classificacao:
        itens = [a for a in itens if classificar(a, agora) == classificacao]
    return itens


def _pct(parte: int, total: int) -> float:
    return round(100 * parte / total, 1) if total else 0.0


def indicadores(ausencias: list[Ausencia], agora: datetime | None = None) -> dict:
    total = len(ausencias)
    classes = Counter(classificar(a, agora) for a in ausencias)
    com_doc = sum(1 for a in ausencias if possui_documento(a))
    justificadas = sum(1 for a in ausencias if justificada(a))
    reposicoes = [r for a in ausencias for r in a.reposicoes]
    por_professor = Counter(a.professor.nome for a in ausencias).most_common()
    por_turma = Counter(a.turma.nome for a in ausencias).most_common()
    por_motivo = Counter(MOTIVOS.get(a.motivo, a.motivo) for a in ausencias).most_common()
    return {
        "total": total,
        "classes": {k: classes.get(k, 0) for k in CLASSIFICACOES},
        "taxa_substituicao": _pct(classes.get("substituida", 0), total),
        "taxa_cobertura": _pct(classes.get("substituida", 0) + classes.get("reposta", 0), total),
        "com_documento": com_doc,
        "taxa_documentacao": _pct(com_doc, total),
        "justificadas": justificadas,
        "reposicoes_agendadas": sum(1 for r in reposicoes if r.status == "agendada"),
        "reposicoes_realizadas": sum(1 for r in reposicoes if r.status == "realizada"),
        "documentos_pendentes": sum(1 for a in ausencias for d in a.anexos if d.status == "pendente"),
        "por_professor": por_professor,
        "por_turma": por_turma,
        "por_motivo": por_motivo,
    }


# --------------------------------------------------------------------------
# Rastreabilidade
# --------------------------------------------------------------------------
def registrar(ausencia: Ausencia | None, acao: str) -> None:
    usuario_id = session.get("usuario_id") if _tem_contexto_requisicao() else None
    db.session.add(Historico(ausencia_id=ausencia.id if ausencia else None, usuario_id=usuario_id, acao=acao))


def _tem_contexto_requisicao() -> bool:
    from flask import has_request_context

    return has_request_context()


def anexos_pendentes() -> list[Anexo]:
    return Anexo.query.filter_by(status="pendente").order_by(Anexo.criado_em).all()
