from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.units import cm
from wbreport.pdf.charts.legend import CustomLegend


def get_data_and_labels_from_df(df, color_palette, percent=True):
    data = list()
    colornamepairs = list()

    for index, row in enumerate(df.itertuples()):
        data.append(float(row.weighting))

        label = f"{row[2]*100:.1f}%" if percent else f"{row[2]:.1f}"
        colornamepairs.append((colors.HexColor(color_palette[index]), f"{row[1]} {label}"))

    return data, colornamepairs


def get_legend_height(df, r2_legend=0.3 * cm, legend_padding=1, legend_max_cols=7):
    return min(len(df), legend_max_cols) * (r2_legend + legend_padding)


def get_pie_chart_vertical_height(
    df,
    r2=2.5 * cm,
    padding=0.45 * cm,
    r2_legend=0.3 * cm,
    legend_padding=1,
    legend_max_cols=7,
):
    return 3 * padding + r2 + get_legend_height(df, r2_legend, legend_padding, legend_max_cols)


def get_pie_chart_vertical(
    df,
    width,
    height,
    color_palette,
    r2=2.5 * cm,
    padding=0.45 * cm,
    r2_legend=0.3 * cm,
    legend_padding=1,
    legend_max_cols=7,
):
    drawing = Drawing(width, height)
    pie = Pie()

    pie.width = r2
    pie.height = r2

    pie.x = (width - r2) / 2
    pie.y = height - r2 - padding
    df = df.sort_values(by=["weighting"], ascending=False)
    data, colornamepairs = get_data_and_labels_from_df(df, color_palette)

    for i, color in enumerate(colornamepairs):
        pie.slices[i].fillColor = color[0]
        pie.slices[i].strokeColor = colors.transparent
        pie.slices[i].strokeWidth = 0  # Border width for wedge
    pie.slices.strokeWidth = 0  # Width of the border around the pie chart.
    pie.data = data

    drawing.add(pie)

    legend = CustomLegend()

    legend.alignment = "right"
    legend.boxAnchor = "nw"
    legend.x = 0
    legend.y = height - r2 - 2 * padding
    legend.dx = legend.dy = r2_legend
    legend.strokeWidth = -1
    legend.columnMaximum = legend_max_cols
    legend.colorNamePairs = colornamepairs
    legend.fontName = "customfont"
    legend.fontSize = 6

    legend.deltax = 0  # Here
    legend.deltay = legend_padding
    legend.swdx = 12
    legend.swdy = 0

    legend.dxTextSpace = r2_legend

    legend.variColumn = True

    drawing.add(legend)
    return drawing


def get_pie_chart_horizontal_height(
    df,
    r2=2.5 * cm,
    padding=0.45 * cm,
    r2_legend=0.3 * cm,
    legend_padding=1,
    legend_max_cols=7,
):
    return max(
        2 * padding + r2,
        2 * padding + get_legend_height(df, r2_legend, legend_padding, legend_max_cols),
    )


def get_pie_chart_horizontal(
    df,
    width,
    height,
    color_palette,
    col_width,
    r2=2.5 * cm,
    padding=0.45 * cm,
    r2_legend=0.3 * cm,
    legend_padding=1,
    legend_max_cols=7,
    legend_x=None,
):
    drawing = Drawing(width, height)
    pie = Pie()

    pie.width = r2
    pie.height = r2

    pie.x = (col_width - r2) / 2
    pie.y = height - r2 - padding
    df = df.sort_values(by=["weighting"], ascending=False)
    data, colornamepairs = get_data_and_labels_from_df(df, color_palette)

    for i, color in enumerate(colornamepairs):
        pie.slices[i].fillColor = color[0]
        pie.slices[i].strokeColor = colors.transparent
        pie.slices[i].strokeWidth = 0  # Border width for wedge.
    pie.slices.strokeWidth = 0  # Width of the border around the pie chart.
    pie.data = data

    drawing.add(pie)

    legend = CustomLegend()

    # legend.x = 4.82 * cm
    # legend.y += 0.78 * cm

    legend_height = get_legend_height(df, r2_legend, legend_padding, legend_max_cols)

    legend.alignment = "right"
    legend.boxAnchor = "nw"

    if legend_x:
        legend.x = legend_x
    else:
        legend.x = width - col_width

    legend.y = (height + legend_height) / 2
    legend.dx = legend.dy = r2_legend
    legend.strokeWidth = -1
    legend.columnMaximum = legend_max_cols
    legend.colorNamePairs = colornamepairs
    legend.fontName = "customfont"
    legend.fontSize = 6

    legend.deltax = 0
    legend.deltay = legend_padding
    legend.swdx = 12
    legend.swdy = 0

    drawing.add(legend)
    return drawing
