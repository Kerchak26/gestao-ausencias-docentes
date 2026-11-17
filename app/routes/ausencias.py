"""Lançamento diário e consulta de ausências."""
from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Ausencia, Aula, Disciplina, Historico, Professor, Turma
from ..services import MOTIVOS, _sobrepoe, filtrar_ausencias, registrar, sugerir_substitutos
from ..utils import parse_data, parse_hora, parse_int
from .auth import GESTAO, login_required, perfis

bp = Blueprint("ausencias", __name__, url_prefix="/ausencias")


def _conflito(professor_id, data, inicio, fim, ignorar_id=None):
    for a in Ausencia.query.filter_by(professor_id=professor_id, data=data).all():
        if a.id != ignorar_id and _sobrepoe(inicio, fim, a.horario_inicio, a.horario_fim):
            return a
    return None


def criar_ausencia(professor_id, disciplina_id, turma_id, data, inicio, fim, motivo, observacao=""):
    if not all([professor_id, disciplina_id, turma_id, data, inicio, fim]):
        raise ValueError("Preencha professor, disciplina, turma, data e horário.")
    if inicio >= fim:
        raise ValueError("O horário de início deve ser anterior ao de término.")
    if motivo not in MOTIVOS:
        motivo = "nao_informado"
    if _conflito(professor_id, data, inicio, fim):
        raise ValueError("Já existe ausência registrada para este professor neste horário.")
    ausencia = Ausencia(
        professor_id=professor_id, disciplina_id=disciplina_id, turma_id=turma_id, data=data,
        horario_inicio=inicio, horario_fim=fim, motivo=motivo, observacao=observacao,
        registrado_por_id=g.usuario.id if g.get("usuario") else None,
    )
    db.session.add(ausencia)
    db.session.flush()
    registrar(ausencia, "Ausência registrada")
    return ausencia


@bp.route("/lancamento", methods=["GET", "POST"])
@perfis(*GESTAO)
def lancamento():
    dia = parse_data(request.values.get("data"), date.today())
    if request.method == "POST":
        motivo = request.form.get("motivo", "nao_informado")
        observacao = request.form.get("observacao", "").strip()
        criadas, erros = 0, []
        aula_ids = [parse_int(x) for x in request.form.getlist("aula_ids")]
        try:
            if aula_ids:  # lançamento rápido a partir da grade horária
                for aula in Aula.query.filter(Aula.id.in_([a for a in aula_ids if a])).all():
                    try:
                        criar_ausencia(aula.professor_id, aula.disciplina_id, aula.turma_id, dia,
                                       aula.horario_inicio, aula.horario_fim, motivo, observacao)
                        criadas += 1
                    except ValueError as e:
                        erros.append(f"{aula.professor.nome} {aula.horario_inicio:%H:%M}: {e}")
            else:  # lançamento manual
                criar_ausencia(
                    parse_int(request.form.get("professor_id")), parse_int(request.form.get("disciplina_id")),
                    parse_int(request.form.get("turma_id")), dia, parse_hora(request.form.get("horario_inicio")),
                    parse_hora(request.form.get("horario_fim")), motivo, observacao,
                )
                criadas = 1
        except ValueError as e:
            erros.append(str(e))
        db.session.commit()
        if criadas:
            flash(f"{criadas} ausência(s) registrada(s).", "ok")
        for erro in erros:
            flash(erro, "erro")
        return redirect(url_for("ausencias.lancamento", data=dia.isoformat()))

    professor_sel = parse_int(request.args.get("professor_id"))
    grade = Aula.query.filter_by(dia_semana=dia.weekday())
    if professor_sel:
        grade = grade.filter_by(professor_id=professor_sel)
    grade = grade.order_by(Aula.horario_inicio).all()
    return render_template(
        "ausencias/lancamento.html", dia=dia, grade=grade, professor_sel=professor_sel,
        ausencias_do_dia=filtrar_ausencias(dia, dia),
        professores=Professor.query.filter_by(ativo=True).order_by(Professor.nome).all(),
        disciplinas=Disciplina.query.order_by(Disciplina.nome).all(),
        turmas=Turma.query.order_by(Turma.nome).all(),
    )


@bp.route("/")
@perfis(*GESTAO)
def lista():
    f = {
        "inicio": parse_data(request.args.get("inicio")),
        "fim": parse_data(request.args.get("fim")),
        "professor_id": parse_int(request.args.get("professor_id")),
        "turma_id": parse_int(request.args.get("turma_id")),
        "classificacao": request.args.get("classificacao") or None,
    }
    return render_template(
        "ausencias/lista.html", ausencias=filtrar_ausencias(**f), f=f,
        professores=Professor.query.order_by(Professor.nome).all(),
        turmas=Turma.query.order_by(Turma.nome).all(),
    )


def pode_ver(ausencia: Ausencia) -> bool:
    if g.usuario.perfil in GESTAO:
        return True
    return g.usuario.professor_id == ausencia.professor_id


@bp.route("/<int:id>")
@login_required
def detalhe(id):
    ausencia = db.get_or_404(Ausencia, id)
    if not pode_ver(ausencia):
        abort(403)
    historico = Historico.query.filter_by(ausencia_id=id).order_by(Historico.criado_em).all()
    sugestoes = sugerir_substitutos(ausencia) if g.usuario.perfil in GESTAO else []
    return render_template("ausencias/detalhe.html", a=ausencia, historico=historico, sugestoes=sugestoes)


@bp.route("/<int:id>/excluir", methods=["POST"])
@perfis(*GESTAO)
def excluir(id):
    ausencia = db.get_or_404(Ausencia, id)
    registrar(ausencia, f"Ausência excluída ({ausencia.professor.nome}, {ausencia.data:%d/%m/%Y})")
    db.session.delete(ausencia)
    db.session.commit()
    flash("Lançamento excluído.", "ok")
    return redirect(url_for("ausencias.lancamento", data=ausencia.data.isoformat()))
