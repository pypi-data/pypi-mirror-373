from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable, Paragraph


class RiskScale(Flowable):
    def __init__(self, risk, para_style, text=None):
        super().__init__()
        self.risk = risk
        self.risk_text = "The actual risk can vary significantly if you cash in at an early stage and you may get back less. You may not be able to sell your product easily or you may have to sell at a price that significantly impacts on how much you get back."
        self.additional_text = text
        self.para_style = para_style
        self.height = 3.564 * cm
        if text:
            self.height += 18

    def draw(self):
        width = 0.4 * cm
        gap = 1.177 * cm

        y = self.height - 0.868 * cm
        x_offset = 0.883 * cm
        self.canv.setFillColor(HexColor(0x9EA3AC))
        for x in range(7):
            _x = x * gap + x_offset
            if x == self.risk - 1:
                self.canv.setFillColor(HexColor(0x3C4859))
                self.canv.circle(_x, y, width, fill=True, stroke=False)
                self.canv.setFillColor(HexColor(0x9EA3AC))
            else:
                self.canv.circle(_x, y, width, fill=True, stroke=False)

            self.canv.setFillColor(white)
            self.canv.setFont("customfont-bd", 11)
            self.canv.drawCentredString(_x, y - 4, str(x + 1))
            self.canv.setFillColor(HexColor(0x9EA3AC))

        self.canv.setFillColor(HexColor(0x6D7683))
        self.canv.setStrokeColor(HexColor(0x6D7683))

        arrow_offset = 0.2 * cm

        p = self.canv.beginPath()
        origin = (x_offset - arrow_offset, y - 0.868 * cm)
        p.moveTo(*origin)
        p.lineTo(origin[0] + 0.059 * cm, origin[1] + 0.08 * cm)
        p.lineTo(origin[0] - 0.165 * cm, origin[1])
        p.lineTo(origin[0] + 0.059 * cm, origin[1] - 0.08 * cm)
        self.canv.drawPath(p, fill=True, stroke=False)

        p = self.canv.beginPath()
        origin = (6 * gap + x_offset + arrow_offset, y - 0.868 * cm)
        p.moveTo(origin[0], origin[1])
        p.lineTo(origin[0] - 0.059 * cm, origin[1] + 0.08 * cm)
        p.lineTo(origin[0] + 0.165 * cm, origin[1])
        p.lineTo(origin[0] - 0.059 * cm, origin[1] - 0.08 * cm)
        self.canv.drawPath(p, fill=True, stroke=False)

        self.canv.setLineWidth(0.02 * cm)
        p = self.canv.beginPath()
        self.canv.line(
            x_offset - arrow_offset,
            y - 0.868 * cm,
            6 * gap + x_offset + arrow_offset,
            y - 0.868 * cm,
        )

        self.canv.setFont("customfont", 6)
        self.canv.setFillColor(black)
        self.canv.drawString(x_offset - arrow_offset - 0.165 * cm, y - 1.2 * cm, "LOWER RISK")

        text_width = stringWidth("HIGHER RISK", "customfont", 6)
        self.canv.drawString(
            6 * gap + x_offset + arrow_offset + 0.165 * cm - text_width,
            y - 1.2 * cm,
            "HIGHER RISK",
        )

        para = Paragraph(self.risk_text, style=self.para_style)
        para.wrapOn(self.canv, 250, 8.954 * cm)
        para.drawOn(self.canv, 0, y - 2.5 * cm)

        if self.additional_text:
            para = Paragraph(f"<i>* {self.additional_text}</i>", style=self.para_style)

            para.wrapOn(self.canv, 250, 8.954 * cm)
            para.drawOn(self.canv, 0, y - 3.2 * cm)
