"""Comandos de linha de comando: ``flask --app run <comando>``."""
import os
import random
from datetime import date, time, timedelta

import click
from flask import current_app
from reportlab.pdfgen import canvas

from .extensions import db
from .models import Anexo, Ausencia, Aula, Disciplina, Professor, Reposicao, Substituicao, Turma, Usuario, PERFIS


def _atestado_exemplo() -> str:
    """Gera (uma vez) um PDF fictício usado como anexo nos dados de demonstração."""
    nome = "atestado-exemplo.pdf"
    caminho = os.path.join(current_app.config["UPLOAD_FOLDER"], nome)
    if not os.path.exists(caminho):
        c = canvas.Canvas(caminho)
        c.drawString(72, 750, "ATESTADO MÉDICO (documento fictício para demonstração)")
        c.save()
    return nome


def popular_demo(seed: int = 42) -> None:
    """Cria dados fictícios para demonstração e testes de usabilidade."""
    rnd = random.Random(seed)
    db.drop_all()
    db.create_all()

    nomes = ["Ana Souza", "Bruno Lima", "Carla Mendes", "Diego Rocha", "Elisa Prado", "Fábio Nunes", "Gabriela Reis"]
    profs = [Professor(nome=n, email=n.lower().split()[0] + "@impacta.edu.br") for n in nomes]
    discs = [Disciplina(codigo=c, nome=n) for c, n in [
        ("ADS101", "Algoritmos e Lógica"), ("ADS102", "Banco de Dados"), ("ADS103", "Engenharia de Software"),
        ("ADS104", "Desenvolvimento Web"), ("ADS105", "Estatística Aplicada"), ("GTI201", "Gestão de Projetos")]]
    turmas = [Turma(nome=n, curso=c, turno="Noite") for n, c in [
        ("ADS-1A", "Análise e Desenvolvimento de Sistemas"), ("ADS-2A", "Análise e Desenvolvimento de Sistemas"),
        ("GTI-1A", "Gestão da Tecnologia da Informação")]]
    db.session.add_all(profs + discs + turmas)
    db.session.flush()

    blocos = [(time(19, 0), time(20, 40)), (time(20, 50), time(22, 30))]
    for dia in range(5):
        livres = profs[:]
        rnd.shuffle(livres)
        for t_idx, turma in enumerate(turmas):
            for b_idx, (ini, fim) in enumerate(blocos):
                prof = livres[(t_idx * 2 + b_idx) % len(livres)]
                db.session.add(Aula(professor_id=prof.id, disciplina_id=discs[(dia + t_idx + b_idx) % len(discs)].id,
                                    turma_id=turma.id, dia_semana=dia, horario_inicio=ini, horario_fim=fim))

    usuarios = [
        ("Secretaria Acadêmica", "secretaria@demo.edu.br", "secretaria", None),
        ("Coordenação de Curso", "coordenador@demo.edu.br", "coordenador", None),
        (profs[0].nome, "professor@demo.edu.br", "professor", profs[0].id),
    ]
    for nome, email, perfil, pid in usuarios:
        u = Usuario(nome=nome, email=email, perfil=perfil, professor_id=pid)
        u.definir_senha("demo123")
        db.session.add(u)
    db.session.flush()

    # Ausências históricas dos últimos 30 dias
    hoje = date.today()
    aulas = Aula.query.all()
    motivos = ["saude", "pessoal", "academico", "transporte", "nao_informado"]
    for delta in range(30, 0, -1):
        dia = hoje - timedelta(days=delta)
        do_dia = [a for a in aulas if a.dia_semana == dia.weekday()]
        for aula in rnd.sample(do_dia, k=min(len(do_dia), rnd.choice([0, 0, 1, 1, 2]))):
            aus = Ausencia(professor_id=aula.professor_id, disciplina_id=aula.disciplina_id, turma_id=aula.turma_id,
                           data=dia, horario_inicio=aula.horario_inicio, horario_fim=aula.horario_fim,
                           motivo=rnd.choice(motivos), registrado_por_id=1)
            db.session.add(aus)
            db.session.flush()
            sorte = rnd.random()
            if sorte < 0.5:
                from .services import sugerir_substitutos
                cands = sugerir_substitutos(aus)
                if cands:
                    db.session.add(Substituicao(ausencia_id=aus.id, substituto_id=cands[0].id))
            elif sorte < 0.8:
                db.session.add(Reposicao(ausencia_id=aus.id, data=dia + timedelta(days=7), horario_inicio=time(18, 0),
                                         horario_fim=time(18, 50), local="Sala 12",
                                         status="realizada" if dia + timedelta(days=7) < hoje else "agendada"))
            if aus.motivo == "saude":
                db.session.add(Anexo(ausencia_id=aus.id, tipo="atestado", nome_original="atestado-exemplo.pdf",
                                     arquivo=_atestado_exemplo(), enviado_por_id=3,
                                     status=rnd.choice(["aprovado", "aprovado", "pendente"])))
            db.session.flush()

    # Duas ausências no dia de hoje, ainda sem substituto (para demonstrar o painel)
    for aula in [a for a in aulas if a.dia_semana == hoje.weekday()][:2]:
        db.session.add(Ausencia(professor_id=aula.professor_id, disciplina_id=aula.disciplina_id,
                                turma_id=aula.turma_id, data=hoje, horario_inicio=aula.horario_inicio,
                                horario_fim=aula.horario_fim, motivo="saude", registrado_por_id=1))
    db.session.commit()


def register(app):
    @app.cli.command("seed")
    def seed():
        """Apaga o banco e cria dados de demonstração."""
        popular_demo()
        click.echo("Banco populado. Usuários: secretaria@demo.edu.br, coordenador@demo.edu.br, "
                   "professor@demo.edu.br (senha: demo123)")

    @app.cli.command("criar-usuario")
    @click.option("--nome", prompt=True)
    @click.option("--email", prompt=True)
    @click.option("--perfil", type=click.Choice(PERFIS), prompt=True)
    @click.option("--senha", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--professor-id", type=int, default=None)
    def criar_usuario(nome, email, perfil, senha, professor_id):
        """Cria um usuário de acesso."""
        u = Usuario(nome=nome, email=email.strip().lower(), perfil=perfil, professor_id=professor_id)
        u.definir_senha(senha)
        db.session.add(u)
        db.session.commit()
        click.echo(f"Usuário {email} criado.")

    @app.cli.command("importar-grade")
    @click.argument("arquivo", type=click.Path(exists=True))
    def importar_grade(arquivo):
        """Importa a grade horária de um CSV exportado do sistema acadêmico."""
        from .importacao import importar_grade_csv

        with open(arquivo, encoding="utf-8-sig") as fh:
            criadas, erros = importar_grade_csv(fh.read())
        click.echo(f"{criadas} aula(s) importada(s).")
        for e in erros:
            click.echo(e, err=True)
