"""Cadastros básicos: professores, disciplinas, turmas e grade horária."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..extensions import db
from ..importacao import importar_grade_csv
from ..models import Aula, Disciplina, Professor, Turma
from ..utils import parse_hora, parse_int
from .auth import GESTAO, perfis

bp = Blueprint("cadastros", __name__, url_prefix="/cadastros")


@bp.route("/")
@perfis(*GESTAO)
def index():
    return render_template(
        "cadastros/index.html",
        professores=Professor.query.order_by(Professor.nome).all(),
        disciplinas=Disciplina.query.order_by(Disciplina.nome).all(),
        turmas=Turma.query.order_by(Turma.nome).all(),
        grade=Aula.query.order_by(Aula.dia_semana, Aula.horario_inicio).all(),
    )


@bp.route("/<tipo>", methods=["POST"])
@perfis(*GESTAO)
def criar(tipo):
    form = request.form
    try:
        if tipo == "professor":
            if not form.get("nome", "").strip():
                raise ValueError("Informe o nome.")
            db.session.add(Professor(nome=form["nome"].strip(), email=form.get("email", "").strip()))
        elif tipo == "disciplina":
            if not form.get("codigo", "").strip() or not form.get("nome", "").strip():
                raise ValueError("Informe código e nome.")
            if Disciplina.query.filter_by(codigo=form["codigo"].strip()).first():
                raise ValueError("Código já cadastrado.")
            db.session.add(Disciplina(codigo=form["codigo"].strip(), nome=form["nome"].strip()))
        elif tipo == "turma":
            if not form.get("nome", "").strip():
                raise ValueError("Informe o nome da turma.")
            db.session.add(Turma(nome=form["nome"].strip(), curso=form.get("curso", "").strip(),
                                 turno=form.get("turno", "").strip()))
        elif tipo == "aula":
            ini, fim = parse_hora(form.get("horario_inicio")), parse_hora(form.get("horario_fim"))
            campos = [parse_int(form.get(c)) for c in ("professor_id", "disciplina_id", "turma_id")]
            dia = parse_int(form.get("dia_semana"))
            if None in campos or dia is None or not ini or not fim or ini >= fim:
                raise ValueError("Preencha todos os campos da aula com horários válidos.")
            db.session.add(Aula(professor_id=campos[0], disciplina_id=campos[1], turma_id=campos[2],
                                dia_semana=dia, horario_inicio=ini, horario_fim=fim))
        elif tipo == "importar":
            arquivo = request.files.get("arquivo")
            if not arquivo:
                raise ValueError("Selecione o arquivo CSV.")
            criadas, erros = importar_grade_csv(arquivo.read().decode("utf-8-sig"))
            flash(f"{criadas} aula(s) importada(s).", "ok")
            for e in erros[:10]:
                flash(e, "erro")
            return redirect(url_for("cadastros.index"))
        elif tipo == "professor-status":
            prof = db.get_or_404(Professor, parse_int(form.get("id")))
            prof.ativo = not prof.ativo
        else:
            raise ValueError("Tipo de cadastro inválido.")
        db.session.commit()
        flash("Cadastro salvo.", "ok")
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "erro")
    return redirect(url_for("cadastros.index"))
