import os
import uuid
from datetime import date, datetime, time

from flask import current_app
from werkzeug.utils import secure_filename


def parse_data(valor: str | None, padrao: date | None = None) -> date | None:
    if not valor:
        return padrao
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return padrao


def parse_hora(valor: str | None) -> time | None:
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%H:%M").time()
    except ValueError:
        return None


def parse_int(valor) -> int | None:
    try:
        return int(valor) if valor not in (None, "") else None
    except (TypeError, ValueError):
        return None


def extensao_permitida(nome: str) -> bool:
    return "." in nome and nome.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def salvar_upload(arquivo) -> tuple[str, str]:
    """Salva o arquivo com nome único. Retorna (nome_original, nome_armazenado)."""
    original = secure_filename(arquivo.filename or "") or "arquivo"
    if not extensao_permitida(original):
        raise ValueError("Formato não permitido. Envie PDF, PNG ou JPG.")
    armazenado = f"{uuid.uuid4().hex}.{original.rsplit('.', 1)[1].lower()}"
    arquivo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], armazenado))
    return original, armazenado
