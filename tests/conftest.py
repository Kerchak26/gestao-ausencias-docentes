from datetime import date, time, timedelta

import pytest

from app import create_app
from app.extensions import db
from app.models import Aula, Disciplina, Professor, Turma, Usuario


@pytest.fixture
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'teste.db'}",
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        "SECRET_KEY": "teste",
    })
    (tmp_path / "uploads").mkdir(exist_ok=True)
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def dados(app):
    """Cenário mínimo: 4 professores, 2 disciplinas, 2 turmas e grade de segunda-feira."""
    ana, bruno, carla, diego = (Professor(nome=n) for n in ("Ana", "Bruno", "Carla", "Diego"))
    alg, bd = Disciplina(codigo="ALG", nome="Algoritmos"), Disciplina(codigo="BD", nome="Banco de Dados")
    t1, t2 = Turma(nome="ADS-1A"), Turma(nome="ADS-2A")
    db.session.add_all([ana, bruno, carla, diego, alg, bd, t1, t2])
    db.session.flush()
    # Segunda-feira, 19:00-20:40: Ana (ALG/T1) e Bruno (BD/T2) dão aula; Carla leciona ALG em outro dia.
    db.session.add_all([
        Aula(professor_id=ana.id, disciplina_id=alg.id, turma_id=t1.id, dia_semana=0,
             horario_inicio=time(19), horario_fim=time(20, 40)),
        Aula(professor_id=bruno.id, disciplina_id=bd.id, turma_id=t2.id, dia_semana=0,
             horario_inicio=time(19), horario_fim=time(20, 40)),
        Aula(professor_id=carla.id, disciplina_id=alg.id, turma_id=t2.id, dia_semana=2,
             horario_inicio=time(19), horario_fim=time(20, 40)),
    ])
    for nome, email, perfil, pid in [("Sec", "sec@t.br", "secretaria", None), ("Coord", "coord@t.br", "coordenador", None),
                                     ("Ana", "ana@t.br", "professor", ana.id), ("Bruno", "bruno@t.br", "professor", bruno.id)]:
        u = Usuario(nome=nome, email=email, perfil=perfil, professor_id=pid)
        u.definir_senha("senha")
        db.session.add(u)
    db.session.commit()
    # próxima segunda-feira (sempre no futuro, para a aula ainda estar "pendente")
    hoje = date.today()
    segunda = hoje + timedelta(days=(7 - hoje.weekday()) or 7)
    return {"ana": ana, "bruno": bruno, "carla": carla, "diego": diego, "alg": alg, "bd": bd,
            "t1": t1, "t2": t2, "segunda": segunda}


def login(client, email, senha="senha"):
    return client.post("/login", data={"email": email, "senha": senha})


@pytest.fixture
def secretaria(app, dados):
    c = app.test_client()
    login(c, "sec@t.br")
    return c


@pytest.fixture
def professora(app, dados):
    c = app.test_client()
    login(c, "ana@t.br")
    return c
