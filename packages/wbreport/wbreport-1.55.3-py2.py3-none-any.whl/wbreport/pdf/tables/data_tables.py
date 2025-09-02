from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def get_simple_data_table(
    headers,
    data,
    width,
    header_row_height,
    data_row_height,
    margin,
    header_style,
    data_style,
    grid_color,
    offset=None,
    debug=False,
):
    table_data = list()

    # Generate Headers
    table_row = list()
    if offset:
        table_row.append(Spacer(width=0, height=0))

    for header in headers[:-1]:
        table_row.extend([Paragraph(header, style=header_style), Spacer(width=0, height=0)])
    else:
        table_row.append(Paragraph(headers[-1], style=header_style))

    table_data.append(table_row)
    table_data.append([Spacer(width=0, height=0) for _ in range(len(data) + (1 if offset else 0))])
    for row in data:
        table_row = list()
        if offset:
            table_row.append(Spacer(width=0, height=0))

        for item in row[:-1]:
            table_row.extend([Paragraph(item, style=data_style), Spacer(width=0, height=0)])
        else:
            table_row.append(Paragraph(row[-1], style=data_style))

        table_data.append(table_row)

    rows = [header_row_height, 0.16 * cm]
    rows.extend([data_row_height] * len(data))

    cols = list()
    if offset:
        cols.append(offset)

    col_width = (width - (offset or 0) - (len(headers) - 1) * margin) / len(headers)
    cols.extend([col_width, margin] * len(headers))

    table = Table(table_data, colWidths=cols, rowHeights=rows)
    table_styles = [
        ("LINEABOVE", (1, 0), (1, 0), 0.25, grid_color),
        ("LINEBELOW", (1, 0), (1, 0), 0.25, grid_color),
        ("LINEABOVE", (3, 0), (3, 0), 0.25, grid_color),
        ("LINEBELOW", (3, 0), (3, 0), 0.25, grid_color),
        ("LINEABOVE", (5, 0), (5, 0), 0.25, grid_color),
        ("LINEBELOW", (5, 0), (5, 0), 0.25, grid_color),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
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
