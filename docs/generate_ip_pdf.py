from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    HRFlowable,
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PDF = ROOT / "docs" / "ip_briefing_dashboard.pdf"
SCREENSHOT = (
    ROOT
    / "assets"
    / "c__Users_lucas_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-457db75e-935a-4e11-9597-d0d796ba9695.png"
)


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=27,
            textColor=colors.HexColor("#0f2a5f"),
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f2a5f"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#111827"),
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
        ),
        "pill": ParagraphStyle(
            "pill",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=colors.white,
            alignment=1,
        ),
    }


def section_bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    flow_items = [ListItem(Paragraph(i, style), leftIndent=12) for i in items]
    return ListFlowable(flow_items, bulletType="bullet", leftIndent=8, bulletFontSize=8)


def build_pdf() -> None:
    styles = make_styles()
    table_cell = ParagraphStyle(
        "table_cell",
        parent=styles["body"],
        fontSize=9.5,
        leading=11.5,
        spaceAfter=0,
    )
    table_head = ParagraphStyle(
        "table_head",
        parent=styles["body"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=11.5,
        textColor=colors.white,
        spaceAfter=0,
    )
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )
    story = []

    story.append(Paragraph("Lung Cancer AI Platform", styles["title"]))
    story.append(Paragraph("Resumen ejecutivo para IP | Version demo funcional", styles["subtitle"]))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#93c5fd"), thickness=1))
    story.append(Spacer(1, 8))

    kpi = Table(
        [
            [
                Paragraph("Estado", table_head),
                Paragraph("Fuentes", table_head),
                Paragraph("Nivel actual", table_head),
                Paragraph("Uso principal", table_head),
            ],
            [
                Paragraph("MVP funcional", table_cell),
                Paragraph("TCGA LUAD/LUSC (publico)", table_cell),
                Paragraph("Exploratorio + reproducido computacionalmente", table_cell),
                Paragraph("Priorizacion de hipotesis", table_cell),
            ],
        ],
        colWidths=[2.8 * cm, 4.2 * cm, 5.6 * cm, 4.0 * cm],
    )
    kpi.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#eff6ff")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(kpi)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Que hace la web", styles["h2"]))
    story.append(
        section_bullets(
            [
                "Visor de pipeline: confirma estado de ejecucion y artefactos.",
                "Trazabilidad de datos: muestra fuentes, descargas y checksums.",
                "Priorizacion de dianas: ranking de candidatos por subtipo.",
                "Carga de datos: prueba interactiva con CSV/TSV reales.",
            ],
            styles["body"],
        )
    )

    story.append(Paragraph("Que valor da al grupo", styles["h2"]))
    story.append(
        section_bullets(
            [
                "Reduce tiempo de cribado inicial y mejora foco experimental.",
                "Aporta trazabilidad tecnica para decisiones y reportes.",
                "Permite repetir analisis con consistencia computacional.",
                "Se puede ejecutar en entorno interno del laboratorio.",
            ],
            styles["body"],
        )
    )

    story.append(Paragraph("Que NO afirma esta demo", styles["h2"]))
    story.append(
        section_bullets(
            [
                "No reemplaza validacion biologica o clinica.",
                "No genera conclusiones causales por si sola.",
                "No sustituye modelos preclinicos del grupo.",
            ],
            styles["body"],
        )
    )

    story.append(Paragraph("Escala de evidencia", styles["h2"]))
    evidence = Table(
        [
            [
                Paragraph("Nivel", table_head),
                Paragraph("Significado", table_head),
                Paragraph("Estado actual", table_head),
            ],
            [
                Paragraph("Exploratorio", table_cell),
                Paragraph("Hallazgo inicial en un dataset", table_cell),
                Paragraph("Si", table_cell),
            ],
            [
                Paragraph("Reproducido computacionalmente", table_cell),
                Paragraph("Resultado consistente en corridas", table_cell),
                Paragraph("Si", table_cell),
            ],
            [
                Paragraph("Validado experimentalmente", table_cell),
                Paragraph("Confirmacion en modelos del laboratorio", table_cell),
                Paragraph("Pendiente", table_cell),
            ],
        ],
        colWidths=[4.2 * cm, 8.3 * cm, 2.9 * cm],
    )
    evidence.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(evidence)

    if SCREENSHOT.exists():
        story.append(Spacer(1, 10))
        story.append(Paragraph("Vista de la aplicacion", styles["h2"]))
        img = Image(str(SCREENSHOT))
        img.drawWidth = 12.8 * cm
        img.drawHeight = img.drawHeight * (12.8 * cm / img.drawWidth)
        story.append(img)

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#cbd5e1"), thickness=0.8))
    story.append(Spacer(1, 5))
    story.append(
        Paragraph(
            "Autor: Lucas Chabrera Querol | Proyecto abierto para mejora continua",
            styles["small"],
        )
    )

    # Pagina 2: detalle tecnico
    story.append(PageBreak())
    story.append(Paragraph("Detalle tecnico del sistema", styles["title"]))
    story.append(
        Paragraph(
            "Como funciona internamente la plataforma y por que puede integrarse en estudios del laboratorio.",
            styles["subtitle"],
        )
    )
    story.append(HRFlowable(width="100%", color=colors.HexColor("#93c5fd"), thickness=1))
    story.append(Spacer(1, 8))

    story.append(Paragraph("TL;DR tecnico", styles["h2"]))
    tldr = Table(
        [
            [
                Paragraph("Motor IA principal", table_head),
                Paragraph("Cuando entra en accion", table_head),
                Paragraph("Por que se usa", table_head),
            ],
            [
                Paragraph("RandomForest + ElasticNet", table_cell),
                Paragraph("En el entrenamiento de `target_model.py`", table_cell),
                Paragraph("Ranking robusto combinando no linealidad e interpretabilidad", table_cell),
            ],
        ],
        colWidths=[4.4 * cm, 5.2 * cm, 5.8 * cm],
    )
    tldr.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#eff6ff")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(tldr)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Pipeline completo (de datos a decision)", styles["h2"]))
    story.append(
        Paragraph(
            "1) Fuentes publicas/propias -> 2) Descarga trazable (`sources.json`, `download_manifest.json`) "
            "-> 3) Preprocesado normalizado -> 4) Integracion de tablas -> 5) Modelo IA y ranking "
            "-> 6) Visualizacion y priorizacion en dashboard.",
            styles["body"],
        )
    )

    story.append(Paragraph("Motor IA: que usa, cuando y por que", styles["h2"]))
    story.append(
        section_bullets(
            [
                "Modelo 1: RandomForestRegressor para capturar relaciones no lineales e interacciones.",
                "Modelo 2: ElasticNetCV para regularizacion y estabilidad en espacios de features amplios.",
                "Entrada en accion: durante ejecucion de `src/models/target_model.py`.",
                "Salida: ranking con `consensus_score` que combina ambos modelos.",
            ],
            styles["body"],
        )
    )

    story.append(Paragraph("Rol de la pestaña 'Carga de datos (demo)'", styles["h2"]))
    story.append(
        section_bullets(
            [
                "Genera ranking exploratorio inmediato con el CSV/TSV subido.",
                "No sustituye validacion biologica ni clinica.",
                "Sirve para filtrar hipotesis iniciales antes de invertir recursos experimentales.",
            ],
            styles["body"],
        )
    )

    story.append(Paragraph("Escalabilidad, actualizacion y adaptabilidad", styles["h2"]))
    story.append(
        section_bullets(
            [
                "Escalable: arquitectura modular por componentes (`data`, `models`, `dashboard`).",
                "Actualizable: nuevas fuentes y releases se incorporan via `sources.json` sin rehacer el sistema.",
                "Adaptable: permite sustituir datos publicos por datasets internos del laboratorio.",
                "Integrable: ejecucion en local o infraestructura interna para mantener privacidad.",
            ],
            styles["body"],
        )
    )

    story.append(Paragraph("Riesgo/limitacion actual y mitigacion", styles["h2"]))
    risk = Table(
        [
            [
                Paragraph("Limitacion actual", table_head),
                Paragraph("Mitigacion propuesta", table_head),
            ],
            [
                Paragraph("La demo actual no incluye validacion experimental (wet lab).", table_cell),
                Paragraph(
                    "Usar el ranking como capa de priorizacion y validar en lineas/modelos del grupo.",
                    table_cell,
                ),
            ],
            [
                Paragraph("Endpoint de demo no representa toda la complejidad translacional.", table_cell),
                Paragraph(
                    "Adaptar endpoints a resistencia y respuesta terapeutica definidos por la IP.",
                    table_cell,
                ),
            ],
        ],
        colWidths=[7.0 * cm, 8.4 * cm],
    )
    risk.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(risk)

    story.append(Spacer(1, 7))
    story.append(
        Paragraph(
            "Conclusion tecnica: el sistema ya es util como base reproducible para priorizacion. "
            "El siguiente salto de valor se produce al conectarlo con endpoints y validaciones del propio laboratorio.",
            styles["body"],
        )
    )

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
