import datetime as dt
from io import BytesIO

from django.template import Context, Template

from wbreport.mixins import ReportMixin


class ReportClass(ReportMixin):
    HTML_TEMPLATE_CONTENT = "<p>{{ title }}</p>"

    @classmethod
    def parse_parameters(cls, parameters):
        return {
            "iteration": parameters["iteration"],
            "end": dt.datetime.strptime(parameters["end"], "%Y-%m-%d"),
        }

    @classmethod
    def get_next_parameters(cls, parameters):
        parameters = cls.parse_parameters(parameters=parameters)
        return {
            "iteration": parameters["iteration"] + 1,
            "end": dt.datetime.strftime(parameters["end"] + dt.timedelta(days=1), "%Y-%m-%d"),
        }

    @classmethod
    def get_version_title(cls, report_title, parameters=None):
        return f'{report_title}-{parameters.get("iteration", "")}'

    @classmethod
    def get_version_date(cls, parameters):
        return parameters.get("end", None)

    @classmethod
    def get_context(cls, version):
        if not version.parameters:
            raise ValueError("Parameters needs to be defined")
        return {"title": version.title}

    @classmethod
    def generate_html(cls, context) -> str:
        template = Template(cls.HTML_TEMPLATE_CONTENT)
        return template.render(Context(context))

    @classmethod
    def generate_file(cls, context) -> BytesIO:
        output = BytesIO(context["title"].encode("utf_8"))
        return output
