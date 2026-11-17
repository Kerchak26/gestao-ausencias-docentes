"""Autenticação simples por sessão e controle de acesso por perfil."""
from functools import wraps

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import Usuario

bp = Blueprint("auth", __name__)


@bp.before_app_request
def carregar_usuario():
    uid = session.get("usuario_id")
    g.usuario = db.session.get(Usuario, uid) if uid else None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if g.usuario is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper


def perfis(*permitidos):
    """Restringe a rota aos perfis informados (ex.: ``@perfis('secretaria')``)."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if g.usuario.perfil not in permitidos:
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator


GESTAO = ("secretaria", "coordenador")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = Usuario.query.filter_by(email=request.form.get("email", "").strip().lower()).first()
        if usuario and usuario.verificar_senha(request.form.get("senha", "")):
            session.clear()
            session["usuario_id"] = usuario.id
            destino = request.args.get("next")
            if not destino or not destino.startswith("/") or destino.startswith("//"):
                destino = url_for("auth.inicio")
            return redirect(destino)
        flash("E-mail ou senha inválidos.", "erro")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/")
@login_required
def inicio():
    if g.usuario.perfil == "professor":
        return redirect(url_for("documentos.minhas_ausencias"))
    if g.usuario.perfil == "coordenador":
        return redirect(url_for("dashboard.painel"))
    return redirect(url_for("ausencias.lancamento"))
