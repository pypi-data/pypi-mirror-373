import json

from django.db.models import Case, Exists, F, IntegerField, OuterRef, When
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page
from rest_framework import filters, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    action,
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.authentication.authentication import (
    JWTCookieAuthentication,
    QueryTokenAuthentication,
)
from wbcore.contrib.guardian.viewsets.mixins import GuardianFilterMixin

from wbreport.filters import ReportFilterSet, ReportVersionFilterSet
from wbreport.models import (
    Report,
    ReportCategory,
    ReportClass,
    ReportVersion,
    bulk_create_child_reports_as_task,
    generate_next_reports_as_task,
    set_primary_report_version_as_task,
    update_context_as_task,
    update_version_context_as_task,
)
from wbreport.serializers import (
    ReportCategoryModelSerializer,
    ReportCategoryRepresentationSerializer,
    ReportClassRepresentationSerializer,
    ReportModelSerializer,
    ReportRepresentationSerializer,
    ReportVersionModelSerializer,
    ReportVersionRepresentationSerializer,
)
from wbreport.tasks import generate_and_send_current_report_file
from wbreport.viewsets.configs import (
    ReportButtonConfig,
    ReportCategoryDisplayConfig,
    ReportDisplayConfig,
    ReportEndpointConfig,
    ReportTitleConfig,
    ReportVersionButtonConfig,
    ReportVersionDisplayConfig,
    ReportVersionEndpointConfig,
    ReportVersionReportDisplayConfig,
    ReportVersionReportEndpointConfig,
    ReportVersionReportHTMEndpointConfig,
    ReportVersionReportTitleConfig,
    ReportVersionTitleConfig,
)


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, JWTCookieAuthentication, QueryTokenAuthentication])
def report(request, namespace):
    report = get_object_or_404(Report, namespace=namespace, is_active=True)
    if (version := report.primary_version) and not version.disabled:
        # Need the report to be public or the user to have access
        if version.report.is_accessible(request.user):
            return HttpResponse(version.generate_html())
    return render(
        request,
        "errors/custom.html",
        {
            "title": "Report Unavailable",
            "header": "Report Unavailable",
            "description": "If you thing this report should be enabled, please " "contact a system administrator",
        },
        status=status.HTTP_403_FORBIDDEN,
    )


@api_view(["GET"])
@cache_page(None, key_prefix="report")
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, JWTCookieAuthentication, QueryTokenAuthentication])
def download_report_version_file(request, uuid):
    version = get_object_or_404(ReportVersion, uuid=uuid, report__is_active=True, disabled=False)
    if version.report.is_accessible(request.user):
        output = version.generate_file()
        if output:
            return FileResponse(
                output,
                as_attachment=True,
                filename=output.name,
                content_type=Report.FileContentType[version.report.file_content_type].label,
            )
    return HttpResponse(
        "No PDF report for this version, please contact an administrator", status=status.HTTP_403_FORBIDDEN
    )


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, JWTCookieAuthentication, QueryTokenAuthentication])
def report_version(request, lookup):
    version = get_object_or_404(ReportVersion, lookup=lookup, report__is_active=True, disabled=False)
    # Need the report to be public or the user to have access
    if version.report.is_accessible(request.user):
        return HttpResponse(version.generate_html())
    return render(
        request,
        "errors/custom.html",
        {
            "title": "Report Unavailable",
            "header": "Report Unavailable",
            "description": "If you thing this report should be enabled, please " "contact a system administrator",
        },
        status=status.HTTP_403_FORBIDDEN,
    )


class ReportCategoryRepresentationViewSet(viewsets.RepresentationViewSet):
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ordering = ("title",)
    search_fields = ("title",)
    serializer_class = ReportCategoryRepresentationSerializer
    queryset = ReportCategory.objects.all()


class ReportRepresentationViewSet(viewsets.RepresentationViewSet):
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ordering = ("title",)
    search_fields = ("title",)
    serializer_class = ReportRepresentationSerializer
    queryset = Report.objects.all()


class ReportClassRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = ordering = ("title",)
    search_fields = ("title",)
    serializer_class = ReportClassRepresentationSerializer
    queryset = ReportClass.objects.all()


class ReportVersionRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = ordering = ("title",)
    search_fields = ("title",)
    serializer_class = ReportVersionRepresentationSerializer
    queryset = ReportVersion.objects.all()


class ReportCategoryModelViewSet(viewsets.ModelViewSet):
    serializer_class = ReportCategoryModelSerializer
    ordering_fields = ("title", "order")
    ordering = ("-title",)
    search_fields = ("title",)

    display_config_class = ReportCategoryDisplayConfig

    queryset = ReportCategory.objects.all()


class ReportModelViewSet(GuardianFilterMixin, viewsets.ModelViewSet):
    serializer_class = ReportModelSerializer
    ordering_fields = (
        "title",
        "parent_report__title",
        "category__title",
        "is_active",
        "permission_type",
        "base_color",
        "mailing_list__title",
    )
    ordering = ("title",)
    search_fields = ("title",)
    filterset_class = ReportFilterSet
    display_config_class = ReportDisplayConfig
    endpoint_config_class = ReportEndpointConfig
    title_config_class = ReportTitleConfig
    button_config_class = ReportButtonConfig

    queryset = Report.objects.annotate(
        has_children=Exists(Report.objects.filter(parent_report=OuterRef("pk"))),
        _group_key=Case(When(has_children=True, then=F("id")), default=None, output_field=IntegerField()),
    )

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def bundletreport(self, request, pk=None):
        if request.user.is_superuser:
            report = get_object_or_404(Report, pk=pk)
            try:
                parameters = json.loads(request.POST["parameters"])
            except KeyError:
                parameters = report.last_version.parameters if report.versions.exists() else None
            generate_and_send_current_report_file.delay(request.user.id, pk, parameters=parameters)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def switchprimaryversions(self, request, pk=None):
        if request.user.is_superuser:
            report = get_object_or_404(Report, pk=pk)
            try:
                parameters = json.loads(request.POST["parameters"])
            except KeyError:
                parameters = report.last_version.parameters if report.versions.exists() else None
            set_primary_report_version_as_task.delay(report.pk, parameters=parameters)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def generatenextreports(self, request, pk=None):
        if request.user.is_superuser:
            parameters = None
            if (start := request.GET.get("start_date", None)) and (end := request.GET.get("end_date", None)):
                parameters = {"start": start, "end": end}
            generate_next_reports_as_task.delay(
                pk,
                user=request.user,
                parameters=parameters,
                comment=request.GET.get("comment", ""),
                max_depth_only=request.GET.get("max_depth_only", False) == "true",
            )
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def bulkcreatereport(self, request, pk=None):
        if request.user.is_superuser:
            start_parameters = end_parameters = None
            if start_parameters_str := request.POST.get("start_parameters", None):
                start_parameters = json.loads(start_parameters_str)
            if end_parameters_str := request.POST.get("end_parameters", None):
                end_parameters = json.loads(end_parameters_str)

            if start_parameters and end_parameters:
                bulk_create_child_reports_as_task.delay(pk, start_parameters, end_parameters, user=request.user)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def updatecontext(self, request, pk=None):
        if request.user.is_superuser:
            report = get_object_or_404(Report, pk=pk)
            if report.versions.exists():
                try:
                    parameters = json.loads(request.POST["parameters"])
                except KeyError:
                    parameters = report.last_version.parameters
                update_version_context_as_task.delay(pk, parameters=parameters, user=request.user)
        return Response({}, status=status.HTTP_200_OK)


class ReportVersionModelViewSet(viewsets.ModelViewSet):
    serializer_class = ReportVersionModelSerializer
    ordering_fields = (
        "uuid",
        "report",
        "title",
        "version_date",
        "creation_date",
        "update_date",
        "is_primary",
        "disabled",
    )
    ordering = ("-version_date",)
    search_fields = ("title", "report__title")
    filterset_class = ReportVersionFilterSet

    display_config_class = ReportVersionDisplayConfig
    endpoint_config_class = ReportVersionEndpointConfig
    title_config_class = ReportVersionTitleConfig
    button_config_class = ReportVersionButtonConfig

    queryset = ReportVersion.objects.all()

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def sendemail(self, request, pk=None):
        version = ReportVersion.objects.get(id=pk)
        if version:
            version.send_mail()
            return Response({}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def updatecontext(self, request, pk=None):
        update_context_as_task.delay(pk, request.user, comment=request.GET.get("comment", ""))
        return Response({}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
        renderer_classes=[StaticHTMLRenderer],
        authentication_classes=[JWTCookieAuthentication],
    )
    def html(self, request, pk=None):
        version = get_object_or_404(ReportVersion, id=pk, disabled=False, report__is_active=True)
        if version.report.is_accessible(request.user):
            return HttpResponse(version.generate_html())
        return Response({}, status=status.HTTP_401_UNAUTHORIZED)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
        authentication_classes=[JWTCookieAuthentication],
    )
    def file(self, request, pk=None):
        version = get_object_or_404(ReportVersion, id=pk, disabled=False, report__is_active=True)
        if version.report.is_accessible(request.user):
            output = version.generate_file()
            output.seek(0)
            if output:
                return FileResponse(
                    output,
                    as_attachment=True,
                    filename=output.name,
                    content_type=Report.FileContentType[version.report.file_content_type].label,
                )
        return Response({}, status=status.HTTP_401_UNAUTHORIZED)


class ReportVersionReportModelViewSet(ReportVersionModelViewSet):
    display_config_class = ReportVersionReportDisplayConfig
    endpoint_config_class = ReportVersionReportEndpointConfig
    title_config_class = ReportVersionReportTitleConfig

    def get_queryset(self):
        report = Report.objects.get(id=self.kwargs["report_id"])
        if report.is_accessible(self.request.user):
            return super().get_queryset().filter(report=self.kwargs["report_id"])
        return ReportVersion.objects.none()


class ReportVersionReportHTMLViewSet(viewsets.HTMLViewSet):
    IDENTIFIER = "wbreport:reportversion-rawhtml"
    queryset = ReportVersion.objects.all()

    endpoint_config_class = ReportVersionReportHTMEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["report_version_id"])

    def get_html(self, queryset) -> str:
        version = get_object_or_404(ReportVersion, id=self.kwargs["report_version_id"])
        if version.report.is_accessible(self.request.user):
            return version.generate_html()
        return ""
