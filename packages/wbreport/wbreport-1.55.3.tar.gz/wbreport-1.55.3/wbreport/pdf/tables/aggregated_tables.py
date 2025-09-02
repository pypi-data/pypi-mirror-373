import numpy as np
from reportlab.lib.colors import grey
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def get_simple_aggregated_table(
    df,
    width,
    row_height,
    header_style,
    row_style,
    data_style,
    grid_color,
    offset=None,
    debug=False,
):
    table_data = list()

    # Generate header column
    table_row = [Spacer(width=0, height=0)] * 2 if offset else 1

    years = list(df.keys())
    months = df[years[0]].keys()
    for column in months:
        table_row.append(Paragraph(str(column).upper(), style=header_style))
    table_data.append(table_row)
    data_style_fake = ParagraphStyle(
        fontName="customfont", fontSize=6, leading=6, name="s_table_center", alignment=TA_CENTER, textColor=grey
    )
    # Generate table
    for year, row in df.items():
        table_row = list()
        if offset:
            table_row.append(Spacer(width=0, height=0))

        table_row.append(Paragraph(str(year), style=row_style))

        for month, element in row.items():
            if element.get("performance", None) is None:
                table_row.append(Spacer(width=0, height=0))
            else:
                value = element["performance"]
                value_str = f"{value:.1%}" if (isinstance(value, float) and not np.isinf(value)) else str(value)
                if element.get("calculated", False):
                    table_row.append(Paragraph(value_str, style=data_style_fake))
                else:
                    table_row.append(Paragraph(value_str, style=row_style))
        # else:
        #     table_row.append(
        #         Paragraph(f"<strong>{row.iloc[-1]:.1f}%</strong>", style=data_style)
        #     )
        table_data.append(table_row)

    num_cols = len(months) + 1

    cols = list()
    if offset:
        cols.append(offset)

    cols.extend([(width - offset or 0) / num_cols] * num_cols)
    rows = [row_height] * (len(years) + 1)

    table = Table(table_data, colWidths=cols, rowHeights=rows)

    table_styles = [
        ("LINEBEFORE", (2, 0), (2, -1), 0.25, grid_color),
        ("LINEBEFORE", (-1, 0), (-1, -1), 0.25, grid_color),
        ("LINEABOVE", (1, 1), (-1, 1), 0.25, grid_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (2, 1), (-1, -1), offset / 2),
    ]

    if debug:
        table_styles.extend(
            [
                ("BOX", (0, 0), (-1, -1), 0.25, grid_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, grid_color),
            ]
        )

    table.setStyle(TableStyle(table_styles))
    return table


def get_fund_table(
    df,
    width,
    row_height,
    header_style,
    row_style,
    data_style,
    grid_color,
    background_color,
    offset=None,
    debug=False,
):
    table_data = [
        [Paragraph("<strong>THE ATONRÂ FUND SHARE CLASSES AND LOADS</strong>", style=header_style)],
        [Spacer(width=0, height=0)],
    ]

    # Generate header column
    table_row = []
    labels = df.columns
    for label in labels:
        table_row.append(Paragraph(f"<strong>{str(label).upper()}</strong>", style=header_style))
    table_data.append(table_row)

    # Generate table
    for index, row in df.iterrows():
        table_row = list()

        for value in row:
            # value = product_data[label]
            # if isinstance(value, (Decimal, int, float)):
            #     value_str = f"{value:.1%}"
            # else:
            #     value_str = str(value)
            value_str = value if value else ""
            table_row.append(Paragraph(str(value_str), style=row_style))
        table_data.append(table_row)

    num_cols = len(labels)

    cols = list()

    cols.extend([(width) / num_cols] * num_cols)
    rows = [row_height] * (df.shape[0] + 3)

    table = Table(table_data, colWidths=cols, rowHeights=rows)

    table_styles = [
        ("LINEBEFORE", (1, 0), (1, -1), 0.25, grid_color),
        ("LINEABOVE", (0, 1), (-1, 1), 0.25, grid_color),
        ("LINEABOVE", (0, 0), (-1, 0), 0.25, grid_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (2, 1), (-1, -1), offset / 2),
        ("BACKGROUND", (0, 0), (-1, 0), background_color),
        ("SPAN", (0, 0), (-1, 0)),  # Col Span Title
        ("SPAN", (0, 1), (-1, 1)),
    ]

    if debug:
        table_styles.extend(
            [
                ("BOX", (0, 0), (-1, -1), 0.25, grid_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, grid_color),
            ]
        )

    table.setStyle(TableStyle(table_styles))
    return table
