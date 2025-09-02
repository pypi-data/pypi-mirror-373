from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, transparent
from reportlab.lib.formatters import DecimalFormatter
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable
from wbreport.pdf.charts.legend import CustomLegend


class ThemeBreakdown(Flowable):
    def __init__(self, df, width, grid_color):
        # self.df = self.df[self.df["allocation_end"] > 0]
        self.df = df[df["allocation_end"] != 0]
        self.pie_padding = 0.45 * cm
        self.pie_diameter = 2.5 * cm
        self.pie_legend_diameter = 0.3 * cm
        self.pie_legend_padding = 1
        self.pie_legend_max_cols = len(self.df)

        self.bar_width = 0.24 * cm
        self.bar_padding = 0.3 * cm
        self.bar_max_label_width = 3.35 * cm
        self.bar_label_offset = 5

        self.font_size = 6
        self.font_name = "customfont"

        self.width = width
        self.height = self.get_height()

        self.grid_color = grid_color

    def get_pie_chart_legend_height(self):
        return min(len(self.df), self.pie_legend_max_cols) * (self.pie_legend_diameter + self.pie_legend_padding)

    def get_pie_chart_height(self):
        return max(
            2 * self.pie_padding + self.pie_diameter,
            2 * self.pie_padding + self.get_pie_chart_legend_height(),
        )

    def get_bar_chart_height(self):
        num_bars = len(self.df) * 2

        return num_bars * self.bar_width + num_bars / 2 * self.bar_padding

    def get_height(self):
        pie_chart_height = self.get_pie_chart_height()
        bar_chart_height = self.get_bar_chart_height()

        return pie_chart_height + bar_chart_height + 40

    def get_pie_chart_with_legend(self):
        pie = Pie()

        pie.x = (self.width / 2 - self.pie_diameter) / 2
        pie.y = self.height - self.pie_diameter - self.pie_padding
        pie.width = self.pie_diameter
        pie.height = self.pie_diameter

        pie_data = list()
        pie_colornamepairs = list()
        max_width_colornamepair = 0

        self.df = self.df.sort_values(by=["allocation_end"], ascending=False).rename(
            columns={"underlying_instrument__title_repr": "underlying_instrument__name_repr"}
        )
        for index, row in enumerate(self.df.itertuples()):
            if row.allocation_end > 0:
                label = f"{row.underlying_instrument__name_repr} {row.allocation_end*100:.1f}%"
                pie_data.append(float(row.allocation_end))
                pie.slices[index].fillColor = HexColor(row.color)
                pie.slices[index].strokeColor = transparent
            else:
                label = f"{row.underlying_instrument__name_repr}"
            pie_colornamepairs.append((HexColor(row.color), label))
            max_width_colornamepair = max(max_width_colornamepair, stringWidth(label, "customfont", 6))

        pie.slices.strokeWidth = -1
        pie.data = pie_data

        legend = CustomLegend()

        legend.fontSize = 6
        legend.fontName = "customfont"
        legend.alignment = "right"
        legend.boxAnchor = "nw"
        legend.x = self.width / 2 - pie.width / 2 + self.pie_padding
        legend.y = self.height - self.pie_padding
        legend.dx = legend.dy = self.pie_legend_diameter
        legend.columnMaximum = self.pie_legend_max_cols
        legend.colorNamePairs = pie_colornamepairs
        legend.strokeWidth = -1

        legend.deltax = 0
        legend.deltay = self.pie_legend_padding
        legend.swdx = 12
        legend.swdy = 0

        return pie, legend

    def get_bar_chart_with_legend(self):
        bar = HorizontalBarChart()

        self.df["contribution_total"] = self.df["contribution_total"] * 100
        self.df["performance_total"] = self.df["performance_total"] * 100
        self.df = self.df.sort_values(by=["performance_total"])

        bar.data = [self.df.contribution_total.to_list(), self.df.performance_total.to_list()]

        bar.x = 0
        bar.y = 40

        bar.width = self.width - self.bar_label_offset - stringWidth("00.00%", self.font_name, self.font_size)
        bar.height = self.get_bar_chart_height()

        bar.barLabels.dx = self.bar_label_offset
        bar.barLabelFormat = DecimalFormatter(1, suffix="%")
        bar.barLabels.dy = 0
        bar.barLabels.boxAnchor = "w"
        bar.barLabels.boxTarget = "hi"
        bar.barLabels.fontSize = self.font_size
        bar.barLabels.fontName = self.font_name
        bar.barLabels.boxFillColor = None
        bar.barLabels.boxStrokeColor = None

        bar.groupSpacing = self.bar_padding
        bar.barWidth = self.bar_width
        bar.bars.strokeWidth = 0
        bar.bars.strokeColor = None

        for index, color in enumerate(self.df.color):
            bar.bars[(0, index)].fillColor = HexColor(f"{color}80", hasAlpha=True)
            bar.bars[(1, index)].fillColor = HexColor(color)

        bar.valueAxis.labelTextFormat = DecimalFormatter(0, suffix="%")
        bar.valueAxis.labels.fontName = "customfont"
        bar.valueAxis.labels.fontSize = 6
        bar.valueAxis.maximumTicks = 10
        bar.valueAxis.strokeWidth = 0.5
        bar.valueAxis.gridStrokeColor = self.grid_color
        bar.valueAxis.gridStrokeDashArray = (0.2, 0, 0.2)
        bar.valueAxis.visibleGrid = True
        bar.valueAxis.forceZero = True

        bar.categoryAxis.tickLeft = 0
        bar.categoryAxis.strokeWidth = 0.5

        legend = CustomLegend()
        legend.x = 30
        legend.y = 0

        legend.alignment = "right"
        legend.boxAnchor = "sw"
        legend.strokeWidth = -1
        legend.columnMaximum = 1
        legend.colorNamePairs = [
            (HexColor(0xAAAAAA), "Monthly Performance"),
            (HexColor(0xAAAAAA80, hasAlpha=True), "Monthly Contribution"),
        ]
        legend.fontName = self.font_name
        legend.fontSize = self.font_size
        legend.deltax = 0
        legend.swdx = 12
        legend.swdy = 0

        return bar, legend

    def draw(self):
        drawing = Drawing(self.width, self.height)
        pie_chart, pie_legend = self.get_pie_chart_with_legend()
        bar_chart, bar_legend = self.get_bar_chart_with_legend()
        drawing.add(pie_chart)
        drawing.add(pie_legend)
        drawing.add(bar_chart)
        drawing.add(bar_legend)
        drawing.drawOn(self.canv, 0, 0)
