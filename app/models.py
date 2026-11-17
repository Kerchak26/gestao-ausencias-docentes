"""Modelo de dados do módulo (ver docs/02-modelagem.md)."""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

PERFIS = ("secretaria", "coordenador", "professor")
DIAS_SEMANA = ("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo")


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey("professor.id"))
    professor = db.relationship("Professor")

    def definir_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)


class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    ativo = db.Column(db.Boolean, default=True, nullable=False)


class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(120), nullable=False)


class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    curso = db.Column(db.String(120))
    turno = db.Column(db.String(20))


class Aula(db.Model):
    """Grade horária: aula recorrente semanal (integração com o sistema acadêmico)."""

    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey("professor.id"), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey("disciplina.id"), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey("turma.id"), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0 = segunda ... 6 = domingo
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)

    professor = db.relationship("Professor")
    disciplina = db.relationship("Disciplina")
    turma = db.relationship("Turma")


class Ausencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey("professor.id"), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey("disciplina.id"), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey("turma.id"), nullable=False)
    data = db.Column(db.Date, nullable=False, index=True)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.String(40), nullable=False)
    observacao = db.Column(db.Text)
    registrado_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    criado_em = db.Column(db.DateTime, default=datetime.now, nullable=False)

    professor = db.relationship("Professor")
    disciplina = db.relationship("Disciplina")
    turma = db.relationship("Turma")
    registrado_por = db.relationship("Usuario")
    substituicao = db.relationship("Substituicao", uselist=False, back_populates="ausencia", cascade="all, delete-orphan")
    reposicoes = db.relationship("Reposicao", back_populates="ausencia", cascade="all, delete-orphan", order_by="Reposicao.data")
    anexos = db.relationship("Anexo", back_populates="ausencia", cascade="all, delete-orphan")


class Substituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ausencia_id = db.Column(db.Integer, db.ForeignKey("ausencia.id"), unique=True, nullable=False)
    substituto_id = db.Column(db.Integer, db.ForeignKey("professor.id"), nullable=False)
    observacao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.now, nullable=False)

    ausencia = db.relationship("Ausencia", back_populates="substituicao")
    substituto = db.relationship("Professor")


class Reposicao(db.Model):
    STATUS = ("agendada", "realizada", "cancelada")

    id = db.Column(db.Integer, primary_key=True)
    ausencia_id = db.Column(db.Integer, db.ForeignKey("ausencia.id"), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    local = db.Column(db.String(60))
    status = db.Column(db.String(20), default="agendada", nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now, nullable=False)

    ausencia = db.relationship("Ausencia", back_populates="reposicoes")
    anexos = db.relationship("Anexo", back_populates="reposicao")


class Anexo(db.Model):
    """Atestados, declarações e comprovantes de reposição."""

    TIPOS = {
        "atestado": "Atestado médico",
        "declaracao": "Declaração / justificativa",
        "comprovante_reposicao": "Comprovante de reposição",
    }
    STATUS = ("pendente", "aprovado", "recusado")

    id = db.Column(db.Integer, primary_key=True)
    ausencia_id = db.Column(db.Integer, db.ForeignKey("ausencia.id"), nullable=False)
    reposicao_id = db.Column(db.Integer, db.ForeignKey("reposicao.id"))
    tipo = db.Column(db.String(30), nullable=False)
    nome_original = db.Column(db.String(255), nullable=False)
    arquivo = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="pendente", nullable=False)
    enviado_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    criado_em = db.Column(db.DateTime, default=datetime.now, nullable=False)

    ausencia = db.relationship("Ausencia", back_populates="anexos")
    reposicao = db.relationship("Reposicao", back_populates="anexos")
    enviado_por = db.relationship("Usuario")


class Historico(db.Model):
    """Trilha de auditoria (rastreabilidade de todas as ações)."""

    id = db.Column(db.Integer, primary_key=True)
    ausencia_id = db.Column(db.Integer, db.ForeignKey("ausencia.id"), index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    acao = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now, nullable=False)

    usuario = db.relationship("Usuario")
