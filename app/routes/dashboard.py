"""Dashboard do coordenador com filtros e indicadores."""
from datetime import date, timedelta

from flask import Blueprint, render_template, request

from ..models import Professor, Turma
from ..services import filtrar_ausencias, indicadores
from ..utils import parse_data, parse_int
from .auth import GESTAO, perfis

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def filtros_da_requisicao():
    hoje = date.today()
    return {
        "inicio": parse_data(request.args.get("inicio"), hoje - timedelta(days=30)),
        "fim": parse_data(request.args.get("fim"), hoje),
        "professor_id": parse_int(request.args.get("professor_id")),
        "turma_id": parse_int(request.args.get("turma_id")),
    }


@bp.route("/")
@perfis(*GESTAO)
def painel():
    f = filtros_da_requisicao()
    ausencias = filtrar_ausencias(**f)
    return render_template(
        "dashboard/painel.html", f=f, ind=indicadores(ausencias), ausencias=ausencias[:15],
        professores=Professor.query.order_by(Professor.nome).all(),
        turmas=Turma.query.order_by(Turma.nome).all(),
    )
