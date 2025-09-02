from typing import Any, Dict

from django.db import models
from django.template.loader import get_template
from rest_framework.reverse import reverse
from wbportfolio.models import Instrument

from wbreport.mixins import ReportMixin

from .mixins import FactsheetReportMixin


class ReportClass(FactsheetReportMixin, ReportMixin):
    HTML_TEMPLATE_FILE = "report/factsheet_menu.html"

    @classmethod
    def generate_html(cls, context: Dict[str, Any]) -> str:
        template = get_template(cls.HTML_TEMPLATE_FILE)
        return template.render(context)

    generate_file = None

    # @classmethod
    # def generate_file(cls, context: Dict[str, Any]):
    #     return None

    @classmethod
    def get_context(cls, version: models.Model) -> Dict[str, Any]:
        parameters = cls.parse_parameters(version.parameters)
        end = parameters["end"]
        products = []
        benchmarks = {}
        parent_report = version.report

        for report in parent_report.child_reports.filter(is_active=True, parameters__is_private=False).order_by(
            "object_id"
        ):
            product = report.content_object
            if product.get_prices().exists() and (
                report_version := report.versions.filter(parameters=parameters).first()
            ):
                latest_price = product.get_latest_valid_price(end)
                table = {}
                # if product.ticker:
                #     table["ticker"] = product.ticker
                table["url"] = reverse("public_report:report_version", args=[report_version.lookup])
                table["title"] = product.title
                table["currency"] = product.currency.key
                table["isin"] = product.isin
                table["price"] = float(latest_price.net_value)
                table["launch_date"] = product.inception_date
                table["bank_title"] = product.bank.title
                if report.logo_file:
                    table["logo_file"] = report.logo_file
                table["color"] = report.base_color
                product_perfs = product.get_last_performance_summary(end=latest_price.date).to_dict("records")[0]
                table["product_perf"] = product_perfs

                benchmarks_perf = {}
                # First element is the primary benchmark

                ordered_benchmarks_ids = product.to_benchmarks.order_by("-is_primary").values_list(
                    "benchmark", flat=True
                )
                if len(ordered_benchmarks_ids) > 0:
                    for benchmark_id in ordered_benchmarks_ids:
                        instrument = Instrument.objects.get(id=benchmark_id)
                        if instrument.id not in benchmarks:
                            benchmarks[instrument.id] = instrument.get_prices_df(from_date=latest_price.date)
                        tmp_val = benchmarks[instrument.id].truncate(
                            before=product.inception_date, after=latest_price.date
                        )
                        benchmark_perf = {"daily": None, "monthly": None, "yearly": None, "inception": None}
                        if not tmp_val.empty:
                            benchmark_daily = Instrument.extract_daily_performance_df(tmp_val).performance.iloc[-1]
                            benchmark_monthly = Instrument.extract_monthly_performance_df(tmp_val).performance.iloc[-1]
                            benchmark_yearly = Instrument.extract_annual_performance_df(tmp_val).performance.iloc[-1]
                            benchmark_inception = Instrument.extract_inception_performance_df(tmp_val)
                            benchmark_perf = {
                                "daily": product_perfs["daily"] - benchmark_daily,
                                "monthly": product_perfs["monthly"] - benchmark_monthly,
                                "yearly": product_perfs["yearly"] - benchmark_yearly,
                                "inception": product_perfs["inception"] - benchmark_inception,
                            }
                        benchmarks_perf[instrument.title] = benchmark_perf

                    primary_benchmark = Instrument.objects.get(id=ordered_benchmarks_ids[0])

                    table["reference_name"] = primary_benchmark.title
                    table["reference_perf"] = benchmarks_perf.pop(primary_benchmark.title)
                    table["benchmark_perf"] = benchmarks_perf

                products.append(table)
        return {"products": products, "title": parent_report.title, "date": end}
