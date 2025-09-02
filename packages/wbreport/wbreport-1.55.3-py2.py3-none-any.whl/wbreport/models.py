import importlib
import uuid
from contextlib import suppress
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional

from celery import shared_task
from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.template import Context, Template
from django.utils.text import slugify
from dynamic_preferences.registries import global_preferences_registry
from guardian.shortcuts import get_objects_for_user
from mptt.models import MPTTModel, TreeForeignKey
from ordered_model.models import OrderedModel
from rest_framework.reverse import reverse
from wbcore.contrib.guardian.models.mixins import PermissionObjectModelMixin
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.models import WBModel
from wbmailing.models import MailTemplate, MassMail

User = get_user_model()


class ReportAsset(models.Model):
    """
    Assets that can be used in reports
    """

    key = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    text = models.TextField(null=True, blank=True)
    asset = models.FileField(max_length=256, upload_to="report/assets", null=True, blank=True)

    class Meta:
        verbose_name = "Report Asset"
        verbose_name_plural = "Report Assets"

    def __str__(self) -> str:
        return self.key


class ReportCategory(OrderedModel):
    """
    An utility class to support categorization in report
    """

    title = models.CharField(max_length=128)

    class Meta(OrderedModel.Meta):
        verbose_name = "Report Category"
        verbose_name_plural = "Report Categories"

    def __str__(self):
        return self.title

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbreport:reportcategory"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbreport:reportcategoryrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class ReportClass(WBModel):
    """
    This class utilises the import module framework, which import the class ReportClass in the specified
    class_path.

    This class is necessary for a report to implement custom behaviors.

    """

    title = models.CharField(max_length=256)
    class_path = models.CharField(max_length=256)
    REPORT_CLASS_DEFAULT_METHODS = [
        "has_view_permission",
        "has_change_permission",
        "has_delete_permission",
        "generate_file",
        "generate_html",
        "get_context",
        "serialize_context",
        "deserialize_context",
        "get_version_title",
        "get_version_date",
        "get_next_parameters",
    ]

    def __init__(self, *args, **kwargs):
        """
        Set the imported method from the attached module as class attributes.
        """
        if (len(args) == 3 and (class_path := args[2])) or (class_path := kwargs.get("class_path", None)):
            try:
                if ReportClassModule := getattr(importlib.import_module(class_path), "ReportClass", None):
                    for method in self.REPORT_CLASS_DEFAULT_METHODS:
                        setattr(self, method, getattr(ReportClassModule, method))
            except ModuleNotFoundError:
                for method in self.REPORT_CLASS_DEFAULT_METHODS:
                    setattr(self, method, lambda *a, **k: None)
        return super().__init__(*args, **kwargs)

    class Meta:
        verbose_name = "Report Class"
        verbose_name_plural = "Report Classes"

    def __str__(self) -> str:
        return self.title

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbreport:report"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbreport:reportrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class Report(MPTTModel, PermissionObjectModelMixin):
    """
    A class that represent the Report instance.

    Inherit PermissionObjectModelMixin to enable user object based permission
    """

    class FileContentType(models.TextChoices):
        PDF = "PDF", "application/pdf"
        CSV = "CSV", "text/csv"
        XLSX = "XLSX", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    key = models.CharField(
        max_length=256,
        default="",
        help_text="The key is like the family name: it represents the nature of the report.",
    )
    file_content_type = models.CharField(max_length=64, default=FileContentType.PDF, choices=FileContentType.choices)

    category = models.ForeignKey(
        ReportCategory,
        related_name="reports",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Report Category",
        help_text="The Visual Report category",
    )

    parent_report = TreeForeignKey(
        "self",
        related_name="child_reports",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Parent Report",
        help_text="The Parent Report attached to this report",
    )

    is_active = models.BooleanField(
        default=False,
        help_text="True if a report needs to be available for this product",
    )
    file_disabled = models.BooleanField(default=False, help_text="True if this version file needs to be disabled")
    base_color = ColorField(
        max_length=64,
        default="#FFF000",
    )

    mailing_list = models.ForeignKey(
        "wbmailing.MailingList",
        related_name="reports",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Report Mailing List",
        help_text="The Mailing List used to send the updated report link",
    )

    report_class = models.ForeignKey(
        ReportClass,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reports",
        verbose_name="Report Class",
        help_text="The method used to generate reports based on context",
    )

    title = models.CharField(max_length=256)
    namespace = models.CharField(max_length=256, default="")

    logo_file = models.FileField(max_length=256, blank=True, null=True, upload_to="report/logo")

    color_palette = models.ForeignKey(
        "color.ColorGradient",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reports",
        verbose_name="Color Palette",
        help_text="The report color palette",
    )

    parameters = models.JSONField(default=dict, encoder=DjangoJSONEncoder)

    class Meta(PermissionObjectModelMixin.Meta):
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        constraints = [
            models.UniqueConstraint(
                name="unique_parent_report_and_report",
                fields=["parent_report", "title"],
            ),
            models.UniqueConstraint(
                name="unique_content_object_and_key",
                fields=["key", "content_type", "object_id"],
            ),
        ]

        notification_types = [
            create_notification_type(
                code="wbreport.report.background_task",
                title="Report Background Task Notification",
                help_text="Sends you a notification when a background task regarding the Reports is done that you have triggered.",
            ),
        ]

    class MPTTMeta:
        parent_attr = "parent_report"

    def __str__(self) -> str:
        t = self.title
        ancestors = self.get_ancestors()

        # If the ascendants exist, make a pretty representation of the parent list.
        if ancestors.exists():
            t += " ["
            separator = " - "
            for parent_report in ancestors.order_by("-id"):
                t += parent_report.title + separator
            t = t[: t.rfind(separator)] + t[t.rfind(separator) + len(separator) :]  # remove last separator.
            t += "]"
        return t

    def save(self, *args, **kwargs):
        if not self.namespace:
            namespace = self.title
            if self.parent_report:
                namespace = f"{slugify(self.parent_report.namespace)}-{namespace}"
            self.namespace = slugify(namespace)
        if not self.key and self.parent_report and self.parent_report.key:
            self.key = self.parent_report.key

        return super().save(*args, **kwargs)

    @property
    def is_public(self) -> bool:
        return self.permission_type == PermissionObjectModelMixin.PermissionType.PUBLIC

    @property
    def primary_version(self) -> Optional["ReportVersion"]:
        """property containing the primary version (must be unique)"""
        if primary_version := self.versions.filter(is_primary=True).first():
            return primary_version
        return None

    @property
    def last_version(self) -> Optional["ReportVersion"]:
        """property containing the latest version (must be unique)"""
        if self.versions.exists():
            return self.versions.latest("version_date")
        return None

    @property
    def earliest_version(self) -> Optional["ReportVersion"]:
        """property containing the latest version (must be unique)"""
        if self.versions.exists():
            return self.versions.earliest("version_date")
        return None

    def is_accessible(self, user: Optional["User"] = None) -> bool:
        """
        Check if this report is accessible by anybody or the given user

        Args:
            user: If None, check for global permission. Otherwise, check if the given user can access the report

        Returns:
            True if report is accessible
        """
        return (user and get_objects_for_user(user, self.view_perm_str).filter(id=self.id).exists()) or self.is_public

    def get_permissions_for_user(self, user: "User", created: Optional[datetime] = None) -> Dict[str, bool]:
        """
        Return a generator of allowed (view|change|delete) permission and its editable state

        Get the default permissions from PermissionObjectMixin and extend it based on the attached report class

        Args:
            user: The user to which we get permission for the given object
            created: The permission creation date. Defaults to None.

        Returns:
            A dictionary of string permission identifier, editable state key value pairs.
        """
        base_permissions = super().get_permissions_for_user(user, created=created)
        for perm_str in ["view", "change", "delete"]:
            with suppress(NotImplementedError):
                has_perm = getattr(self.report_class, f"has_{perm_str}_permission")(self, user)
                dict_key = getattr(self, f"{perm_str}_perm_str")
                if has_perm:
                    base_permissions[dict_key] = True
                elif not has_perm and dict_key in base_permissions:
                    del base_permissions[dict_key]
        return base_permissions

    def get_or_create_version(
        self, parameters: Dict[str, str], update_context: Optional[bool] = False, comment: Optional[str] = None
    ) -> "ReportVersion":
        """
        Return the version corresponding to the specified parameters. Update its context if necessary
        Args:
            parameters: The parameters to filter against
            update_context: If True, update the returned version context
            comment: Optional comment

        Returns:
            The found or created version
        """
        if version := self.versions.filter(parameters=parameters).first():
            pass
        else:
            version = ReportVersion.objects.create(
                title=self.report_class.get_version_title(self.title, parameters),
                parameters=parameters,
                version_date=self.report_class.get_version_date(parameters),
                report=self,
            )
        if comment:
            version.save()

        if update_context:
            version.update_context()
            if not version.disabled:
                try:
                    # We try to check if the version generate a proper report
                    version.generate_html()
                except Exception:
                    version.disabled = True
                    version.save()
        return version

    def set_primary_versions(self, parameters: Dict[str, str]):
        """
        Set the version corresponding to these parameters as primary (will automatically unset the previous primary

        Args:
            parameters: The parameters to filter against
        """
        for version in self.versions.filter(parameters=parameters):
            if not version.is_primary:  # if the version wasn't the primary one, we lock it initially
                version.lock = True
            version.is_primary = True
            version.save()

    def get_context(self, **kwargs) -> Dict[str, Any]:
        """
        Get the base (default) context from the report.

        Args:
            **kwargs: keyword argument context

        Returns:
            A dictionary containing the default report context
        """
        base_context = {
            "report_title": self.title,
            "slugify_report_title": slugify(self.title),
            "report_base_color": self.base_color,
        }

        if self.color_palette:
            base_context["colors_palette"] = list(self.color_palette.get_gradient(self.base_color))
        if self.logo_file:
            # We need to store the id and retreive the file into a deserialization step to avoid pickle error
            base_context["report_logo_file_id"] = self.id
        return {**base_context, **kwargs}

    def get_gradient(self) -> List[str]:
        """
        Get the colors gradients based on the report base color

        Returns:
            The gradient list of colors
        """
        if self.color_palette and self.base_color:
            return self.color_palette.get_gradient(self.base_color)
        return []

    def get_next_parameters(self, next_parameters: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
        """
        Get the next parameters if they are not explicitly defined and if report has previous versions.
        Args:
            next_parameters: explicit next parameters.
        """
        if not next_parameters and self.versions.exists():
            next_parameters = self.report_class.get_next_parameters(self.last_version.parameters)
        return next_parameters

    # Parent Report function
    def generate_next_reports(
        self,
        next_parameters: Optional[Dict[str, str]] = None,
        comment: Optional[str] = None,
        max_depth_only: bool = False,
    ) -> None:
        """
        Generate and update context of all descendant versions whose report inherits from this parent report.
        Do not generate and update context for non-active reports.

        Args:
            next_parameters: The parameters used to create versions. If None, the current report parameters is used.
            comment: Optional report comment
            max_depth_only: Boolean that allows to generate next reports for leaves node.
        """
        self_next_parameters = self.get_next_parameters(next_parameters=next_parameters)
        reports = self.get_descendants(include_self=True).filter(is_active=True)
        if max_depth_only:
            max_depth = reports.aggregate(max_depth=models.Max("level"))["max_depth"]
            reports = reports.filter(level=max_depth)

        for report in reports.order_by(models.F("parent_report").desc(nulls_last=True)):
            # If self has already versions, we can calculate next parameters.
            # If it does not have versions, but we explicitly choose next_parameters, it creates the first version of
            # an empty report.
            if report.versions.exists() or self_next_parameters is not None:
                next_parameters = report.get_next_parameters(next_parameters=self_next_parameters)
                report.get_or_create_version(next_parameters, update_context=True, comment=comment)

    def bulk_create_child_reports(
        self, start_parameters: Dict[str, str], end_parameters: Dict[str, str], max_iteration: int = 20
    ) -> None:
        """
        Bootstrap utility function to generate multiple iterations of versions
        Args:
            start_parameters: The seed dictionary parameters to spinup the process
            end_parameters: The end parameters where the loop stops
            max_iteration: Max number of allowed iteration before exiting. Defaults to 20.
        """
        print(f"Bootstrap Iteration with parameters {start_parameters}")  # noqa: T201
        iteration = 0
        self.generate_next_reports(start_parameters)
        while start_parameters != end_parameters and iteration < max_iteration and self.report_class:
            start_parameters = self.report_class.get_next_parameters(start_parameters)
            print(f"Iteration {iteration} with parameters {start_parameters}")  # noqa: T201
            self.generate_next_reports(start_parameters)
            iteration += 1

    def set_primary_report_version(self, parameters: Optional[Dict[str, str]] = None) -> None:
        """
        Set all similar active children (all descendants including self) reports's versions as primary
        Args:
            parameters: Set all corresponding versions as primary. If None, use the report current parameters
        """
        if not parameters and self.versions.exists():
            parameters = self.last_version.parameters

        for report in self.get_descendants(include_self=True).filter(is_active=True):
            if report.versions.exists():
                primary_parameters = report.last_version.parameters if not parameters else parameters
                report.set_primary_versions(primary_parameters)

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbreport:reportrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class ReportVersion(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    lookup = models.CharField(max_length=256, default="", unique=True)

    title = models.CharField(max_length=256)
    parameters = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    context = models.JSONField(default=dict, encoder=DjangoJSONEncoder)

    version_date = models.DateField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    comment = models.TextField(default="")

    is_primary = models.BooleanField(
        default=False,
        help_text="Only one Version from a report can be considered primary and is usually the last created one",
    )
    disabled = models.BooleanField(default=False, help_text="True if version needs to be disabled")
    lock = models.BooleanField(default=False, help_text="True, the context cannot be regenerated")

    report = models.ForeignKey(
        "wbreport.Report", on_delete=models.CASCADE, verbose_name="Report", related_name="versions"
    )

    class Meta:
        verbose_name = "Report Version"
        verbose_name_plural = "Report Versions"

    @property
    def slugify_title(self):
        return slugify(self.title)

    def __str__(self):
        return f"{self.title} ({self.uuid})"

    def save(self, *args, **kwargs):
        """Override save method to ensure uniqueness of primary among report's version"""
        qs = ReportVersion.objects.filter(report=self.report, is_primary=True).exclude(id=self.id)
        if self.is_primary:
            qs.update(is_primary=False)
        elif not qs.exists():
            self.is_primary = True
        if not self.version_date:
            self.version_date = self.creation_date
        if not self.lookup:
            lookup = self.title
            if self.report.parent_report:
                lookup = f"{slugify(self.report.parent_report.namespace)}-{lookup}"
            self.lookup = slugify(lookup)
        return super().save(*args, **kwargs)

    @property
    def deserialized_context(self) -> Dict[str, Any]:
        context = self.report.report_class.deserialize_context(self.context)

        # we add possible report parameters into the context
        for k, v in self.report.parameters.items():
            context[f"report_{k}"] = v
        return context

    @property
    def filename(self):
        base_filename = self.report.parameters.get("filename", "report_{slugify_title}").format(
            slugify_title=self.slugify_title, **model_to_dict(self)
        )
        return f"{base_filename}.{Report.FileContentType[self.report.file_content_type].name.lower()}"

    def get_context(self, **kwargs) -> Dict[str, Any]:
        """
        Get the base context and the ReportClass module get_context for the version.

        Args:
            **kwargs: Divers keyword arguments to be injected in the get_context function

        Returns:
            A dictionary containing the dynamic and base version context
        """
        context = self.report.report_class.get_context(self)
        base_context = self.report.get_context(**kwargs)
        return {
            "uuid": str(self.uuid),
            "download_url": reverse("public_report:report_download_version_file", args=[self.uuid]),
            "version_title": self.title,
            "slugify_version_title": slugify(self.title),
            "comment": self.comment,
            **context,
            **base_context,
        }

    def update_context(self, silent: bool | None = True, force_context_update: bool = False, **kwargs):
        """
        Update version context. If an error is encounter, we disabled automatically this version

        Args:
            **kwargs: Divers keyword arguments to be injected in the get_context function
        """
        if not self.lock or force_context_update:
            if silent:
                try:
                    self.context = self.get_context(**kwargs)
                    self.disabled = False
                except Exception as e:
                    print(f"Error while updating Context for snap {self.id} {e}")  # noqa: T201
                    self.disabled = True
            else:
                self.context = self.get_context(**kwargs)
            self.context = self.report.report_class.serialize_context(self.context)
            self.save()

    def generate_file(self) -> BytesIO:
        """
        Generate the file file (BytesIO object) given the context by calling the method generate_file in ReportClass

        Returns:
            The BytesIO object containing the generated file
        """
        file = self.report.report_class.generate_file(self.deserialized_context)
        file.name = self.filename
        return file

    def generate_html(self) -> str:
        """
        Generate the html given the context by calling the method generate_html in ReportClass

        Returns:
            The generated html as string
        """
        return self.report.report_class.generate_html(self.deserialized_context)

    def send_mail(self, template: Optional[str] = None, base_message: Optional[str] = None):
        """
        Send the version as a file in a email to the mailing list specified in the parent report.

        Args:
            template: The template to use as mail body. Defaults to None (and the default module template)
            base_message: The base mail message. Defaults to None
        """
        if not base_message:
            base_message = """
<p>The monthly report for <strong>{{ version_title }}</strong> has just been updated. You can find it <a href={{ report_version_url }}>here</a>.</p>
<p>You can download it as a file by clicking on the "save" button at its bottom right.</p>
            """
        if not template:
            global_preferences = global_preferences_registry.manager()
            report_template_id = global_preferences["report__report_mail_template_id"]
            template = MailTemplate.objects.get(id=report_template_id)

        endpoint = reverse("public_report:report_version", args=[self.lookup])

        context = {"report_version_url": f"{settings.BASE_ENDPOINT_URL}{endpoint}", **self.deserialized_context}
        body = Template(base_message).render(Context(context))
        mass_mail = MassMail.objects.create(
            template=template, from_email=settings.DEFAULT_FROM_EMAIL, subject=f"{self.title} report update", body=body
        )
        mass_mail.mailing_lists.add(self.report.mailing_list)
        mass_mail.submit()
        mass_mail.send()
        mass_mail.save()

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbreport:reportversion"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbreport:reportversionrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


@receiver(models.signals.post_save, sender="wbreport.ReportVersion")
def generate_version_context_if_null(sender, instance, created, raw, **kwargs):
    """
    Generate report version context on save
    """
    if created and not instance.context:
        update_context_as_task.apply_async((instance.id,), countdown=30)


@shared_task()
def generate_next_reports_as_task(report_id, parameters=None, user=None, comment=None, max_depth_only=False):
    """
    Trigger the Report generate_next_reports as a task
    """
    report = Report.objects.get(id=report_id)
    report.generate_next_reports(next_parameters=parameters, comment=comment, max_depth_only=max_depth_only)
    if user:
        send_notification(
            code="wbreport.report.background_task",
            title="The next reports generation task is complete",
            body="You can now refresh the report widget to display its new parameters state",
            user=user,
        )


@shared_task()
def bulk_create_child_reports_as_task(report_id, start_parameters, end_parameters, user=None):
    """
    Trigger the Report generate_next_reports as a task
    """
    report = Report.objects.get(id=report_id)
    report.bulk_create_child_reports(start_parameters, end_parameters)
    if user:
        send_notification(
            code="wbreport.report.background_task",
            title="The bulk reports creation task is complete",
            body="You can now refresh the report widget to access to all generated reports",
            user=user,
        )


@shared_task()
def update_context_as_task(report_version_id, user=None, comment=None):
    """
    Trigger the Report Version update_report_context as a task
    """
    version = ReportVersion.objects.get(id=report_version_id)
    if comment:
        version.comment = comment
        version.save()
    version.update_context()
    if user:
        send_notification(
            code="wbreport.report.background_task",
            title="The report version context refresh task is complete",
            body="You can now acces the report html page to see the updated context",
            user=user,
        )


@shared_task()
def update_version_context_as_task(report_id, parameters=None, user=None):
    """
    Trigger the Report Version update_report_context as a task
    """
    for report in Report.objects.filter(
        models.Q(is_active=True) & (models.Q(id=report_id) | models.Q(parent_report=report_id))
    ).distinct():
        print(  # noqa: T201
            f'Updating context for report {str(report)} and version parameters {parameters if parameters else "{all}"}'
        )
        versions = report.versions.filter(disabled=False)
        if parameters:
            versions = versions.filter(parameters=parameters)
        for version in versions.all():
            version.update_context()
    if user:
        send_notification(
            code="wbreport.report.background_task",
            title="The context update of all the report versions is complete",
            body="You can now acces the report html page to see the updated context",
            user=user,
        )


@shared_task()
def set_primary_report_version_as_task(report_id, parameters=None, user=None):
    """
    Trigger the Report set_primary_versions as a task
    """
    report = Report.objects.get(id=report_id)
    report.set_primary_report_version(parameters)
