"""Gestão de substituições no mesmo dia."""
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Ausencia
from ..services import atribuir_substituto, filtrar_ausencias, registrar, sugerir_substitutos
from ..utils import parse_data, parse_int
from .auth import GESTAO, perfis

bp = Blueprint("substituicoes", __name__, url_prefix="/substituicoes")


@bp.route("/")
@perfis(*GESTAO)
def painel():
    dia = parse_data(request.args.get("data"), date.today())
    ausencias = filtrar_ausencias(dia, dia)
    ausencias.sort(key=lambda a: a.horario_inicio)
    sugestoes = {a.id: sugerir_substitutos(a) for a in ausencias}
    return render_template("substituicoes/painel.html", dia=dia, ausencias=ausencias, sugestoes=sugestoes)


def _voltar(ausencia):
    destino = request.form.get("voltar")
    if destino == "detalhe":
        return redirect(url_for("ausencias.detalhe", id=ausencia.id))
    return redirect(url_for("substituicoes.painel", data=ausencia.data.isoformat()))


@bp.route("/<int:ausencia_id>", methods=["POST"])
@perfis(*GESTAO)
def atribuir(ausencia_id):
    ausencia = db.get_or_404(Ausencia, ausencia_id)
    try:
        atribuir_substituto(ausencia, parse_int(request.form.get("substituto_id")),
                            request.form.get("observacao", "").strip())
        db.session.commit()
        flash("Substituto atribuído.", "ok")
    except (ValueError, TypeError) as e:
        db.session.rollback()
        flash(str(e) or "Selecione um substituto.", "erro")
    return _voltar(ausencia)


@bp.route("/<int:ausencia_id>/remover", methods=["POST"])
@perfis(*GESTAO)
def remover(ausencia_id):
    ausencia = db.get_or_404(Ausencia, ausencia_id)
    if ausencia.substituicao:
        registrar(ausencia, f"Substituição removida ({ausencia.substituicao.substituto.nome})")
        db.session.delete(ausencia.substituicao)
        db.session.commit()
        flash("Substituição removida.", "ok")
    return _voltar(ausencia)
