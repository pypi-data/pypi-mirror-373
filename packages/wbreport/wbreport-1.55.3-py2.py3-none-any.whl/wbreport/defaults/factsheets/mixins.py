from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Any, Dict


class FactsheetReportMixin:
    @classmethod
    def get_version_title(cls, report_title: str, parameters: Dict[str, Any]) -> str:
        parameters = cls.parse_parameters(parameters)
        end = parameters["end"]
        return f'{report_title} - {end.strftime("%b %Y")}'

    @classmethod
    def parse_parameters(cls, parameters: Dict[str, str]) -> Dict[str, Any]:
        return {
            "start": datetime.strptime(parameters["start"], "%Y-%m-%d"),
            "end": datetime.strptime(parameters["end"], "%Y-%m-%d"),
        }

    @classmethod
    def get_next_parameters(cls, parameters: Dict[str, str]) -> Dict[str, str]:
        parameters = cls.parse_parameters(parameters)
        end = parameters["end"]
        start = end
        next_month = end.month + 1
        next_year = end.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        end = date(next_year, next_month, day=monthrange(next_year, next_month)[1])

        while end.weekday() in [5, 6]:  # Mon-Fri are 0-4
            end -= timedelta(days=1)

        return {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")}
