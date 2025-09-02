from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.content_type.serializers import (
    ContentTypeRepresentationSerializer,
    DynamicObjectIDRepresentationSerializer,
)
from wbcore.contrib.authentication.authentication import inject_short_lived_token
from wbmailing.serializers import MailingListRepresentationSerializer

from .models import Report, ReportCategory, ReportClass, ReportVersion


class ReportVersionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ReportVersion
        fields = (
            "id",
            "title",
        )


class ReportClassRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ReportClass
        fields = ("id", "title")


class ReportCategoryRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ReportCategory
        fields = ("id", "title")


class ReportRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="report:report-detail")

    class Meta:
        model = Report
        fields = ("id", "title", "_detail")


class ReportCategoryModelSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = ReportCategory
        fields = ("id", "title")


class ReportVersionModelSerializer(wb_serializers.ModelSerializer):
    _report = ReportRepresentationSerializer(source="report")
    parameters = wb_serializers.JSONTableField()

    @wb_serializers.register_resource()
    def version_resources(self, instance, request, user):
        res = {}
        if instance.report.is_accessible(user) and instance.report.is_active and not instance.disabled:
            if user.is_superuser:
                res["update_context"] = reverse(
                    "wbreport:reportversion-updatecontext", args=[instance.id], request=request
                )
            if not instance.report.file_disabled:
                res["file"] = reverse("report:reportversion-file", args=[instance.id], request=request)

            res["html"] = reverse("wbreport:reportversion-rawhtml-list", args=[instance.id], request=request)
            if instance.report.mailing_list:
                res["send_email"] = reverse("report:reportversion-sendemail", args=[instance.id], request=request)
        return res

    from wbcore.contrib.authentication.authentication import TokenAuthentication

    @wb_serializers.register_resource()
    @inject_short_lived_token(view_name="public_report:report_version")
    def public_html_resources(self, instance, request, user):
        res = {}
        if instance.report.is_accessible(user) and instance.report.is_active and not instance.disabled:
            res["public_html"] = reverse("public_report:report_version", args=[instance.lookup], request=request)
        return res

    class Meta:
        model = ReportVersion
        fields = (
            "id",
            "uuid",
            "title",
            "creation_date",
            "version_date",
            "update_date",
            "is_primary",
            "disabled",
            "lookup",
            "parameters",
            "comment",
            "report",
            "_report",
            "parameters",
            "_additional_resources",
        )


class ReportModelSerializer(wb_serializers.ModelSerializer):
    _mailing_list = MailingListRepresentationSerializer(many=False, source="mailing_list")
    _category = ReportCategoryRepresentationSerializer(source="category")
    _report_class = ReportClassRepresentationSerializer(source="report_class")
    _parent_report = ReportRepresentationSerializer(source="parent_report")
    _content_type = ContentTypeRepresentationSerializer(source="content_type")
    _object_id = DynamicObjectIDRepresentationSerializer(
        source="object_id",
        optional_get_parameters={"content_type": "content_type"},
        depends_on=[{"field": "content_type", "options": {}}],
    )
    _group_key = wb_serializers.CharField(read_only=True)

    @wb_serializers.register_resource()
    def versions_resources(self, instance, request, user):
        res = {}
        if instance.is_accessible(user):
            res["versions"] = reverse("wbreport:report-version-list", args=[instance.id], request=request)
            res["reports"] = f'{reverse("wbreport:report-list", args=[], request=request)}?parent_report={instance.id}'
            if instance.child_reports.exists():
                res["bundle_versions"] = reverse("wbreport:report-bundletreport", args=[instance.id], request=request)

            if user.is_superuser:
                res.update(
                    {
                        "bulk_create_reports": reverse(
                            "wbreport:report-bulkcreatereport", args=[instance.id], request=request
                        ),
                        "generate_next_reports": reverse(
                            "wbreport:report-generatenextreports", args=[instance.id], request=request
                        ),
                        "switch_primary_versions": reverse(
                            "wbreport:report-switchprimaryversions", args=[instance.id], request=request
                        ),
                        "update_versions_context": reverse(
                            "wbreport:report-updatecontext", args=[instance.id], request=request
                        ),
                    }
                )
        return res

    @wb_serializers.register_resource()
    @inject_short_lived_token(view_name="public_report:report_version")
    def public_resources(self, instance, request, user):
        res = {}
        if instance.is_accessible(user) and (
            primary_snap := instance.versions.filter(is_primary=True, disabled=False).first()
        ):
            res["primary_version"] = reverse(
                "public_report:report_version", args=[primary_snap.lookup], request=request
            )

            if (
                (last_version := instance.versions.latest("creation_date"))
                and not last_version.disabled
                and last_version != primary_snap
            ):
                res["last_version"] = reverse(
                    "public_report:report_version", args=[last_version.lookup], request=request
                )
        return res

    class Meta:
        model = Report
        dependency_map = {
            "object_id": ["content_type"],
        }
        fields = (
            "id",
            "title",
            "namespace",
            "_mailing_list",
            "mailing_list",
            "category",
            "_category",
            "report_class",
            "_report_class",
            "is_active",
            "base_color",
            "permission_type",
            "file_disabled",
            "file_content_type",
            "title",
            "logo_file",
            "_parent_report",
            "parent_report",
            "_content_type",
            "object_id",
            "_object_id",
            "content_type",
            "_additional_resources",
            "_group_key",
        )
