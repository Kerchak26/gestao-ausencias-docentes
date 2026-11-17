"""Geração do relatório em PDF (histórico de ausências e reposições)."""
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .services import CLASSIFICACOES, MOTIVOS, classificar, indicadores, justificada

AZUL = colors.HexColor("#1f4e79")


def _tabela(dados, larguras, cabecalho=True):
    t = Table(dados, colWidths=larguras, repeatRows=1 if cabecalho else 0)
    estilo = [
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5f9")]),
    ]
    if cabecalho:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
    t.setStyle(TableStyle(estilo))
    return t


def gerar_pdf(ausencias, descricao_filtros: str, agora: datetime | None = None) -> bytes:
    agora = agora or datetime.now()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            title="Relatório de ausências docentes", author="Secretaria de Coordenação")
    est = getSampleStyleSheet()
    pequeno = ParagraphStyle("pequeno", parent=est["Normal"], fontSize=8, leading=10)
    ind = indicadores(ausencias, agora)

    elementos = [
        Paragraph("Relatório de Ausências Docentes e Reposições", est["Title"]),
        Paragraph(f"Filtros: {descricao_filtros}", est["Normal"]),
        Paragraph(f"Gerado em {agora:%d/%m/%Y %H:%M}", est["Normal"]),
        Spacer(1, 0.4 * cm),
        Paragraph("Indicadores", est["Heading2"]),
        _tabela([
            ["Total de ausências", "Substituídas", "Taxa de substituição", "Aulas vagas sem cobertura",
             "Reposições agendadas", "Reposições realizadas", "Com documento"],
            [ind["total"], ind["classes"]["substituida"], f'{ind["taxa_substituicao"]}%', ind["classes"]["vaga"],
             ind["reposicoes_agendadas"], ind["reposicoes_realizadas"], f'{ind["taxa_documentacao"]}%'],
        ], [3.8 * cm] * 7),
        Spacer(1, 0.4 * cm),
    ]

    if ind["por_professor"]:
        elementos += [Paragraph("Ausências por professor", est["Heading2"]),
                      _tabela([["Professor", "Ausências"]] + [list(x) for x in ind["por_professor"]], [10 * cm, 3 * cm]),
                      Spacer(1, 0.4 * cm)]

    elementos.append(Paragraph("Histórico detalhado", est["Heading2"]))
    linhas = [["Data", "Horário", "Professor", "Disciplina", "Turma", "Motivo", "Situação", "Substituto",
               "Reposições", "Documentos"]]
    for a in sorted(ausencias, key=lambda x: (x.data, x.horario_inicio)):
        reposicoes = "<br/>".join(f"{r.data:%d/%m} {r.horario_inicio:%H:%M} ({r.status})" for r in a.reposicoes) or "—"
        docs = f"{len(a.anexos)} ({'justificada' if justificada(a) else 'não justificada'})" if a.anexos else "—"
        linhas.append([
            a.data.strftime("%d/%m/%Y"), f"{a.horario_inicio:%H:%M}–{a.horario_fim:%H:%M}",
            Paragraph(a.professor.nome, pequeno), Paragraph(a.disciplina.nome, pequeno), a.turma.nome,
            Paragraph(MOTIVOS.get(a.motivo, a.motivo), pequeno),
            Paragraph(CLASSIFICACOES[classificar(a, agora)], pequeno),
            Paragraph(a.substituicao.substituto.nome if a.substituicao else "—", pequeno),
            Paragraph(reposicoes, pequeno), Paragraph(docs, pequeno),
        ])
    if len(linhas) == 1:
        elementos.append(Paragraph("Nenhuma ausência encontrada para os filtros selecionados.", est["Normal"]))
    else:
        elementos.append(_tabela(linhas, [1.9 * cm, 2.1 * cm, 3.6 * cm, 3.6 * cm, 1.8 * cm, 2.8 * cm,
                                          3 * cm, 3 * cm, 2.9 * cm, 2.2 * cm]))

    doc.build(elementos)
    return buf.getvalue()
