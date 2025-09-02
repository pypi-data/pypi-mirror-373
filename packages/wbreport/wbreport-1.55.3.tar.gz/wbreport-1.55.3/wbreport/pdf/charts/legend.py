from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Circle
from reportlab.lib.colors import transparent


class CustomLegend(Legend):
    def _defaultSwatch(self, x, thisy, dx, dy, fillColor, strokeWidth, strokeColor):
        return Circle(
            x,
            thisy + dx / 2,
            dx / 2,
            fillColor=fillColor,
            strokeColor=transparent,
            strokeWidth=strokeWidth,
        )
