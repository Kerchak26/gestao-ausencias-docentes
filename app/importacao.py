"""Importação da grade horária a partir de CSV exportado pelo sistema acadêmico.

Formato esperado (separador ``;`` ou ``,``, com cabeçalho):

    professor;email;disciplina_codigo;disciplina_nome;turma;curso;turno;dia_semana;inicio;fim
    Ana Souza;ana@impacta.edu.br;ADS101;Algoritmos;ADS-1A;ADS;Noite;0;19:00;20:40

``dia_semana``: 0 = segunda ... 6 = domingo.
"""
import csv
import io
from datetime import datetime

from .extensions import db
from .models import Aula, Disciplina, Professor, Turma


def _obter(modelo, filtro: dict, **extras):
    obj = modelo.query.filter_by(**filtro).first()
    if obj is None:
        obj = modelo(**filtro, **extras)
        db.session.add(obj)
        db.session.flush()
    return obj


def importar_grade_csv(texto: str) -> tuple[int, list[str]]:
    dialeto = ";" if texto.splitlines()[0].count(";") >= texto.splitlines()[0].count(",") else ","
    leitor = csv.DictReader(io.StringIO(texto), delimiter=dialeto)
    criadas, erros = 0, []
    for n, linha in enumerate(leitor, start=2):
        try:
            prof = _obter(Professor, {"nome": linha["professor"].strip()}, email=(linha.get("email") or "").strip())
            disc = _obter(Disciplina, {"codigo": linha["disciplina_codigo"].strip()},
                          nome=linha["disciplina_nome"].strip())
            turma = _obter(Turma, {"nome": linha["turma"].strip()}, curso=(linha.get("curso") or "").strip(),
                           turno=(linha.get("turno") or "").strip())
            dia = int(linha["dia_semana"])
            ini = datetime.strptime(linha["inicio"].strip(), "%H:%M").time()
            fim = datetime.strptime(linha["fim"].strip(), "%H:%M").time()
            if not 0 <= dia <= 6 or ini >= fim:
                raise ValueError("dia ou horário inválido")
            existe = Aula.query.filter_by(professor_id=prof.id, disciplina_id=disc.id, turma_id=turma.id,
                                          dia_semana=dia, horario_inicio=ini).first()
            if not existe:
                db.session.add(Aula(professor_id=prof.id, disciplina_id=disc.id, turma_id=turma.id,
                                    dia_semana=dia, horario_inicio=ini, horario_fim=fim))
                criadas += 1
        except (KeyError, ValueError, AttributeError) as e:
            erros.append(f"Linha {n}: {e}")
    db.session.commit()
    return criadas, erros
