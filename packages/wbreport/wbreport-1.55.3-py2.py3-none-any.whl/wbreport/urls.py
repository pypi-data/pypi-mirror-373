from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbreport.viewsets import viewsets

router = WBCoreRouter()

router.register(
    r"reportcategoryrepresentation",
    viewsets.ReportCategoryRepresentationViewSet,
    basename="reportcategoryrepresentation",
)
router.register(
    r"reportversionerepresentation",
    viewsets.ReportVersionRepresentationViewSet,
    basename="reportversionrepresentation",
)
router.register(
    r"reportclassrepresentation", viewsets.ReportClassRepresentationViewSet, basename="reportclassrepresentation"
)
router.register(r"reportrepresentation", viewsets.ReportRepresentationViewSet, basename="reportrepresentation")
router.register(r"report", viewsets.ReportModelViewSet, basename="report")
router.register(r"reportversion", viewsets.ReportVersionModelViewSet, basename="reportversion")
router.register(r"reportcategory", viewsets.ReportCategoryModelViewSet, basename="reportcategory")

report_router = WBCoreRouter()
report_router.register(r"version", viewsets.ReportVersionReportModelViewSet, basename="report-version")

report_version_router = WBCoreRouter()
report_version_router.register(r"rawhtml", viewsets.ReportVersionReportHTMLViewSet, basename="reportversion-rawhtml")

urlpatterns = [
    path("", include(router.urls)),
    path("report/<int:report_id>/", include(report_router.urls)),
    path("reportversion/<int:report_version_id>/", include(report_version_router.urls)),
]
