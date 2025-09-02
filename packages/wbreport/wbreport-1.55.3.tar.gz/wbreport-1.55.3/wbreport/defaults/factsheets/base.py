from datetime import date
from decimal import Decimal
from io import BytesIO

import pandas as pd
from django.template.loader import get_template
from reportlab import platypus
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
    Flowable,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.frames import Frame
from wbcore.utils.figures import (
    get_factsheet_timeseries_chart,
    get_horizontal_barplot,
    get_piechart,
)
from wbportfolio.models.products import InvestmentIndex

from wbreport.mixins import ReportMixin
from wbreport.models import ReportAsset
from wbreport.pdf.charts.pie import (
    get_pie_chart_horizontal,
    get_pie_chart_horizontal_height,
    get_pie_chart_vertical,
    get_pie_chart_vertical_height,
)
from wbreport.pdf.charts.timeseries import Scale, get_timeseries_chart
from wbreport.pdf.flowables.textboxes import TextWithIcon
from wbreport.pdf.tables.aggregated_tables import get_simple_aggregated_table
from wbreport.pdf.tables.data_tables import get_simple_data_table

from .mixins import FactsheetReportMixin


class ReportClass(FactsheetReportMixin, ReportMixin):
    HTML_TEMPLATE_FILE = "report/factsheet_base.html"

    @classmethod
    def get_context(cls, version):
        content_object = version.report.content_object
        parameters = cls.parse_parameters(version.parameters)

        asset_portfolio = content_object.asset_portfolio
        base_portfolio = content_object.primary_portfolio
        context = {"product_title": content_object.title}

        end = content_object.asset_portfolio.get_latest_asset_position_date(parameters["end"])
        start = content_object.asset_portfolio.get_latest_asset_position_date(parameters["start"])
        prices = content_object.get_prices_df(from_date=end)
        if start and end and not prices.empty:
            context["date"] = end

            if content_object.group:
                context["funds_table"] = content_object.group.get_fund_product_table(end)

            context["currency"] = content_object.currency.symbol
            context["external_webpage"] = content_object.external_webpage
            context["monthly_returns"] = content_object.get_monthly_return_summary_dict(end=end)

            context["introduction"] = content_object.description
            context["all_time"] = content_object.get_price_range(val_date=end)
            context["risk_scale"] = content_object.risk_scale
            context["risk_scale_loop"] = [True] * content_object.risk_scale + [False] * (7 - content_object.risk_scale)
            context["holdings"] = asset_portfolio.get_holding(end).values(
                "underlying_instrument__name_repr", "weighting"
            )
            contributors = (
                asset_portfolio.get_portfolio_contribution_df(start, end, with_cash=False)
                .sort_values(by="contribution_total", ascending=False)
                .underlying_instrument__name_repr
            )

            if contributors is not None and not contributors.empty:
                contributors_list = contributors.values.tolist()
                context["top_contributors"] = contributors_list[:3]
                contributors_list.reverse()
                context["worst_contributors"] = contributors_list[:3]

            context["prices"] = prices
            context["geographical_breakdown"] = asset_portfolio.get_geographical_breakdown(end)
            context["currency_exposure"] = asset_portfolio.get_currency_exposure(end)
            context["asset_allocation"] = asset_portfolio.get_asset_allocation(end)
            context["market_cap_distribution"] = asset_portfolio.get_equity_market_cap_distribution(end)
            context["equity_liquidity"] = asset_portfolio.get_equity_liquidity(end)
            context["industry_exposure"] = asset_portfolio.get_industry_exposure(end).sort_values(
                by=["weighting"], ascending=False
            )
            if content_object.investment_index == InvestmentIndex.LONG_SHORT.name:
                context["longshort"] = base_portfolio.get_longshort_distribution(end)
        else:
            raise ValueError("Context cannot be generated")
        return context

    @classmethod
    def generate_html(cls, context):
        if "funds_table" in context:
            context["funds_table"] = context["funds_table"].to_html(
                border=0,
                index=False,
                classes=["table", "table-funds", "table-colored"],
                index_names=False,
                float_format="%.1f%%",
                na_rep="",
            )

        context["prices"] = get_factsheet_timeseries_chart(
            context["prices"], color=context["report_base_color"]
        ).to_html(full_html=False, include_plotlyjs=False)

        nb_labels_first_row = max(
            [
                context["geographical_breakdown"].shape[0],
                context["currency_exposure"].shape[0],
                context["asset_allocation"].shape[0],
            ]
        )
        height_piechart = 300
        context["geographical_breakdown"] = get_piechart(
            context["geographical_breakdown"],
            colors_map=context["colors_palette"],
            height=height_piechart,
            max_number_label=nb_labels_first_row,
        ).to_html(full_html=False, include_plotlyjs=False)
        context["currency_exposure"] = get_piechart(
            context["currency_exposure"],
            colors_map=context["colors_palette"],
            height=height_piechart,
            max_number_label=nb_labels_first_row,
        ).to_html(full_html=False, include_plotlyjs=False)
        context["asset_allocation"] = get_piechart(
            context["asset_allocation"],
            colors_map=context["colors_palette"],
            height=height_piechart,
            max_number_label=nb_labels_first_row,
        ).to_html(full_html=False, include_plotlyjs=False)

        # SECOND WWIDGET ROW
        context["market_cap_distribution"] = get_piechart(
            context["market_cap_distribution"], height=height_piechart, colors_map=context["colors_palette"]
        ).to_html(full_html=False, include_plotlyjs=False)
        context["equity_liquidity"] = get_piechart(
            context["equity_liquidity"], height=height_piechart, colors_map=context["colors_palette"]
        ).to_html(full_html=False, include_plotlyjs=False)

        context["industry_exposure"] = get_horizontal_barplot(
            context["industry_exposure"], colors=context["colors_palette"][0]
        ).to_html(full_html=False, include_plotlyjs=False)
        if "strategy_allocation" in context:
            index_allocation_df = context["strategy_allocation"]
            if not index_allocation_df.empty:
                context["strategy_allocation"] = get_piechart(
                    index_allocation_df,
                    x_label="allocation_end",
                    height=height_piechart,
                    y_label="underlying_instrument__name_repr",
                    hoverinfo="text",
                    colors_label="color",
                ).to_html(full_html=False, include_plotlyjs=False)
                renamed_df = index_allocation_df.rename(
                    columns={"performance_total": "Monthly Performance", "contribution_total": "Monthly Contribution"}
                )
                context["stragegy_contribution"] = get_horizontal_barplot(
                    renamed_df,
                    colors_label="color",
                    x_label=["Monthly Performance", "Monthly Contribution"],
                    y_label="underlying_instrument__name_repr",
                ).to_html(full_html=False, include_plotlyjs=False)

        if not context.get("longshort", pd.DataFrame()).empty:
            context["longshort"] = get_piechart(
                context["longshort"],
                colors_map=context["colors_palette"],
                hoverinfo="label+text",
                default_normalize=False,
                height=height_piechart,
                y_label="title",
            ).to_html(full_html=False, include_plotlyjs=False)

        template = get_template(cls.HTML_TEMPLATE_FILE)
        return template.render(context)

    @classmethod
    def generate_file(cls, context):
        debug = False
        # Product Data
        # Main Feature table as dictionary
        main_features_dict = context["information_table"].get(
            "Main Features", context["information_table"].get("Share Class Information", {})
        )
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
        top_3_holdings = list(context["holdings"].values_list("underlying_instrument__name_repr", flat=True))[0:3]
        top_3_holdings = [t.upper() for t in top_3_holdings]

        top_3_contributors = [c.upper() for c in context["top_contributors"]]
        bottom_3_contributors = [c.upper() for c in context["worst_contributors"]]

        # {'high': {'price':low, 'date':date}, 'low' : {'price':high, 'date':date}}
        all_time_dict = context["all_time"]
        end = context["date"]
        general_data = {}
        general_data["date"] = end.strftime("%b %Y")
        general_data["colors"] = context["colors_palette"]
        general_data["title"] = context["product_title"].replace("&", "&amp;")
        general_data["risk_scale"] = context["risk_scale"]

        general_data["introduction"] = context["introduction"]

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

        output = BytesIO()
        doc = BaseDocTemplate(
            output,
            pagesize=A4,
            rightMargin=0,
            leftMargin=0,
            topMargin=0,
            bottomMargin=0,
            title=general_data["title"],
        )
        elements = []

        s_base = ParagraphStyle(name="s_base", fontName="customfont", fontSize=9, leading=10)
        s_base_small_justified = ParagraphStyle(
            name="s_base_small_justified", parent=s_base, fontSize=6.5, leading=7, alignment=TA_JUSTIFY
        )
        # s_base_small_justified_indent = ParagraphStyle(
        #     name="s_base_small_justified_indent", parent=s_base_small_justified, leftIndent=CONTENT_OFFSET
        # )
        s_base_indent = ParagraphStyle(name="s_description", parent=s_base, spaceBefore=8, leftIndent=CONTENT_OFFSET)
        s_table_base = ParagraphStyle(
            name="s_table_base",
            fontName="customfont",
            fontSize=6,
            leading=6,
        )
        s_table_medium = ParagraphStyle(name="s_table_medium", parent=s_table_base, fontSize=9, leading=8)
        s_table_medium_leading = ParagraphStyle(name="s_table_medium_leading", parent=s_table_medium, leading=13.9)
        # s_table_large = ParagraphStyle(name="s_table_large", parent=s_table_medium, fontSize=11, leading=11)
        # s_table_large_center = ParagraphStyle(name="s_table_large", parent=s_table_large, alignment=TA_CENTER)
        # s_table_large_center_padding = ParagraphStyle(
        #     name="s_table_large", parent=s_table_large_center, spaceBefore=20, spaceAfter=20
        # )
        # s_table_center = ParagraphStyle(
        #     name="s_table_center",
        #     parent=s_table_base,
        #     alignment=TA_CENTER,
        # )
        # s_table_center_high = ParagraphStyle(name="s_table_center", parent=s_table_center, leading=9, fontSize=8)
        s_table_right = ParagraphStyle(name="s_table_right", parent=s_table_base, alignment=TA_RIGHT)
        s_table_center = ParagraphStyle(name="s_table_center", parent=s_table_base, alignment=TA_CENTER)
        s_table_headline = ParagraphStyle(
            name="s_table_headline",
            parent=s_table_base,
            fontSize=16,
            leading=16,
        )
        # s_table_headline_2 = ParagraphStyle(
        #     name="s_table_headline_2",
        #     parent=s_table_base,
        #     fontSize=10,
        #     leading=10,
        # )

        # Setup Colors
        c_product = HexColor(general_data["colors"][0])
        c_product_alpha = HexColor(f"{general_data['colors'][0]}20", hasAlpha=True)

        c_table_border = HexColor(0x9EA3AC)
        c_grid_color = HexColor(0xB6BAC1)
        c_box_color = HexColor(0x3C4859)
        c_table_background = colors.HexColor(0xE2E3E6)

        # Frame and Page Layout
        frame_defaults = {
            "showBoundary": debug,
            "leftPadding": 0,
            "rightPadding": 0,
            "topPadding": 0,
            "bottomPadding": 0,
        }

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

            canv.restoreState()

        doc.addPageTemplates(
            [
                PageTemplate(id="page", onPage=on_page, frames=[text_frame, main_features_frame]),
                PageTemplate(id="second_page", onPage=on_page, frames=[second_page]),
            ]
        )

        elements.append(NextPageTemplate(["second_page"]))

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
                    "<strong>Top 3 Holdings</strong>",
                    "<strong>Top 3 Contributors</strong>",
                    "<strong>Bottom 3 Contributors</strong>",
                ],
                data=list(zip(top_3_holdings, top_3_contributors, bottom_3_contributors)),
                width=CONTENT_WIDTH_PAGE1_LEFT,
                header_row_height=0.85 * cm,
                data_row_height=0.39 * cm,
                margin=0.16 * cm,
                header_style=s_table_medium,
                data_style=s_table_base,
                grid_color=c_table_border,
                offset=CONTENT_OFFSET,
                debug=debug,
            )
        )

        elements.append(platypus.FrameBreak("main_features_frame"))

        # Main Features Table

        MAIN_FEATURES_COLOR_BAR_HEIGHT = 0.23 * cm
        MAIN_FEATURES_GAP_HEIGHT = 0.17 * cm
        MAIN_FEATURES_TITLE_HEIGHT = 1.94 * cm
        MAIN_FEATURES_TITLE1_HEIGHT = 0.74 * cm

        table_data = [
            [Spacer(width=0, height=0)],
            [
                TextWithIcon(
                    width=CONTENT_WIDTH_PAGE1_RIGHT,
                    height=MAIN_FEATURES_TITLE_HEIGHT,
                    text=general_data["date"],
                    font="customfont-bd",
                    font_size=11,
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

        # Second Page
        elements.append(platypus.PageBreak("second_page"))
        elements.append(generate_title(general_data["title"]))
        elements.append(Spacer(height=LINEHEIGHT * 1, width=0))

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
                categories.append(f"{row.aggregated_title} ({row.weighting * 100:.1f}%)")

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

        class RiskScaleFlowable(Flowable):
            def __init__(self, height, risk, text=None):
                super().__init__()
                self.risk = risk
                self.height = height
                self.risk_text = (
                    text
                    or "The actual risk can vary significantly if you cash in at an early stage and you may get back less. You may not be able to sell your product easily or you may have to sell at a price that significantly impacts on how much you get back."
                )

            def draw(self):
                width = 0.4 * cm
                gap = 1.177 * cm
                # y = (2.15 + 1) * cm
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

                    self.canv.setFillColor(colors.white)
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
                    x_offset - arrow_offset, y - 0.868 * cm, 6 * gap + x_offset + arrow_offset, y - 0.868 * cm
                )

                self.canv.setFont("customfont", 6)
                self.canv.setFillColor(colors.black)
                self.canv.drawString(x_offset - arrow_offset - 0.165 * cm, y - 1.2 * cm, "LOWER RISK")

                text_width = stringWidth("HIGHER RISK", "customfont", 6)
                self.canv.drawString(
                    6 * gap + x_offset + arrow_offset + 0.165 * cm - text_width, y - 1.2 * cm, "HIGHER RISK"
                )

                para = Paragraph(self.risk_text, style=s_base_small_justified)
                para.wrapOn(self.canv, 250, 8.954 * cm)
                para.drawOn(self.canv, 0, y - 2.5 * cm)

        TABLE_MARGIN = 0.56 * cm
        NUM_CHARTS_FIRST_ROW = 4
        WIDTH_CHARTS_FIRST_ROW = (
            (CONTENT_WIDTH_PAGE2 - CONTENT_OFFSET) - ((NUM_CHARTS_FIRST_ROW - 1) * TABLE_MARGIN)
        ) / NUM_CHARTS_FIRST_ROW

        max_height = max(
            [
                get_pie_chart_vertical_height(geographical, legend_max_cols=10),
                get_pie_chart_vertical_height(currencies),
                get_pie_chart_vertical_height(allocation),
                get_pie_chart_vertical_height(marketcap),
            ]
        )
        geographical_pie_chart = get_pie_chart_vertical(
            geographical, WIDTH_CHARTS_FIRST_ROW, max_height, general_data["colors"], legend_max_cols=10
        )
        currencies_pie_chart = get_pie_chart_vertical(
            currencies, WIDTH_CHARTS_FIRST_ROW, max_height, general_data["colors"]
        )
        allocation_pie_chart = get_pie_chart_vertical(
            allocation, WIDTH_CHARTS_FIRST_ROW, max_height, general_data["colors"]
        )
        marketcap_pie_chart = get_pie_chart_vertical(
            marketcap, WIDTH_CHARTS_FIRST_ROW, max_height, general_data["colors"]
        )

        top_3_td = [
            [
                Spacer(width=0, height=0),
                Paragraph("<strong>Geographical<br />Breakdown</strong>", style=s_table_medium_leading),
                Spacer(width=0, height=0),
                Paragraph("<strong>Currency<br />Exposure</strong>", style=s_table_medium_leading),
                Spacer(width=0, height=0),
                Paragraph("<strong>Asset<br />Allocation</strong>", style=s_table_medium_leading),
                Spacer(width=0, height=0),
                Paragraph(
                    f"<strong>Market Cap<br />Distributions ({context['currency']})</strong>",
                    style=s_table_medium_leading,
                ),
            ],
            [
                Spacer(width=0, height=0),
                geographical_pie_chart,
                Spacer(width=0, height=0),
                currencies_pie_chart,
                Spacer(width=0, height=0),
                allocation_pie_chart,
                Spacer(width=0, height=0),
                marketcap_pie_chart,
            ],
        ]

        cols = [CONTENT_OFFSET]
        cols.extend([WIDTH_CHARTS_FIRST_ROW, TABLE_MARGIN] * NUM_CHARTS_FIRST_ROW)
        cols.pop(-1)

        top_3_t = Table(
            top_3_td,
            colWidths=cols,
            rowHeights=[
                1.4 * cm,
                max_height,
            ],
        )
        top_3_table_styles = [
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]

        for col in range(1, NUM_CHARTS_FIRST_ROW * 2, 2):
            top_3_table_styles.extend(
                [
                    ("LINEABOVE", (col, 0), (col, 0), 0.25, c_box_color),
                    ("LINEBELOW", (col, 0), (col, 0), 0.25, c_box_color),
                ]
            )

        if debug:
            top_3_table_styles.extend(
                [
                    ("BOX", (0, 0), (-1, -1), 0.25, c_box_color),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, c_box_color),
                ]
            )

        top_3_t.setStyle(TableStyle(top_3_table_styles))
        elements.append(top_3_t)

        # top_3_t.setStyle(
        #     TableStyle(
        #         [
        # ("BOX", (0, 0), (-1, -1), 0.25, c_box_color),
        # ("INNERGRID", (0, 0), (-1, -1), 0.25, c_box_color),
        # ("LINEABOVE", (1, 0), (1, 0), 0.25, c_box_color),
        # ("LINEBELOW", (1, 0), (1, 0), 0.25, c_box_color),
        # ("LINEABOVE", (3, 0), (3, 0), 0.25, c_box_color),
        # ("LINEBELOW", (3, 0), (3, 0), 0.25, c_box_color),
        # ("LINEABOVE", (5, 0), (5, 0), 0.25, c_box_color),
        # ("LINEBELOW", (5, 0), (5, 0), 0.25, c_box_color),
        # ("LINEABOVE", (7, 0), (7, 0), 0.25, c_box_color),
        # ("LINEBELOW", (7, 0), (7, 0), 0.25, c_box_color),
        # ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        # ("LEFTPADDING", (0, 0), (-1, -1), 0),
        # ("SPAN", (1, 2), (3, 2)),
        # ("SPAN", (1, 3), (3, 3)),
        # ("SPAN", (1, 4), (3, 4)),
        # ("SPAN", (5, 2), (7, 2)),
        # ("SPAN", (1, 5), (3, 5)),
        # ("SPAN", (1, 4), (1, 4)),
        # ("LINEABOVE", (1, 2), (3, 2), 0.25, c_box_color),
        # ("LINEBELOW", (1, 2), (3, 2), 0.25, c_box_color),
        # ("LINEABOVE", (5, 2), (7, 2), 0.25, c_box_color),
        # ("LINEBELOW", (5, 2), (7, 2), 0.25, c_box_color),
        # ("LINEABOVE", (1, 4), (3, 4), 0.25, c_box_color),
        # ("LINEBELOW", (1, 4), (3, 4), 0.25, c_box_color),
        # ("VALIGN", (1, 2), (-1, 2), "MIDDLE"),
        # ("VALIGN", (1, 4), (3, 4), "MIDDLE"),
        # ("VALIGN", (1, 4), (3, 4), "MIDDLE"),
        # ("VALIGN", (1, 4), (3, 4), "MIDDLE"),
        # ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        # ("SPAN", (5, 3), (7, 5)),
        # ("VALIGN", (5, 3), (7, 5), "TOP"),
        #         ]
        #     )
        # )

        liquid_height = get_pie_chart_horizontal_height(liquidity, legend_max_cols=50)
        liquidity_pie_chart = get_pie_chart_horizontal(
            liquidity,
            4.23 * cm + 0.56 * cm + 4.23 * cm,
            liquid_height,
            general_data["colors"],
            4.23 * cm,
            legend_max_cols=50,
        )

        risk_height = 3.564 * cm
        industry_height = get_bar_chart_height(industry)

        available_height = CONTENT_HEIGHT - 1.4 * cm - max_height - 0.85 * cm - (0.41 * cm + 12)

        left_height = liquid_height + risk_height + (1 * 0.85 * cm)
        right_height = max(min(available_height, industry_height), left_height)

        # max_available_height = CONTENT_HEIGHT - 1.4 * cm - max_height - 0.85 * cm
        industry_chart = get_bar_chart(industry, 8.94 * cm, right_height - 30)

        last_row_height = right_height - liquid_height - 0.85 * cm

        # last_height = min(
        #     max(industry_height - liquid_height + 6, 3.564 * cm), max_available_height - liquid_height
        # )  # 6 because of the drawn string

        second_charts = [
            [
                Spacer(width=0, height=0),
                Paragraph(
                    "<strong>Equity Liquidity</strong>  (on average 3M daily trading volume)",
                    style=s_table_medium_leading,
                ),
                Spacer(width=0, height=0),
                Paragraph("<strong>Industry Exposure</strong>", style=s_table_medium_leading),
            ],
            [
                Spacer(width=0, height=0),
                liquidity_pie_chart,
                Spacer(width=0, height=0),
                # Spacer(width=0, height=0),
                industry_chart,
            ],
            [
                Spacer(width=0, height=0),
                Paragraph("<strong>Risk Scale</strong>", style=s_table_medium_leading),
                Spacer(width=0, height=0),
                Spacer(width=0, height=0),
            ],
            [
                Spacer(width=0, height=0),
                RiskScaleFlowable(risk_height, general_data["risk_scale"]),
                Spacer(width=0, height=0),
                Spacer(width=0, height=0),
            ],
        ]

        col_width = (CONTENT_WIDTH_PAGE2 - CONTENT_OFFSET - TABLE_MARGIN) / 2

        other_table = Table(
            second_charts,
            colWidths=[CONTENT_OFFSET, col_width, TABLE_MARGIN, col_width],
            rowHeights=[0.85 * cm, liquid_height, 0.85 * cm, last_row_height],
        )

        other_table_styles = [
            ("VALIGN", (1, 2), (1, -1), "TOP"),
            ("SPAN", (3, 1), (3, -1)),
            ("VALIGN", (3, 1), (3, -1), "TOP"),
            ("LINEABOVE", (1, 0), (1, 0), 0.25, c_box_color),
            ("LINEBELOW", (1, 0), (1, 0), 0.25, c_box_color),
            ("LINEABOVE", (3, 0), (3, 0), 0.25, c_box_color),
            ("LINEBELOW", (3, 0), (3, 0), 0.25, c_box_color),
            ("LINEABOVE", (1, 2), (1, 2), 0.25, c_box_color),
            ("LINEBELOW", (1, 2), (1, 2), 0.25, c_box_color),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ]
        if debug:
            other_table_styles.extend(
                [
                    ("BOX", (0, 0), (-1, -1), 0.25, c_box_color),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, c_box_color),
                ]
            )

        other_table.setStyle(TableStyle(other_table_styles))

        elements.append(other_table)

        doc.build(elements)
        output.seek(0)

        return output
