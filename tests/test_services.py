"""Testes unitários das regras de negócio."""
from datetime import date, datetime, time, timedelta

import pytest

from app.extensions import db
from app.models import Anexo, Ausencia, Reposicao, Substituicao
from app.services import (atribuir_substituto, classificar, filtrar_ausencias, indicadores, justificada,
                          sugerir_substitutos)


def nova_ausencia(dados, prof="ana", disc="alg", turma="t1", dia=None, ini=time(19), fim=time(20, 40)):
    a = Ausencia(professor_id=dados[prof].id, disciplina_id=dados[disc].id, turma_id=dados[turma].id,
                 data=dia or dados["segunda"], horario_inicio=ini, horario_fim=fim, motivo="saude")
    db.session.add(a)
    db.session.commit()
    return a


class TestClassificacao:
    def test_pendente_antes_do_fim_da_aula(self, dados):
        a = nova_ausencia(dados)
        antes = datetime.combine(a.data, time(19, 30))
        assert classificar(a, antes) == "pendente"

    def test_vaga_quando_aula_termina_sem_cobertura(self, dados):
        a = nova_ausencia(dados)
        depois = datetime.combine(a.data, time(21))
        assert classificar(a, depois) == "vaga"

    def test_substituida_tem_prioridade(self, dados):
        a = nova_ausencia(dados)
        db.session.add(Substituicao(ausencia_id=a.id, substituto_id=dados["carla"].id))
        db.session.add(Reposicao(ausencia_id=a.id, data=a.data, horario_inicio=time(18), horario_fim=time(19)))
        db.session.commit()
        assert classificar(a, datetime.combine(a.data, time(23))) == "substituida"

    def test_reposicao_agendada_e_realizada(self, dados):
        a = nova_ausencia(dados)
        rep = Reposicao(ausencia_id=a.id, data=a.data + timedelta(days=7), horario_inicio=time(18), horario_fim=time(19))
        db.session.add(rep)
        db.session.commit()
        depois = datetime.combine(a.data, time(23))
        assert classificar(a, depois) == "reposicao_agendada"
        rep.status = "realizada"
        db.session.commit()
        assert classificar(a, depois) == "reposta"

    def test_reposicao_cancelada_volta_a_vaga(self, dados):
        a = nova_ausencia(dados)
        db.session.add(Reposicao(ausencia_id=a.id, data=a.data, horario_inicio=time(18), horario_fim=time(19),
                                 status="cancelada"))
        db.session.commit()
        assert classificar(a, datetime.combine(a.data, time(23))) == "vaga"


class TestSubstitutos:
    def test_exclui_ausente_e_quem_tem_aula_no_horario(self, dados):
        a = nova_ausencia(dados)
        nomes = [p.nome for p in sugerir_substitutos(a)]
        assert "Ana" not in nomes      # ausente
        assert "Bruno" not in nomes    # tem aula no mesmo horário
        assert set(nomes) == {"Carla", "Diego"}

    def test_prioriza_quem_leciona_a_mesma_disciplina(self, dados):
        a = nova_ausencia(dados)
        assert sugerir_substitutos(a)[0].nome == "Carla"

    def test_quem_ja_substitui_no_horario_fica_indisponivel(self, dados):
        a1 = nova_ausencia(dados)
        a2 = nova_ausencia(dados, prof="bruno", disc="bd", turma="t2")
        atribuir_substituto(a1, dados["carla"].id)
        db.session.commit()
        assert [p.nome for p in sugerir_substitutos(a2)] == ["Diego"]

    def test_inativo_nao_e_sugerido(self, dados):
        dados["diego"].ativo = False
        db.session.commit()
        a = nova_ausencia(dados)
        assert "Diego" not in [p.nome for p in sugerir_substitutos(a)]

    def test_atribuir_indisponivel_gera_erro(self, dados):
        a = nova_ausencia(dados)
        with pytest.raises(ValueError):
            atribuir_substituto(a, dados["bruno"].id)

    def test_troca_de_substituto(self, dados):
        a = nova_ausencia(dados)
        atribuir_substituto(a, dados["carla"].id)
        db.session.commit()
        atribuir_substituto(a, dados["diego"].id)
        db.session.commit()
        assert a.substituicao.substituto.nome == "Diego"
        assert Substituicao.query.count() == 1


class TestIndicadoresEFiltros:
    def test_indicadores(self, dados):
        a1 = nova_ausencia(dados)
        nova_ausencia(dados, prof="bruno", disc="bd", turma="t2")
        atribuir_substituto(a1, dados["carla"].id)
        db.session.add(Anexo(ausencia_id=a1.id, tipo="atestado", nome_original="x.pdf", arquivo="x.pdf",
                             status="aprovado"))
        db.session.commit()
        ind = indicadores(Ausencia.query.all(), datetime.combine(dados["segunda"], time(23)))
        assert ind["total"] == 2
        assert ind["taxa_substituicao"] == 50.0
        assert ind["classes"]["vaga"] == 1
        assert ind["taxa_documentacao"] == 50.0
        assert ind["justificadas"] == 1
        assert justificada(a1)

    def test_indicadores_sem_dados(self, app):
        assert indicadores([])["taxa_substituicao"] == 0.0

    def test_filtros(self, dados):
        seg = dados["segunda"]
        nova_ausencia(dados)
        nova_ausencia(dados, prof="bruno", disc="bd", turma="t2", dia=seg + timedelta(days=7))
        assert len(filtrar_ausencias(inicio=seg, fim=seg)) == 1
        assert len(filtrar_ausencias(professor_id=dados["bruno"].id)) == 1
        assert len(filtrar_ausencias(turma_id=dados["t1"].id)) == 1
        assert len(filtrar_ausencias(classificacao="pendente")) == 2
