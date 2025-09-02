from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Report, ReportAsset, ReportCategory, ReportClass, ReportVersion


@admin.register(ReportAsset)
class ReportAssetModelAdmin(admin.ModelAdmin):
    list_display = ["key", "asset", "text"]


@admin.register(ReportCategory)
class ReportCategoryModelAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ("title",)


@admin.register(ReportClass)
class ReportClassModelAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ("title",)


@admin.register(ReportVersion)
class ReportVersionModelAdmin(admin.ModelAdmin):
    list_display = ["title", "uuid", "disabled", "is_primary", "creation_date", "update_date"]
    search_fields = ("title",)


class ReportVersionTabularInline(admin.TabularInline):
    model = ReportVersion
    fields = ["title", "disabled", "is_primary", "parameters"]
    readonly_fields = ("creation_date", "update_date", "uuid")
    extra = 0


class ReportTabularInline(admin.TabularInline):
    model = Report
    fields = ["title", "is_active", "permission_type"]
    extra = 0


@admin.register(Report)
class ReportModelAdmin(GuardedModelAdmin):
    list_display = ["title", "key", "category", "is_active", "permission_type"]
    search_fields = (
        "title",
        "key",
        "category__title",
    )

    fieldsets = (
        (
            "Main Information",
            {
                "fields": (
                    ("title", "namespace", "category", "logo_file"),
                    ("is_active", "permission_type", "mailing_list"),
                    ("key", "base_color", "color_palette"),
                    (
                        "report_class",
                        "parent_report",
                    ),
                    (
                        "file_content_type",
                        "file_disabled",
                    ),
                    ("parameters",),
                )
            },
        ),
        (
            "Generic Content Type",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
    )
    inlines = [ReportVersionTabularInline]
    autocomplete_fields = [
        "content_type",
        "report_class",
        "category",
    ]
