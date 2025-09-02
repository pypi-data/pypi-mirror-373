from wbcore.metadata.configs.titles import TitleViewConfig

from wbreport.models import Report


class ReportVersionTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Versions"

    def get_instance_title(self):
        return "Version: {{title}}"

    def get_create_title(self):
        return "New Version"


class ReportTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Reports"

    def get_instance_title(self):
        return "Report: {{title}}"

    def get_create_title(self):
        return "New Report"


class ReportVersionReportTitleConfig(ReportVersionTitleConfig):
    def get_list_title(self):
        report = Report.objects.get(id=self.view.kwargs["report_id"])
        return f"Versions for report {str(report)}"
