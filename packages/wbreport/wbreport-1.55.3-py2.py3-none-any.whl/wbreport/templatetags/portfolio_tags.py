from datetime import date, datetime
from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def percent_filter(value, precision=2):
    if value is not None:
        if isinstance(value, float) or isinstance(value, Decimal):
            return f"{value:,.{precision}%}"
        else:
            return value
    return ""


@register.filter
def value_filter(value, precision=1):
    if value is not None:
        if isinstance(value, float) or isinstance(value, Decimal):
            return "%.*f" % (precision, value)
        elif isinstance(value, datetime) or isinstance(value, date):
            return value.strftime("%d-%b-%y")
        else:
            return value
    return ""


@register.filter
def parse_title_date(value):
    if value is not None and not isinstance(value, str):
        return value.strftime("%B %Y")
    return value
