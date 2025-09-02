from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ReportVersionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        return reverse("wbreport:reportversion-list", request=self.request)


class ReportEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbreport:report-list", request=self.request)


class ReportVersionReportEndpointConfig(EndpointViewConfig):
    pass


class ReportVersionReportHTMEndpointConfig(EndpointViewConfig):
    pass
