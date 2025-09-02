from django.urls import path

from wbreport.viewsets import viewsets

urlpatterns = [
    path("<str:namespace>/", viewsets.report, name="report"),
    path("version/<str:lookup>/", viewsets.report_version, name="report_version"),
    path(
        "download_version_file/<str:uuid>/", viewsets.download_report_version_file, name="report_download_version_file"
    ),
]
