"""Módulo de Gestão de Ausências Docentes e Substituições.

Fábrica da aplicação Flask. Cada área funcional fica em um blueprint
próprio dentro de ``app/routes`` para facilitar o trabalho em equipe.
"""
import os

from flask import Flask

from .extensions import db


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", "sqlite:///" + os.path.join(app.instance_path, "ausencias.db")
        ),
        UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER", os.path.join(app.instance_path, "uploads")),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 MB por anexo
        ALLOWED_EXTENSIONS={"pdf", "png", "jpg", "jpeg"},
    )
    if config:
        app.config.update(config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    from .routes import auth, ausencias, cadastros, dashboard, documentos, relatorios, substituicoes, api

    for bp in (auth.bp, ausencias.bp, substituicoes.bp, documentos.bp, dashboard.bp, relatorios.bp, cadastros.bp, api.bp):
        app.register_blueprint(bp)

    from .filters import register_filters

    register_filters(app)

    from . import cli

    cli.register(app)

    with app.app_context():
        db.create_all()

    return app
