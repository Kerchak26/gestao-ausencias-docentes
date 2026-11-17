from datetime import date, datetime

from .models import Anexo, DIAS_SEMANA
from .services import CLASSIFICACOES, MOTIVOS, classificar, justificada


def register_filters(app):
    @app.template_filter("data_br")
    def data_br(valor):
        if isinstance(valor, datetime):
            return valor.strftime("%d/%m/%Y %H:%M")
        if isinstance(valor, date):
            return valor.strftime("%d/%m/%Y")
        return valor or ""

    @app.template_filter("hora")
    def hora(valor):
        return valor.strftime("%H:%M") if valor else ""

    @app.context_processor
    def utilidades():
        return {
            "classificar": classificar,
            "justificada": justificada,
            "CLASSIFICACOES": CLASSIFICACOES,
            "MOTIVOS": MOTIVOS,
            "TIPOS_ANEXO": Anexo.TIPOS,
            "DIAS_SEMANA": DIAS_SEMANA,
        }
