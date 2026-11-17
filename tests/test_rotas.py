"""Testes de integração: fluxos completos via HTTP."""
import io

from app.models import Anexo, Ausencia, Historico, Reposicao
from tests.conftest import login


def lancar(client, dados, **extra):
    form = {"data": dados["segunda"].isoformat(), "professor_id": dados["ana"].id, "disciplina_id": dados["alg"].id,
            "turma_id": dados["t1"].id, "horario_inicio": "19:00", "horario_fim": "20:40", "motivo": "saude"}
    form.update(extra)
    return client.post("/ausencias/lancamento", data=form, follow_redirects=True)


def test_login_invalido(app, dados):
    r = app.test_client().post("/login", data={"email": "sec@t.br", "senha": "errada"})
    assert "inválidos" in r.get_data(as_text=True)


def test_rotas_exigem_login(app, dados):
    r = app.test_client().get("/dashboard/")
    assert r.status_code == 302 and "/login" in r.location


def test_professor_nao_acessa_dashboard(professora):
    assert professora.get("/dashboard/").status_code == 403


def test_lancamento_manual_e_duplicidade(secretaria, dados):
    r = lancar(secretaria, dados)
    assert "1 ausência(s) registrada(s)" in r.get_data(as_text=True)
    r = lancar(secretaria, dados)
    assert "Já existe ausência" in r.get_data(as_text=True)
    assert Ausencia.query.count() == 1
    assert Historico.query.filter_by(acao="Ausência registrada").count() == 1


def test_lancamento_horario_invalido(secretaria, dados):
    r = lancar(secretaria, dados, horario_inicio="21:00", horario_fim="20:00")
    assert "anterior ao de término" in r.get_data(as_text=True)
    assert Ausencia.query.count() == 0


def test_lancamento_rapido_pela_grade(secretaria, dados):
    pagina = secretaria.get(f"/ausencias/lancamento?data={dados['segunda'].isoformat()}").get_data(as_text=True)
    assert "Algoritmos" in pagina and "Banco de Dados" in pagina
    from app.models import Aula
    ids = [a.id for a in Aula.query.filter_by(dia_semana=0)]
    secretaria.post("/ausencias/lancamento", data={"data": dados["segunda"].isoformat(), "aula_ids": ids,
                                                   "motivo": "pessoal"})
    assert Ausencia.query.count() == 2


def test_fluxo_substituicao(secretaria, dados):
    lancar(secretaria, dados)
    a = Ausencia.query.first()
    painel = secretaria.get(f"/substituicoes/?data={dados['segunda'].isoformat()}").get_data(as_text=True)
    assert "Carla" in painel
    r = secretaria.post(f"/substituicoes/{a.id}", data={"substituto_id": dados["carla"].id}, follow_redirects=True)
    assert "Substituto atribuído" in r.get_data(as_text=True)
    assert a.substituicao.substituto.nome == "Carla"
    r = secretaria.post(f"/substituicoes/{a.id}", data={"substituto_id": dados["bruno"].id}, follow_redirects=True)
    assert "indisponível" in r.get_data(as_text=True)


def test_professor_envia_atestado_e_coordenacao_aprova(app, secretaria, professora, dados):
    lancar(secretaria, dados)
    a = Ausencia.query.first()
    r = professora.post(f"/ausencias/{a.id}/anexos", data={"tipo": "atestado",
                        "arquivo": (io.BytesIO(b"%PDF-1.4 teste"), "atestado.pdf")},
                        content_type="multipart/form-data", follow_redirects=True)
    assert "Documento enviado" in r.get_data(as_text=True)
    anexo = Anexo.query.one()
    assert anexo.status == "pendente"
    assert professora.get(f"/anexos/{anexo.id}").data == b"%PDF-1.4 teste"
    secretaria.post(f"/anexos/{anexo.id}/avaliar", data={"status": "aprovado"})
    assert Anexo.query.one().status == "aprovado"


def test_upload_formato_invalido(secretaria, professora, dados):
    lancar(secretaria, dados)
    a = Ausencia.query.first()
    r = professora.post(f"/ausencias/{a.id}/anexos", data={"tipo": "atestado",
                        "arquivo": (io.BytesIO(b"x"), "virus.exe")},
                        content_type="multipart/form-data", follow_redirects=True)
    assert "Formato não permitido" in r.get_data(as_text=True)
    assert Anexo.query.count() == 0


def test_professor_nao_ve_ausencia_de_outro(app, secretaria, dados):
    lancar(secretaria, dados, professor_id=dados["bruno"].id, disciplina_id=dados["bd"].id, turma_id=dados["t2"].id)
    a = Ausencia.query.first()
    c = app.test_client()
    login(c, "ana@t.br")
    assert c.get(f"/ausencias/{a.id}").status_code == 403


def test_reposicao_com_comprovante(secretaria, professora, dados):
    lancar(secretaria, dados)
    a = Ausencia.query.first()
    professora.post(f"/ausencias/{a.id}/reposicoes", data={"data": dados["segunda"].isoformat(),
                    "horario_inicio": "17:00", "horario_fim": "18:40", "local": "Sala 3"})
    rep = Reposicao.query.one()
    assert rep.status == "agendada"
    professora.post(f"/ausencias/{a.id}/anexos", data={"tipo": "comprovante_reposicao", "reposicao_id": rep.id,
                    "arquivo": (io.BytesIO(b"lista"), "lista-presenca.jpg")}, content_type="multipart/form-data")
    anexo = Anexo.query.one()
    secretaria.post(f"/anexos/{anexo.id}/avaliar", data={"status": "aprovado"})
    assert Reposicao.query.one().status == "realizada"


def test_dashboard_e_pdf(secretaria, dados):
    lancar(secretaria, dados)
    seg = dados["segunda"].isoformat()
    r = secretaria.get(f"/dashboard/?inicio={seg}&fim={seg}")
    assert r.status_code == 200 and "Taxa de substituição" in r.get_data(as_text=True)
    r = secretaria.get(f"/relatorios/pdf?inicio={seg}&fim={seg}&professor_id={dados['ana'].id}")
    assert r.status_code == 200 and r.mimetype == "application/pdf" and r.data.startswith(b"%PDF")


def test_api_json(secretaria, dados):
    lancar(secretaria, dados)
    seg = dados["segunda"].isoformat()
    itens = secretaria.get(f"/api/ausencias?inicio={seg}&fim={seg}").get_json()
    assert itens[0]["professor"] == "Ana" and itens[0]["classificacao"] == "pendente"


def test_importacao_csv(secretaria, dados):
    csv = ("professor;email;disciplina_codigo;disciplina_nome;turma;curso;turno;dia_semana;inicio;fim\n"
           "Elisa;elisa@t.br;WEB;Desenvolvimento Web;ADS-3A;ADS;Noite;3;19:00;20:40\n"
           "Linha;quebrada\n")
    r = secretaria.post("/cadastros/importar", data={"arquivo": (io.BytesIO(csv.encode()), "grade.csv")},
                        content_type="multipart/form-data", follow_redirects=True)
    texto = r.get_data(as_text=True)
    assert "1 aula(s) importada(s)" in texto and "Linha 3" in texto


def test_paginas_responsivas_tem_viewport(secretaria):
    assert 'name="viewport"' in secretaria.get("/ausencias/lancamento").get_data(as_text=True)
