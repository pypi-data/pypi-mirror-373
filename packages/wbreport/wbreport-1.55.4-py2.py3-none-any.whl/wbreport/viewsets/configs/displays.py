from typing import Optional

from rest_framework.reverse import reverse
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import Display
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ReportCategoryDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="title", label="Title"),
                dp.Field(key="order", label="Order"),
            )
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["title"], ["order"]])


class ReportDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="namespace", label="Namespace"),
                dp.Field(key="parent_report", label="Parent Report"),
                dp.Field(key="category", label="Category"),
                dp.Field(key="is_active", label="Active"),
                dp.Field(key="permission_type", label="Permission Type"),
                dp.Field(key="file_disabled", label="PDF Disabled"),
                dp.Field(key="base_color", label="Color"),
                dp.Field(key="mailing_list", label="Mailing List"),
            ],
            tree=True,
            # tree_group_lookup="id_repr",
            tree_group_field="title",
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_key="parent_report",
                    filter_depth=1,
                    filter_blacklist=["parent_report__isnull"],
                    list_endpoint=reverse(
                        "wbreport:report-list",
                        args=[],
                        request=self.request,
                    ),
                )
            ],
        )

    def get_instance_display(self) -> Display:
        version_section = create_simple_section("version_section", "Versions", [["content_type"], ["object_id"]])
        version_table_section = create_simple_section("version_table_section", "Versions", [["versions"]], "versions")
        child_report_section = create_simple_section("child_report_section", "Child Reports", [["reports"]], "reports")
        return create_simple_display(
            [
                ["title", "namespace", "."],
                ["base_color", "category", "file_content_type"],
                ["is_active", "permission_type", "file_disabled"],
                ["mailing_list", "report_class", "."],
                ["version_section", "version_section", "version_section"],
                ["version_table_section", "version_table_section", "version_table_section"],
                ["child_report_section", "child_report_section", "child_report_section"],
            ],
            [child_report_section, version_table_section, version_section],
        )


class ReportVersionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="uuid", label="UUID"),
                dp.Field(key="lookup", label="Lookup"),
                dp.Field(key="title", label="Title"),
                dp.Field(key="version_date", label="Date"),
                dp.Field(key="report", label="Report"),
                dp.Field(key="is_primary", label="Is Primary"),
                dp.Field(key="disabled", label="Disabled"),
                dp.Field(key="parameters", label="Parameters"),
            )
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["title", "lookup", "uuid"],
                ["version_date", "creation_date", "update_date"],
                ["is_primary", "disabled", "disabled"],
                ["parameters", ".", "."],
            ]
        )


class ReportVersionReportDisplayConfig(ReportVersionDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="uuid", label="UUID"),
                dp.Field(key="lookup", label="Lookup"),
                dp.Field(key="title", label="Title"),
                dp.Field(key="version_date", label="Date"),
                dp.Field(key="report", label="Report"),
                dp.Field(key="is_primary", label="Is Primary"),
                dp.Field(key="disabled", label="Disabled"),
                dp.Field(key="parameters", label="Parameters"),
                dp.Field(key="comment", label="Comment"),
            )
        )
