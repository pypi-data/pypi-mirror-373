from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbreport.models import Report


class CommentSerializer(wb_serializers.Serializer):
    comment = wb_serializers.TextField(default="")


class ReportButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.HyperlinkButton(
                key="last_version",
                label="Last Version (unreleased)",
                icon=WBIcon.DOCUMENT_IN_PROGRESS.icon,
            ),
            bt.HyperlinkButton(
                key="primary_version",
                label="Primary Version",
                icon=WBIcon.DOCUMENT_PRIVATE.icon,
            ),
        }

    def get_custom_instance_buttons(self):
        default_parameters = earliest_parent_parameters = latest_parent_paremeters = dict()
        if report_id := self.view.kwargs.get("pk", None):
            report = Report.objects.get(id=report_id)
            if version := report.last_version:
                default_parameters = version.parameters
            if default_parameters:
                report.report_class.get_next_parameters(default_parameters)
            if parent_report := report.parent_report:
                if version := parent_report.earliest_version:
                    earliest_parent_parameters = version.parameters
                if version := parent_report.last_version:
                    latest_parent_paremeters = version.parameters

        class ParametersSerializer(wb_serializers.Serializer):
            parameters = wb_serializers.JSONTableField(default=default_parameters, label="Version Parameters")

        class StartEndParametersSerializer(wb_serializers.Serializer):
            start_parameters = wb_serializers.JSONTableField(
                default=earliest_parent_parameters, label="Start Parameters"
            )
            end_parameters = wb_serializers.JSONTableField(default=latest_parent_paremeters, label="End Parameters")
            comment = wb_serializers.TextField(default="")

        class GenerateNextReportSerializer(CommentSerializer):
            max_depth_only = wb_serializers.BooleanField(default=False)
            start_date = wb_serializers.DateField()
            end_date = wb_serializers.DateField()

        return self.get_custom_list_instance_buttons() | {
            bt.DropDownButton(
                label="Utility",
                icon=WBIcon.UNFOLD.icon,
                buttons=(
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbreport:report",),
                        key="generate_next_reports",
                        label="Generate Next Report",
                        icon=WBIcon.GENERATE_NEXT.icon,
                        description_fields="""
                        <p> Generate reports based on current report parameters to next iteration?</p>
                        <p> Note: This action takes a minute</p>
                        """,
                        serializer=GenerateNextReportSerializer,
                        action_label="Generate Next Report",
                        title="Generate Report to Next Iteration",
                        instance_display=create_simple_display([["start_date"], ["end_date"], ["max_depth_only"]]),
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbreport:report",),
                        key="update_versions_context",
                        label="Regenerate context",
                        icon=WBIcon.REGENERATE.icon,
                        serializer=ParametersSerializer,
                        description_fields="""
                        <p> Do you want to regenerate this report's versions?</p>
                        <p> If parameters is unset, it will recompute all report's versions</p>
                        <p> Note: This action takes few minute?</p>
                        """,
                        action_label="Regenerate versions context",
                        title="Regenerate versions context",
                        instance_display=create_simple_display([["all_versions"], ["parameters"]]),
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbreport:report",),
                        key="bundle_versions",
                        label="Bundle Versions",
                        icon=WBIcon.FOLDERS_OPEN.icon,
                        description_fields="""
                        <p>Generate a reports bundle for the specified parameters.
                        If left empty, will use the latest parameters state.</p>
                        <p> Note: This action takes around 10 minutes</p>
                        """,
                        serializer=ParametersSerializer,
                        action_label="Bundle Versions",
                        title="Bundle Versions",
                        instance_display=create_simple_display([["parameters"]]),
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbreport:report",),
                        key="bulk_create_reports",
                        label="Bulk Reports Creations",
                        icon=WBIcon.FOLDERS_ADD.icon,
                        description_fields="""
                        <p>Create all the report version between the two specified parameters set.
                        <p> Note: This action takes around 10 minutes</p>
                        """,
                        serializer=StartEndParametersSerializer,
                        action_label="Bulk Reports Creations",
                        title="Bulk Reports Creations",
                        instance_display=create_simple_display([["start_parameters"], ["end_parameters"]]),
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbreport:report",),
                        key="switch_primary_versions",
                        label="Switch Primary Versions",
                        description_fields="""
                        <p>Switch the Primary Versions of all the child reports to the given parameters. </p>
                        <p> The primary version is the one display by default</p>
                        """,
                        icon=WBIcon.SYNCHRONIZE.icon,
                        serializer=ParametersSerializer,
                        action_label="Switch Primary Versions",
                        title="Switch Primary Versions",
                        instance_display=create_simple_display([["parameters"]]),
                    ),
                ),
            )
        }


class ReportVersionButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(
                key="html",
                label="Report (HTML)",
                icon=WBIcon.LINK.icon,
            ),
            bt.HyperlinkButton(
                key="file",
                label="Report (File)",
                icon=WBIcon.SAVE.icon,
            ),
            bt.HyperlinkButton(
                key="public_html",
                label="Public Report",
                icon=WBIcon.SAVE.icon,
            ),
            bt.ActionButton(
                method=RequestType.GET,
                identifiers=("wbreport:reportversion",),
                key="update_context",
                label="Update Context",
                description_fields="""
                <p>Update and actualize context</p>
                """,
                serializer=CommentSerializer,
                icon=WBIcon.REGENERATE.icon,
                action_label="Update Context",
                title="Update Context",
            ),
            bt.ActionButton(
                method=RequestType.GET,
                identifiers=("wbreport:reportversion",),
                key="send_email",
                label="Send to Mailing List",
                description_fields="""
                <p>Send this version as email to the specified report mailing list</p>
                """,
                icon=WBIcon.MAIL.icon,
                action_label="Send Email",
                title="Send Email",
            ),
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
