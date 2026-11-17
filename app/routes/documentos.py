"""Atestados, comprovações e reposições."""
from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, send_from_directory, url_for

from ..extensions import db
from ..models import Anexo, Ausencia, Reposicao
from ..services import anexos_pendentes, filtrar_ausencias, registrar
from ..utils import parse_data, parse_hora, salvar_upload
from .ausencias import pode_ver
from .auth import GESTAO, login_required, perfis

bp = Blueprint("documentos", __name__)


@bp.route("/documentos")
@perfis(*GESTAO)
def central():
    reposicoes = Reposicao.query.filter_by(status="agendada").order_by(Reposicao.data).all()
    return render_template("documentos/central.html", pendentes=anexos_pendentes(), reposicoes=reposicoes)


@bp.route("/minhas-ausencias")
@login_required
def minhas_ausencias():
    if not g.usuario.professor_id:
        return redirect(url_for("auth.inicio"))
    return render_template("professor/minhas_ausencias.html",
                           ausencias=filtrar_ausencias(professor_id=g.usuario.professor_id))


@bp.route("/ausencias/<int:id>/anexos", methods=["POST"])
@login_required
def enviar_anexo(id):
    ausencia = db.get_or_404(Ausencia, id)
    if not pode_ver(ausencia):
        abort(403)
    arquivo = request.files.get("arquivo")
    tipo = request.form.get("tipo", "atestado")
    reposicao = None
    if tipo == "comprovante_reposicao":
        reposicao = db.session.get(Reposicao, int(request.form.get("reposicao_id") or 0))
        if not reposicao or reposicao.ausencia_id != ausencia.id:
            flash("Selecione a reposição a que o comprovante se refere.", "erro")
            return redirect(url_for("ausencias.detalhe", id=id))
    if tipo not in Anexo.TIPOS or not arquivo or not arquivo.filename:
        flash("Selecione um arquivo e o tipo de documento.", "erro")
        return redirect(url_for("ausencias.detalhe", id=id))
    try:
        original, armazenado = salvar_upload(arquivo)
    except ValueError as e:
        flash(str(e), "erro")
        return redirect(url_for("ausencias.detalhe", id=id))
    anexo = Anexo(ausencia=ausencia, reposicao=reposicao, tipo=tipo, nome_original=original,
                  arquivo=armazenado, enviado_por_id=g.usuario.id)
    db.session.add(anexo)
    registrar(ausencia, f"Documento enviado: {Anexo.TIPOS[tipo]} ({original})")
    db.session.commit()
    flash("Documento enviado. Aguarda conferência da coordenação.", "ok")
    return redirect(url_for("ausencias.detalhe", id=id))


@bp.route("/anexos/<int:id>")
@login_required
def baixar_anexo(id):
    anexo = db.get_or_404(Anexo, id)
    if not pode_ver(anexo.ausencia):
        abort(403)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], anexo.arquivo,
                               download_name=anexo.nome_original)


@bp.route("/anexos/<int:id>/avaliar", methods=["POST"])
@perfis(*GESTAO)
def avaliar_anexo(id):
    anexo = db.get_or_404(Anexo, id)
    status = request.form.get("status")
    if status not in ("aprovado", "recusado"):
        abort(400)
    anexo.status = status
    if anexo.tipo == "comprovante_reposicao" and anexo.reposicao and status == "aprovado":
        anexo.reposicao.status = "realizada"
        registrar(anexo.ausencia, f"Reposição de {anexo.reposicao.data:%d/%m/%Y} comprovada")
    registrar(anexo.ausencia, f"Documento {anexo.nome_original} {status}")
    db.session.commit()
    flash(f"Documento {status}.", "ok")
    return redirect(request.referrer or url_for("documentos.central"))


@bp.route("/ausencias/<int:id>/reposicoes", methods=["POST"])
@login_required
def agendar_reposicao(id):
    ausencia = db.get_or_404(Ausencia, id)
    if not pode_ver(ausencia):
        abort(403)
    data = parse_data(request.form.get("data"))
    ini, fim = parse_hora(request.form.get("horario_inicio")), parse_hora(request.form.get("horario_fim"))
    if not (data and ini and fim) or ini >= fim:
        flash("Informe data e horário válidos para a reposição.", "erro")
        return redirect(url_for("ausencias.detalhe", id=id))
    rep = Reposicao(ausencia=ausencia, data=data, horario_inicio=ini, horario_fim=fim,
                    local=request.form.get("local", "").strip())
    db.session.add(rep)
    registrar(ausencia, f"Reposição agendada para {data:%d/%m/%Y} {ini:%H:%M}")
    db.session.commit()
    flash("Reposição agendada.", "ok")
    return redirect(url_for("ausencias.detalhe", id=id))


@bp.route("/reposicoes/<int:id>/status", methods=["POST"])
@perfis(*GESTAO)
def status_reposicao(id):
    rep = db.get_or_404(Reposicao, id)
    status = request.form.get("status")
    if status not in Reposicao.STATUS:
        abort(400)
    rep.status = status
    registrar(rep.ausencia, f"Reposição de {rep.data:%d/%m/%Y} marcada como {status}")
    db.session.commit()
    flash("Reposição atualizada.", "ok")
    return redirect(request.referrer or url_for("ausencias.detalhe", id=rep.ausencia_id))
