from reportlab.graphics import renderPDF
from reportlab.lib.colors import black
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable, Image, Paragraph, Table, TableStyle
from svglib.svglib import svg2rlg


class TextBox(Flowable):
    def __init__(
        self,
        width,
        height,
        text,
        text_style,
        box_color,
        grid_width=0.30 * cm,
        offset=None,
        debug=False,
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.offset = offset or 0
        self.grid_width = grid_width

        self.text_table = Table([[Paragraph(text, style=text_style)]], rowHeights=[height - grid_width])
        table_styles = [
            ("BACKGROUND", (0, 0), (0, 0), box_color),
            ("GRID", (0, 0), (0, 0), grid_width, box_color),
            ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
        ]

        if debug:
            table_styles.extend(
                [
                    ("BOX", (0, 0), (-1, -1), 0.25, black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, black),
                ]
            )

        self.text_table.setStyle(TableStyle(table_styles))

    def draw(self):
        self.text_table.wrapOn(self.canv, self.width - self.grid_width - self.offset, self.height)
        self.text_table.drawOn(self.canv, (self.offset or 0) + (self.grid_width / 2), (self.grid_width / 2))


class TextBoxWithImage(TextBox):
    def __init__(
        self,
        width,
        height,
        img,
        img_x,
        img_y,
        img_width,
        img_height,
        text,
        text_style,
        box_color,
        grid_width=0.28 * cm,
        svg=False,
        offset=None,
        debug=False,
    ):
        super().__init__(width, height, text, text_style, box_color, grid_width, offset, debug)
        self.img = img
        self.img_x = img_x
        self.img_y = img_y
        self.img_width = img_width
        self.img_height = img_height
        self.svg = svg

    def draw(self):
        super().draw()

        if self.svg:
            raise NotImplementedError("SVG is not yet implemented.")
        else:
            img = Image(self.img)
            img.drawWidth = self.img_width
            img.drawHeight = self.img_height
            img.drawOn(self.canv, self.img_x, self.img_y)


class TextWithIcon(Flowable):
    def __init__(self, width, height, text, font, font_size, icon=None):
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.font_size = font_size
        self.icon = icon
        self.svg = None
        if icon:
            self.svg = self.icon.name.split(".")[-1] in ["svg", "SVG"]

    def draw(self):
        # Get text width and set font
        text_width = stringWidth(self.text, self.font, self.font_size)
        self.canv.setFont(self.font, self.font_size, leading=self.font_size)

        # Get icon
        icon = None
        if self.svg:
            icon = svg2rlg(self.icon)
        elif self.icon and self.icon.name:
            icon = Image(self.icon)

        tx = self.width / (4 if icon else 2) - text_width / 2
        ty = self.height / 2 - self.font_size / 2
        self.canv.drawString(tx, ty, self.text)

        if icon:
            if self.svg:
                icon_width = icon.width
                icon_height = icon.height
            else:
                icon_width = icon.imageWidth
                icon_height = icon.imageHeight

            drawing_height = self.height / 2
            scale = drawing_height / icon_height
            drawing_width = icon_width * scale

            allowed_width = (self.width / 2) - 0.2 * cm

            if drawing_width > allowed_width:
                drawing_width = allowed_width
                scale = drawing_width / icon_width
                drawing_height = icon_height * scale

            dx = (self.width / 4) * 3 - (icon_width * scale) / 2
            dy = (self.height - drawing_height) / 2

            if self.svg:
                icon.scale(scale, scale)
                renderPDF.draw(icon, self.canv, dx, dy)
            else:
                icon.drawWidth = drawing_width
                icon.drawHeight = drawing_height
                icon.drawOn(self.canv, dx, dy)
