import io
from typing import Any, Dict, Optional
import qrcode

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para adicionar numeração de páginas dinâmico (Página X de Y).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list = []
        self._startPage: int = 1
        self._pageNumber: int = 1

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage = getattr(self, "_pageNumber", 1)
        self._pageNumber += 1

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int) -> None:
        self.saveState()
        self.setFont("Helvetica", 9)
        page_text = f"Página {self._pageNumber} de {page_count}"
        # Posiciona a contagem alinhada à direita respeitando a margem da folha letter
        self.drawRightString(letter[0] - 36, 15, page_text)
        self.restoreState()


def generate_qr_code(batch_id: int) -> io.BytesIO:
    """Gera um QR Code em memória para validação do documento"""
    qr = qrcode.make(f"https://sicc.empresa.com.br/validar/{batch_id}")
    qr_buffer = io.BytesIO()
    # Ajuste: passa 'PNG' como argumento posicional em vez de format='PNG'
    qr.save(qr_buffer, "PNG")
    qr_buffer.seek(0)
    return qr_buffer


def generate_pdf_report(
    assay_data: Dict[str, Any],
    validation_results: Dict[str, Any],
    batch_id: Optional[int] = 1,
) -> io.BytesIO:
    """
    Gera o relatório em PDF e devolve um buffer em memória (BytesIO).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=45,
    )
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        alignment=1,
        textColor=colors.HexColor("#1E3A8A"),
    )
    cell_header_style = ParagraphStyle(
        "CellHeader",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        fontName="Helvetica-Bold",
        textColor=colors.whitesmoke,
        alignment=1,
    )
    cell_body_style = ParagraphStyle(
        "CellBody",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=1,
    )

    concessionaire_name = str(assay_data.get("concessionaire", "")).upper()

    # 1. Cabeçalho com Título
    story.append(
        Paragraph(
            f"<b>RELATÓRIO TÉCNICO DE CONFORMIDADE — {concessionaire_name}</b>",
            title_style,
        )
    )
    story.append(Spacer(1, 10))

    # 2. QR Code e Informações do Lote
    status_str = str(validation_results.get("status_geral", "Pendente"))
    status_color = (
        "green" if status_str == "Aprovado para Comercialização" else "red"
    )

    client_code = assay_data.get("client_code", "-")
    concessionaire = assay_data.get("concessionaire", "-")

    info_html = f"""
    <b>Código Cliente / Bitola:</b> {client_code}<br/>
    <b>Concessionária:</b> {concessionaire}<br/>
    <b>Status Geral:</b> <font color="{status_color}"><b>{status_str}</b></font>
    """

    actual_batch_id = batch_id if batch_id is not None else 1
    qr_img = Image(generate_qr_code(actual_batch_id), width=50, height=50)

    header_table = Table(
        [[Paragraph(info_html, styles["Normal"]), qr_img]],
        colWidths=[480, 60],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 12))

    # 3. Tabela de Ensaios
    table_data = [
        [
            Paragraph("Ensaio", cell_header_style),
            Paragraph("Referência Normativa", cell_header_style),
            Paragraph("Valor Medido", cell_header_style),
            Paragraph("Resultado", cell_header_style),
        ]
    ]

    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]

    items = assay_data.get("items", [])
    for idx, item in enumerate(items, start=1):
        item_status = str(item.get("status", ""))
        table_data.append(
            [
                Paragraph(str(item.get("assay_name", "")), cell_body_style),
                Paragraph(str(item.get("norm_reference", "")), cell_body_style),
                Paragraph(str(item.get("measured_value", "")), cell_body_style),
                Paragraph(f"<b>{item_status}</b>", cell_body_style),
            ]
        )

        if "Rejeitado" in item_status or "Alerta" in item_status:
            table_styles.append(
                (
                    "BACKGROUND",
                    (0, idx),
                    (-1, idx),
                    colors.HexColor("#FEE2E2"),
                )
            )
            table_styles.append(
                (
                    "TEXTCOLOR",
                    (3, idx),
                    (3, idx),
                    colors.HexColor("#991B1B"),
                )
            )

    t = Table(table_data, colWidths=[140, 160, 100, 140])
    t.setStyle(TableStyle(table_styles))
    story.append(t)
    story.append(Spacer(1, 25))

    # 4. Bloco de Assinatura
    sig_text = """
    __________________________________________________<br/>
    <b>Assinatura Digital do Responsável Técnico</b><br/>
    Engenharia de Qualidade e Conformidade
    """
    story.append(
        Paragraph(
            sig_text,
            ParagraphStyle(
                "SigStyle",
                parent=styles["Normal"],
                alignment=1,
                fontSize=8,
                leading=11,
            ),
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer