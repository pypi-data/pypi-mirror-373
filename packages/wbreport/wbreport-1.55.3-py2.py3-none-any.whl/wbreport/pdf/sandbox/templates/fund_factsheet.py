import itertools
from datetime import date
from decimal import Decimal
from io import BytesIO

from reportlab import platypus
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.formatters import DecimalFormatter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily, stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Image,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import KeepTogether, TopPadder
from reportlab.platypus.frames import Frame
from svglib.svglib import svg2rlg
from wbreport.models import ReportAsset
from wbreport.pdf.charts.pie import (
    get_pie_chart_horizontal,
    get_pie_chart_horizontal_height,
)
from wbreport.pdf.charts.timeseries import Scale, get_timeseries_chart
from wbreport.pdf.flowables.risk import RiskScale
from wbreport.pdf.flowables.textboxes import TextBox, TextBoxWithImage, TextWithIcon
from wbreport.pdf.tables.aggregated_tables import (
    get_fund_table,
    get_simple_aggregated_table,
)
from wbreport.pdf.tables.data_tables import get_simple_data_table


def generate_report(context):
    debug = False

    main_features_dict_tmp = context["information_table"]
    main_features_dict = {}
    for k, v in main_features_dict_tmp.items():
        main_features_dict.update(v)
    # Monthly returns table as dataframe, None is no value
    monthly_returns = context["monthly_returns"]

    # Pie chart Dataframe
    geographical = context["geographical_breakdown"]
    currencies = context["currency_exposure"]
    allocation = context["asset_allocation"]
    marketcap = context["market_cap_distribution"]
    liquidity = context["equity_liquidity"]
    industry = context["industry_exposure"]

    # Price time serie as dataframe
    prices = context["prices"]

    # TOPs as list

    top_10_holdings = context["holdings"][0:10]

    top_3_contributors = context["top_contributors"]
    bottom_3_contributors = context["worst_contributors"]

    # {'high': {'price':low, 'date':date}, 'low' : {'price':high, 'date':date}}
    all_time_dict = context["all_time"]
    end = context["date"]
    general_data = {}
    general_data["date"] = end.strftime("%b %Y")
    general_data["colors"] = context["colors_palette"]
    general_data["title"] = context["title"].replace("&", "&amp;")
    general_data["risk_scale"] = context["risk_scale"]

    general_data["introduction"] = context["introduction"]
    fund_table = context["funds_table"]
    calculated_risk_scale = context["risk_scale"]

    # Register Fonts
    pdfmetrics.registerFont(TTFont("customfont", ReportAsset.objects.get(key="font-default").asset))
    pdfmetrics.registerFont(TTFont("customfont-bd", ReportAsset.objects.get(key="font-bd").asset))
    pdfmetrics.registerFont(TTFont("customfont-it", ReportAsset.objects.get(key="font-it").asset))
    registerFontFamily("customfont", normal="customfont", bold="customfont-bd", italic="customfont-it")

    # Page Variables
    LINEHEIGHT = 12

    HEADER_HEIGHT = 2.34 * cm
    FOOTER_HEIGHT = 2.34 * cm

    SIDE_MARGIN = 0.96 * cm
    TOP_MARGIN = 3.63 * cm
    CONTENT_OFFSET = 0.34 * cm
    CONTENT_MARGIN = SIDE_MARGIN + CONTENT_OFFSET

    CONTENT_HEIGHT = 22.25 * cm
    CONTENT_WIDTH_PAGE1_LEFT = 13.84 * cm
    CONTENT_WIDTH_PAGE1_RIGHT = 4.23 * cm
    CONTENT_WIDTH_PAGE2 = A4[0] - SIDE_MARGIN - CONTENT_MARGIN

    CONTENT_X_PAGE1_RIGHT = A4[0] - CONTENT_MARGIN - CONTENT_WIDTH_PAGE1_RIGHT
    CONTENT_Y = A4[1] - CONTENT_HEIGHT - TOP_MARGIN

    TABLE_MARGIN_PAGE2 = 0.56 * cm

    output = BytesIO()
    doc = BaseDocTemplate(
        output,
        pagesize=A4,
        rightMargin=0,
        leftMargin=0,
        topMargin=0,
        bottomMargin=0,
        title=general_data["title"],
        author="Atonra Partners SA",
    )
    elements = []

    s_base = ParagraphStyle(name="s_base", fontName="customfont", fontSize=9, leading=10)
    s_base_small_justified = ParagraphStyle(
        name="s_base_small_justified", parent=s_base, fontSize=6.5, leading=7, alignment=TA_JUSTIFY
    )
    s_base_small_justified_indent = ParagraphStyle(
        name="s_base_small_justified_indent", parent=s_base_small_justified, leftIndent=CONTENT_OFFSET
    )
    s_base_indent = ParagraphStyle(name="s_description", parent=s_base, spaceBefore=8, leftIndent=CONTENT_OFFSET)
    s_table_base = ParagraphStyle(
        name="s_table_base",
        fontName="customfont",
        fontSize=6,
        leading=6,
    )
    s_table_medium = ParagraphStyle(name="s_table_medium", parent=s_table_base, fontSize=9, leading=8)
    s_table_medium_leading = ParagraphStyle(name="s_table_medium_leading", parent=s_table_medium, leading=13.9)
    s_table_large = ParagraphStyle(name="s_table_large", parent=s_table_medium, fontSize=11, leading=11)
    s_table_large_center = ParagraphStyle(name="s_table_large", parent=s_table_large, alignment=TA_CENTER)
    s_table_large_center_padding = ParagraphStyle(
        name="s_table_large", parent=s_table_large_center, spaceBefore=20, spaceAfter=20
    )
    s_table_center = ParagraphStyle(
        name="s_table_center",
        parent=s_table_base,
        alignment=TA_CENTER,
    )
    s_table_center_high = ParagraphStyle(name="s_table_center", parent=s_table_center, leading=9, fontSize=8)
    s_table_right = ParagraphStyle(name="s_table_right", parent=s_table_base, alignment=TA_RIGHT)
    s_table_center = ParagraphStyle(name="s_table_center", parent=s_table_base, alignment=TA_CENTER)
    s_table_headline = ParagraphStyle(
        name="s_table_headline",
        parent=s_table_base,
        fontSize=16,
        leading=16,
    )
    s_table_headline_2 = ParagraphStyle(
        name="s_table_headline_2",
        parent=s_table_base,
        fontSize=10,
        leading=10,
    )

    # Setup Colors
    c_product = HexColor(general_data["colors"][0])
    c_product_alpha = HexColor(f"{general_data['colors'][0]}20", hasAlpha=True)

    c_table_border = HexColor(0x9EA3AC)
    c_grid_color = HexColor(0xB6BAC1)
    c_box_color = HexColor(0x3C4859)
    c_table_background = colors.HexColor(0xE2E3E6)

    # Frame and Page Layout
    frame_defaults = {"showBoundary": debug, "leftPadding": 0, "rightPadding": 0, "topPadding": 0, "bottomPadding": 0}

    text_frame = Frame(
        x1=SIDE_MARGIN,
        y1=CONTENT_Y,
        width=CONTENT_WIDTH_PAGE1_LEFT,
        height=CONTENT_HEIGHT,
        id="text_frame",
        **frame_defaults,
    )

    main_features_frame = Frame(
        x1=CONTENT_X_PAGE1_RIGHT,
        y1=CONTENT_Y,
        width=CONTENT_WIDTH_PAGE1_RIGHT,
        height=CONTENT_HEIGHT,
        id="main_features_frame",
        **frame_defaults,
    )

    second_page = Frame(
        x1=SIDE_MARGIN,
        y1=CONTENT_Y,
        width=CONTENT_WIDTH_PAGE2,
        height=CONTENT_HEIGHT,
        id="second_page",
        **frame_defaults,
    )

    def on_page(canv, dock):
        canv.saveState()

        # Header
        canv.setFillColor(c_box_color)
        canv.rect(0, A4[1] - HEADER_HEIGHT, A4[0], HEADER_HEIGHT, fill=True, stroke=False)

        colors = [
            HexColor(0xFFB166),
            HexColor(0x8CD66B),
            HexColor(0x05D6A1),
            HexColor(0x01ABAA),
            HexColor(0x70D6FF),
            HexColor(0x0585FF),
            HexColor(0x5724D9),
            HexColor(0xA359E5),
            HexColor(0xEF476F),
        ]
        height = 0.13 * cm
        width = A4[0] / len(colors)
        for index, color in enumerate(colors):
            canv.setFillColor(color)
            canv.rect(0 + index * width, A4[1] - HEADER_HEIGHT - height, width, height, fill=True, stroke=False)

        # Footer
        canv.setFillColor(c_box_color)
        canv.rect(0, 0, A4[0], FOOTER_HEIGHT, fill=True, stroke=False)

        for index, color in enumerate(colors):
            canv.setFillColor(color)
            canv.rect(0 + index * width, FOOTER_HEIGHT, width, height, fill=True, stroke=False)

        drawing = svg2rlg(ReportAsset.objects.get(key="logo").asset)
        width, height = drawing.width, drawing.height
        height = 1.295 * cm

        scaling_factor = 1.295 * cm / drawing.height
        drawing.scale(scaling_factor, scaling_factor)
        renderPDF.draw(
            drawing, canv, ((A4[0] - width * scaling_factor) / 2), A4[1] - height - (HEADER_HEIGHT - height) / 2
        )

        reportlab_image = Image(ReportAsset.objects.get(key="footer-text").asset)
        width, height = reportlab_image.imageWidth, reportlab_image.imageHeight
        ratio = float(width) / float(height)
        height = 0.436 * cm
        width = height * ratio

        reportlab_image.drawWidth = width
        reportlab_image.drawHeight = height
        reportlab_image.drawOn(canv, (A4[0] - width) / 2, (FOOTER_HEIGHT - height) / 2)

        canv.restoreState()

    doc.addPageTemplates(
        [
            PageTemplate(id="page", onPage=on_page, frames=[text_frame, main_features_frame]),
            PageTemplate(id="second_page", onPage=on_page, frames=[second_page]),
        ]
    )

    def generate_title(title):
        table_data = [[Paragraph("", style=s_table_headline), Paragraph(title, style=s_table_headline)]]
        title_table = Table(table_data, colWidths=[0.14 * cm, None], rowHeights=[0.41 * cm])
        title_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), c_product),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (1, 0), (-1, -1), 0.2 * cm),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return title_table

    def impress(l):
        style = s_table_headline_2
        table_data = [
            [
                Paragraph("", style=style),
                Paragraph("Important information", style=style),
            ],
            [
                Paragraph("", style=style),
                Paragraph(ReportAsset.objects.get(key="disclaimer").text, style=s_base_small_justified),
            ],
        ]

        t = Table(table_data, colWidths=[0.14 * cm, None], rowHeights=[0.41 * cm, None])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), colors.white),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (1, 0), (-1, -1), 0.2 * cm),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 1), (-1, -1), 0.334 * cm),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    # ("BOTTOMPADDING", (0, -1), (-1, -1), 0.7*cm),
                ]
            )
        )
        l.append(KeepTogether(TopPadder(t)))

    # Description
    elements.append(generate_title(general_data["title"]))
    elements.append(Paragraph(general_data["introduction"], style=s_base_indent))
    elements.append(Spacer(height=LINEHEIGHT * 2, width=0))

    # Monthly Returns
    elements.append(generate_title("Monthly Returns (%)"))
    elements.append(Spacer(height=LINEHEIGHT * 1, width=0))
    elements.append(
        get_simple_aggregated_table(
            df=monthly_returns,
            width=CONTENT_WIDTH_PAGE1_LEFT,
            row_height=0.389 * cm,
            header_style=s_table_center,
            row_style=s_table_center,
            data_style=s_table_right,
            grid_color=c_table_border,
            offset=CONTENT_OFFSET,
            debug=debug,
        )
    )
    elements.append(Spacer(height=LINEHEIGHT * 1, width=0))
    elements.append(
        Paragraph(
            "<i>*Performance data from February 2016 to July 7th 2020 reflect the historical performances of AtonRâ's thematic certificates. Themes at inception: Mobile Payments, Biotechnology, Artificial Intelligence & Robotics, Security & Space. Subsequent additions: Bionics (January 2017), Fintech (May 2017), Sustainable Future (October 2018).</i>",
            style=s_base_small_justified,
        )
    )
    elements.append(Spacer(height=LINEHEIGHT * 2, width=0))

    # Price Timeseries Chart
    elements.append(
        get_timeseries_chart(
            data=[list(zip(prices.index, prices.net_value))],
            width=CONTENT_WIDTH_PAGE1_LEFT - CONTENT_OFFSET,
            height=4.34 * cm,
            color=c_product,
            fill_color=c_product_alpha,
            grid_color=c_grid_color,
            scale=Scale.LOGARITHMIC.value,
            debug=debug,
            x=CONTENT_OFFSET,
        )
    )
    elements.append(Spacer(height=LINEHEIGHT * 2, width=0))

    # Top 3
    elements.append(
        get_simple_data_table(
            headers=[
                "<strong>Top 10 Holdings</strong>",
                "<strong>Top 3 Contributors</strong>",
                "<strong>Bottom 3 Contributors</strong>",
            ],
            data=list(itertools.zip_longest(top_10_holdings, top_3_contributors, bottom_3_contributors, fillvalue="")),
            width=CONTENT_WIDTH_PAGE1_LEFT,
            header_row_height=0.85 * cm,
            data_row_height=0.45 * cm,
            margin=0.16 * cm,
            header_style=s_table_medium,
            data_style=s_table_base,
            grid_color=c_table_border,
            offset=CONTENT_OFFSET,
            debug=debug,
        )
    )

    # More Information Box
    elements.append(
        TopPadder(
            TextBoxWithImage(
                width=CONTENT_WIDTH_PAGE1_LEFT,
                height=1.36 * cm,
                img=ReportAsset.objects.get(key="robot").asset,
                img_x=0.516 * cm,
                img_y=-0.8 * cm,
                img_width=2.89 * cm,
                img_height=2.89 * cm,
                text='<strong>Click here to learn more:</strong> <a href="https://www.atonra.ch/our-research/">www.atonra.ch/our-research/</a>',
                text_style=s_table_center_high,
                box_color=c_table_background,
                offset=CONTENT_OFFSET,
                debug=debug,
            )
        )
    )

    elements.append(platypus.FrameBreak("main_features_frame"))

    # Main Features Table

    MAIN_FEATURES_COLOR_BAR_HEIGHT = 0.23 * cm
    MAIN_FEATURES_GAP_HEIGHT = 0.17 * cm
    MAIN_FEATURES_TITLE_HEIGHT = 1.4 * cm
    MAIN_FEATURES_TITLE1_HEIGHT = 0.74 * cm

    table_data = [
        [Spacer(width=0, height=0)],
        [
            TextWithIcon(
                width=CONTENT_WIDTH_PAGE1_RIGHT,
                height=MAIN_FEATURES_TITLE_HEIGHT,
                text=general_data["date"],
                font="customfont-bd",
                font_size=10,
                icon=context["logo_file"] if "logo_file" in context else None,
            )
        ],
        [Paragraph("<strong>MAIN FEATURES</strong>", style=s_table_center)],
        [Spacer(width=0, height=0)],
    ]

    for label, value in main_features_dict.items():
        if isinstance(value, date):
            value = value.strftime("%d-%b-%y")
        elif isinstance(value, (Decimal, float)):
            value = "%.2f" % value
        elif isinstance(value, int):
            value = str(value)
        elif value is None:
            value = ""

        if label.lower() in ["currency", "last price"]:
            table_data.append(
                [
                    Paragraph(f"<strong>{label.upper()}</strong>", style=s_table_base),
                    Paragraph(f"<strong>{value.upper()}</strong>", style=s_table_base),
                ]
            )
        else:
            table_data.append(
                [
                    Paragraph(label.upper(), style=s_table_base),
                    Paragraph(value.upper(), style=s_table_base),
                ]
            )

    table_data.extend([[Spacer(width=0, height=0)], [Spacer(width=0, height=0)]])

    row_heights = [
        MAIN_FEATURES_COLOR_BAR_HEIGHT,
        MAIN_FEATURES_TITLE_HEIGHT,
        MAIN_FEATURES_TITLE1_HEIGHT,
        MAIN_FEATURES_GAP_HEIGHT,
    ]
    row_heights.extend([None] * (len(table_data) - 6))
    row_heights.extend([MAIN_FEATURES_GAP_HEIGHT, MAIN_FEATURES_COLOR_BAR_HEIGHT])

    t = Table(table_data, rowHeights=row_heights, colWidths=[CONTENT_WIDTH_PAGE1_RIGHT / 2] * 2)
    table_styles = [
        ("BACKGROUND", (0, 0), (1, 0), c_product),  # Top Color Bar
        ("BACKGROUND", (0, -1), (1, -1), c_product),  # Bottom Color Bar
        ("BACKGROUND", (0, 2), (-1, 2), c_table_background),  # Title Background
        ("LINEABOVE", (0, 2), (-1, 2), 0.25, colors.HexColor("#6d7683")),  # Title Line Above
        ("LINEBELOW", (0, 2), (-1, 2), 0.25, colors.HexColor("#6d7683")),  # Title Line Below
        ("LINEBEFORE", (1, 3), (1, -2), 0.25, colors.HexColor("#6d7683")),  # Data Vertical Seperator
        ("SPAN", (0, 1), (-1, 1)),  # Col Span Title
        ("SPAN", (0, 2), (-1, 2)),  # Col Span Title1
        ("LEFTPADDING", (0, 1), (0, -1), 0),  # Leftpadding Data Labels
        ("LEFTPADDING", (1, 1), (1, -1), 0.28 * cm),  # Leftpadding Data Values
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
    ]

    if debug:
        table_styles.extend(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )

    t.setStyle(TableStyle(table_styles))

    elements.append(t)
    elements.append(Spacer(height=LINEHEIGHT * 1, width=0))

    # All time table
    table_data = [
        [
            Paragraph("<strong>ALL TIME HIGH</strong>", style=s_table_center),
            Paragraph("<strong>ALL TIME LOW</strong>", style=s_table_center),
        ],
        [
            Paragraph("", style=s_table_center),
            Paragraph("", style=s_table_center),
        ],
    ]

    table_data.append(
        [
            Paragraph(f'PRICE: {all_time_dict["high"]["price"]:.1f}', style=s_table_center),
            Paragraph(f'PRICE: {all_time_dict["low"]["price"]:.1f}', style=s_table_center),
        ],
    )
    table_data.append(
        [
            Paragraph(f'DATE: {all_time_dict["high"]["date"]:%d-%b-%y}', style=s_table_center),
            Paragraph(f'DATE: {all_time_dict["low"]["date"]:%d-%b-%y}', style=s_table_center),
        ],
    )
    table_data.append(
        [
            Paragraph("", style=s_table_center),
            Paragraph("", style=s_table_center),
        ]
    )

    row_heights = [0.74 * cm, 0.17 * cm, None, None, 0.17 * cm]

    t = Table(table_data, rowHeights=row_heights)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (1, 0), c_table_background),
                ("LINEABOVE", (0, 0), (1, 0), 0.25, colors.HexColor("#6d7683")),
                ("LINEBELOW", (0, 0), (1, 0), 0.25, colors.HexColor("#6d7683")),
                ("LINEBELOW", (0, -1), (1, -1), 0.25, colors.HexColor("#6d7683")),
                ("LINEBEFORE", (1, 0), (1, -1), 0.25, colors.HexColor("#6d7683")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    elements.append(t)

    elements.append(
        TopPadder(
            TextBox(
                width=CONTENT_WIDTH_PAGE1_RIGHT,
                height=4.20 * cm,
                text='<strong>Investment Team:</strong><br />a seasoned team of<br />portfolio managers /<br />analysts and engineers<br />supported by the full<br />resources of AtonRâ<br />Partners.<br /><br /><strong><a href="https://atonra.ch/who-we-are/our-team/">Click here to discover<br />the entire team</a></strong>',
                text_style=s_table_center_high,
                box_color=c_table_background,
                debug=debug,
            )
        )
    )

    # Second Page

    def get_bar_chart_height(df, bar_width=0.12 * cm, bar_padding=0.3 * cm, max_label_width=3.35 * cm):
        number_of_items = len(df)
        return number_of_items * (bar_width + 2 * bar_padding)

    def get_bar_chart(df, width, height, bar_width=0.12 * cm, bar_padding=0.3 * cm, max_label_width=3.35 * cm):
        font_size = 6
        drawing = Drawing(width, height)
        bar_chart = HorizontalBarChart()

        data = list()
        categories = list()
        for index, row in enumerate(df.itertuples()):
            data.append(row.weighting * 100)
            categories.append(f"{row.aggregated_title} ({row.weighting*100:.1f}%)")

        max_label = 0
        _categories = list()
        for category in categories:
            _w = stringWidth(category, "customfont", font_size)
            if _w > max_label_width:
                split_list = category.split(" ")
                splitter = int(len(split_list) * 2 / 3)

                part_1 = " ".join(split_list[:splitter])
                part_2 = " ".join(split_list[splitter:])
                category = part_1 + "\n" + part_2
                _w1 = stringWidth(part_1, "customfont", font_size)
                _w2 = stringWidth(part_2, "customfont", font_size)
                _w = max(_w1, _w2)
            _categories.append(category)
            max_label = max(max_label, _w - bar_chart.categoryAxis.labels.dx)

        bar_chart.width = width - max_label

        bar_chart.height = height
        bar_chart.x = width - bar_chart.width
        bar_chart.y = 0

        bar_chart.data = [list(reversed(data))]
        bar_chart.categoryAxis.categoryNames = list(reversed(_categories))
        bar_chart.categoryAxis.labels.boxAnchor = "e"
        bar_chart.categoryAxis.labels.textAnchor = "end"
        bar_chart.categoryAxis.labels.fontName = "customfont"
        bar_chart.categoryAxis.labels.fontSize = font_size
        bar_chart.categoryAxis.labels.leading = font_size

        bar_chart.barWidth = bar_width
        bar_chart.bars.strokeColor = colors.transparent
        bar_chart.bars[0].fillColor = c_product

        # x-Axis
        bar_chart.valueAxis.labelTextFormat = DecimalFormatter(0, suffix="%")
        bar_chart.valueAxis.labels.fontName = "customfont"
        bar_chart.valueAxis.labels.fontSize = 6

        bar_chart.valueAxis.strokeWidth = -1
        bar_chart.valueAxis.gridStrokeColor = c_grid_color
        bar_chart.valueAxis.gridStrokeDashArray = (0.2, 0, 0.2)

        bar_chart.valueAxis.visibleGrid = True
        bar_chart.valueAxis.forceZero = True

        bar_chart.categoryAxis.strokeWidth = 0.5
        bar_chart.categoryAxis.strokeColor = HexColor(0x6D7683)
        bar_chart.categoryAxis.tickLeft = 0
        bar_chart.categoryAxis.labels.fontName = "customfont"
        bar_chart.categoryAxis.labels.fontSize = 6
        drawing.add(bar_chart)
        drawing.add(String(0, -25, "", fontName="customfont", fontSize=6, fillColor=colors.black))
        return drawing

    NUM_CHARTS_FIRST_ROW = 2
    WIDTH_CHARTS_FIRST_ROW = (
        (CONTENT_WIDTH_PAGE2 - CONTENT_OFFSET) - ((NUM_CHARTS_FIRST_ROW - 1) * TABLE_MARGIN_PAGE2)
    ) / NUM_CHARTS_FIRST_ROW

    max_height = max(
        [
            get_pie_chart_horizontal_height(geographical, legend_max_cols=10),
            get_pie_chart_horizontal_height(currencies, legend_max_cols=10),
        ]
    )
    geographical_pie_chart = get_pie_chart_horizontal(
        geographical,
        WIDTH_CHARTS_FIRST_ROW,
        max_height,
        general_data["colors"],
        4.23 * cm,
        legend_max_cols=10,
        legend_x=3.8 * cm,
    )
    currencies_pie_chart = get_pie_chart_horizontal(
        currencies,
        WIDTH_CHARTS_FIRST_ROW,
        max_height,
        general_data["colors"],
        4.23 * cm,
        legend_max_cols=10,
        legend_x=3.8 * cm,
    )

    max_height2 = max(
        [
            get_pie_chart_horizontal_height(liquidity, legend_max_cols=10),
            get_pie_chart_horizontal_height(allocation, legend_max_cols=10),
        ]
    )
    liquidity_pie_chart = get_pie_chart_horizontal(
        liquidity,
        WIDTH_CHARTS_FIRST_ROW,
        max_height2,
        general_data["colors"],
        4.23 * cm,
        legend_max_cols=10,
        legend_x=3.8 * cm,
    )
    allocation_pie_chart = get_pie_chart_horizontal(
        allocation,
        WIDTH_CHARTS_FIRST_ROW,
        max_height2,
        general_data["colors"],
        4.23 * cm,
        legend_max_cols=10,
        legend_x=3.8 * cm,
    )

    risk = RiskScale(
        general_data["risk_scale"],
        para_style=s_base_small_justified,
        text=f"This risk ({calculated_risk_scale:.1f}) was calculated manually by weighing the risk of all implemented strategies.",
    )

    max_height3 = max([get_pie_chart_horizontal_height(marketcap, legend_max_cols=10), risk.height])
    marketcap_pie_chart = get_pie_chart_horizontal(
        marketcap,
        WIDTH_CHARTS_FIRST_ROW,
        max_height3,
        general_data["colors"],
        4.23 * cm,
        legend_max_cols=10,
        legend_x=3.8 * cm,
    )

    third_td = [
        [
            Spacer(width=0, height=0),
            Paragraph("<strong>Geographical<br />Breakdown</strong>", style=s_table_medium_leading),
            Spacer(width=0, height=0),
            Paragraph("<strong>Currency<br />Exposure</strong>", style=s_table_medium_leading),
        ],
        [
            Spacer(width=0, height=0),
            geographical_pie_chart,
            Spacer(width=0, height=0),
            currencies_pie_chart,
        ],
        [
            Spacer(width=0, height=0),
            Paragraph("<strong>Liquidity</strong>", style=s_table_medium_leading),
            Spacer(width=0, height=0),
            Paragraph("<strong>Asset<br />Allocation</strong>", style=s_table_medium_leading),
        ],
        [
            Spacer(width=0, height=0),
            liquidity_pie_chart,
            Spacer(width=0, height=0),
            allocation_pie_chart,
        ],
        [
            Spacer(width=0, height=0),
            Paragraph(
                f"<strong>Market Cap.<br />Distributions ({context['currency']})</strong>",
                style=s_table_medium_leading,
            ),
            Spacer(width=0, height=0),
            Paragraph("<strong>Risk Scale</strong>", style=s_table_medium_leading),
        ],
        [Spacer(width=0, height=0), marketcap_pie_chart, Spacer(width=0, height=0), risk],
    ]

    cols = [CONTENT_OFFSET]
    cols.extend([WIDTH_CHARTS_FIRST_ROW, TABLE_MARGIN_PAGE2] * NUM_CHARTS_FIRST_ROW)
    cols.pop(-1)

    third_t = Table(
        third_td,
        colWidths=cols,
        rowHeights=[
            1.4 * cm,
            max_height,
            1.4 * cm,
            max_height2,
            1.4 * cm,
            max_height3,
        ],
    )
    third_table_styles = [
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("VALIGN", (0, 2), (-1, 2), "MIDDLE"),
        ("VALIGN", (0, 4), (-1, 4), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]

    third_table_styles.extend(
        [
            ("LINEABOVE", (1, 0), (1, 0), 0.25, c_box_color),
            ("LINEBELOW", (1, 0), (1, 0), 0.25, c_box_color),
            ("LINEABOVE", (3, 0), (3, 0), 0.25, c_box_color),
            ("LINEBELOW", (3, 0), (3, 0), 0.25, c_box_color),
            ("LINEABOVE", (1, 2), (1, 2), 0.25, c_box_color),
            ("LINEBELOW", (1, 2), (1, 2), 0.25, c_box_color),
            ("LINEABOVE", (3, 2), (3, 2), 0.25, c_box_color),
            ("LINEBELOW", (3, 2), (3, 2), 0.25, c_box_color),
            ("LINEABOVE", (1, 4), (1, 4), 0.25, c_box_color),
            ("LINEBELOW", (1, 4), (1, 4), 0.25, c_box_color),
            ("LINEABOVE", (3, 4), (3, 4), 0.25, c_box_color),
            ("LINEBELOW", (3, 4), (3, 4), 0.25, c_box_color),
        ]
    )

    if debug:
        third_table_styles.extend(
            [
                ("BOX", (0, 0), (-1, -1), 0.25, c_box_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, c_box_color),
            ]
        )

    third_t.setStyle(TableStyle(third_table_styles))

    elements.append(platypus.PageBreak("second_page"))
    elements.append(generate_title(general_data["title"]))
    elements.append(Spacer(height=LINEHEIGHT, width=0))
    elements.append(third_t)

    cols = [CONTENT_OFFSET]
    cols.extend([WIDTH_CHARTS_FIRST_ROW, TABLE_MARGIN_PAGE2])
    cols.pop(-1)

    industry_height = get_bar_chart_height(industry)
    industry_chart = get_bar_chart(industry, 17 * cm, industry_height - 30)

    second_charts = [
        [
            Spacer(width=0, height=0),
            Paragraph("<strong>Industry Exposure</strong>", style=s_table_medium_leading),
        ],
        [Spacer(width=0, height=0), industry_chart],
    ]

    col_width = CONTENT_WIDTH_PAGE2 - CONTENT_OFFSET - TABLE_MARGIN_PAGE2

    other_table = Table(
        second_charts,
        colWidths=[CONTENT_OFFSET, col_width],
        rowHeights=[
            0.85 * cm,
            industry_height * 0.9,
        ],
    )

    other_table_styles = [
        ("VALIGN", (1, 1), (1, 1), "TOP"),
        ("LINEABOVE", (1, 0), (1, 0), 0.25, c_box_color),
        ("LINEBELOW", (1, 0), (1, 0), 0.25, c_box_color),
    ]
    if debug:
        other_table_styles.extend(
            [
                ("BOX", (0, 0), (-1, -1), 0.25, c_box_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, c_box_color),
            ]
        )

    other_table.setStyle(TableStyle(other_table_styles))
    elements.append(platypus.PageBreak("second_page"))
    elements.append(generate_title(general_data["title"]))
    elements.append(Spacer(height=LINEHEIGHT, width=0))
    elements.append(other_table)

    elements.append(platypus.PageBreak("second_page"))
    elements.append(generate_title(general_data["title"]))
    elements.append(Spacer(height=LINEHEIGHT * 1, width=0))
    elements.append(
        get_fund_table(
            df=fund_table,
            width=20.0 * cm,
            row_height=0.45 * cm,
            header_style=s_table_center,
            row_style=s_table_center,
            data_style=s_table_right,
            grid_color=c_table_border,
            background_color=c_table_background,
            offset=CONTENT_OFFSET,
            debug=debug,
        )
    )
    elements.append(Spacer(height=LINEHEIGHT * 1, width=0))

    impress(elements)

    doc.build(elements)
    output.seek(0)

    return output
