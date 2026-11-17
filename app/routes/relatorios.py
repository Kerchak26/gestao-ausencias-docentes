"""Relatórios em PDF para reuniões com professores."""
from datetime import date

from flask import Blueprint, Response, render_template

from ..extensions import db
from ..models import Professor, Turma
from ..reports import gerar_pdf
from ..services import filtrar_ausencias
from .auth import GESTAO, perfis
from .dashboard import filtros_da_requisicao

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


@bp.route("/")
@perfis(*GESTAO)
def formulario():
    return render_template("relatorios/formulario.html", f=filtros_da_requisicao(),
                           professores=Professor.query.order_by(Professor.nome).all(),
                           turmas=Turma.query.order_by(Turma.nome).all())


def descrever(f) -> str:
    partes = [f"período {f['inicio']:%d/%m/%Y} a {f['fim']:%d/%m/%Y}"]
    professor = db.session.get(Professor, f["professor_id"]) if f["professor_id"] else None
    turma = db.session.get(Turma, f["turma_id"]) if f["turma_id"] else None
    if professor:
        partes.append(f"professor {professor.nome}")
    if turma:
        partes.append(f"turma {turma.nome}")
    return ", ".join(partes)


@bp.route("/pdf")
@perfis(*GESTAO)
def pdf():
    f = filtros_da_requisicao()
    conteudo = gerar_pdf(filtrar_ausencias(**f), descrever(f))
    nome = f"relatorio-ausencias-{date.today():%Y%m%d}.pdf"
    return Response(conteudo, mimetype="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{nome}"'})
