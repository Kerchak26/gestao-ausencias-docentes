"""API JSON somente leitura para integração com o sistema existente da instituição."""
from flask import Blueprint, jsonify

from ..services import CLASSIFICACOES, classificar, filtrar_ausencias, indicadores, justificada
from .auth import GESTAO, perfis
from .dashboard import filtros_da_requisicao

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/ausencias")
@perfis(*GESTAO)
def ausencias():
    itens = filtrar_ausencias(**filtros_da_requisicao())
    return jsonify([
        {
            "id": a.id,
            "data": a.data.isoformat(),
            "horario_inicio": a.horario_inicio.strftime("%H:%M"),
            "horario_fim": a.horario_fim.strftime("%H:%M"),
            "professor": a.professor.nome,
            "disciplina": a.disciplina.nome,
            "turma": a.turma.nome,
            "motivo": a.motivo,
            "classificacao": classificar(a),
            "classificacao_descricao": CLASSIFICACOES[classificar(a)],
            "substituto": a.substituicao.substituto.nome if a.substituicao else None,
            "justificada": justificada(a),
            "reposicoes": [{"data": r.data.isoformat(), "status": r.status} for r in a.reposicoes],
        }
        for a in itens
    ])


@bp.route("/indicadores")
@perfis(*GESTAO)
def resumo():
    return jsonify(indicadores(filtrar_ausencias(**filtros_da_requisicao())))
