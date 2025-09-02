from enum import Enum

from reportlab.graphics.charts.axes import LogYValueAxis, NormalDateXValueAxis
from reportlab.graphics.charts.lineplots import LinePlot, SimpleTimeSeriesPlot
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.units import cm


class Scale(Enum):
    ARITHMETIC = 1
    LOGARITHMIC = 2


class LogScaleTimeSeriesPlot(LinePlot):
    def __init__(self):
        super().__init__()

        class CustomYAxis(LogYValueAxis):
            def _calcTickPositions(self):
                return self._calcStepAndTickPositions()[1]

        self.xValueAxis = NormalDateXValueAxis()
        self.yValueAxis = CustomYAxis()


def get_timeseries_chart(
    data, width, height, color, fill_color, grid_color, scale, x_label_format="{mm}/{yy}", **chart_attributes
):
    width -= 0.65 * cm
    chart_map = {
        Scale.ARITHMETIC.value: SimpleTimeSeriesPlot,
        Scale.LOGARITHMIC.value: LogScaleTimeSeriesPlot,
    }
    data = [list(filter(lambda x: x[1] > 0, data[0]))]
    max_x_ticks = 20

    # ensure that if the data count is too low (e.g. less than a month range), we don't overcrowds the X axis
    if len(data[0]) < max_x_ticks:
        x_label_format = "{dd}/{mm}/{yy}"
        max_x_ticks = 10

    drawing = Drawing(width, height)

    chart = chart_map[scale]()
    chart.width = width
    chart.height = height

    for key, value in chart_attributes.items():
        setattr(chart, key, value)

    chart.data = data

    chart.lines[0].strokeWidth = 0.5
    chart.lines[0].strokeColor = color
    chart.lines[0].fillColor = fill_color
    chart.lines[0].inFill = True

    chart.yValueAxis.strokeWidth = -1
    chart.yValueAxis.strokeColor = colors.white
    chart.yValueAxis.labels.fontSize = 7
    chart.yValueAxis.labels.fontName = "customfont"
    chart.yValueAxis.labels.dx = width + 0.55 * cm
    chart.yValueAxis.maximumTicks = 100
    chart.yValueAxis.labelTextFormat = "%d"

    chart.xValueAxis.strokeWidth = 0
    chart.xValueAxis.labels.fontSize = 7
    chart.xValueAxis.labels.fontName = "customfont"
    chart.xValueAxis.maximumTicks = max_x_ticks
    chart.xValueAxis.visibleGrid = 1
    chart.xValueAxis.gridStrokeDashArray = (0.2, 0, 0.2)
    chart.xValueAxis.gridStrokeColor = grid_color
    chart.xValueAxis.xLabelFormat = x_label_format

    drawing.add(chart)
    return drawing
