import datetime as dt

import pytest
from django.test import override_settings
from faker import Faker
from wbmailing.models import MassMail
from wbreport.models import ReportVersion

fake = Faker()


@pytest.mark.django_db
class TestReportAssetModel:
    def test_init(self, report_asset):
        assert report_asset.id is not None

    def test_str(self, report_asset):
        assert str(report_asset) == report_asset.key


@pytest.mark.django_db
class TestReportCategoryModel:
    def test_init(self, report_category):
        assert report_category.id is not None

    def test_str(self, report_category):
        assert str(report_category) == report_category.title


@pytest.mark.django_db
class TestReportClassModel:
    def test_init(self, report_class):
        assert report_class.id is not None

    def test_get_context(self, report_class, report_version_factory):
        report_version = report_version_factory.create(parameters={"a": "b"})
        context = report_class.get_context(report_version)
        assert context == {"title": report_version.title}

    @pytest.mark.parametrize("report_title", [fake.word()])
    def test_get_version_title(self, report_class, report_title):
        title = report_class.get_version_title(report_title, dict(iteration=0))
        assert title == f"{report_title}-{0}"
        assert title

    def test_get_version_date(self, report_class):
        assert report_class.get_version_date({"a": "b"}) is None

    @pytest.mark.parametrize("title", [fake.word()])
    def test_generate_file(self, title, report_class):
        output = report_class.generate_file({"title": title})
        assert output.getvalue().decode("utf_8") == title

    @pytest.mark.parametrize("title", [fake.word()])
    def test_generate_html(self, title, report_class):
        output = report_class.generate_html({"title": title})
        assert output == f"<p>{title}</p>"


@pytest.mark.django_db
class TestReportModel:
    @staticmethod
    def convert_date(date: dt.date) -> str:
        return dt.datetime.strftime(date, "%Y-%m-%d")

    def test_init(self, report_factory):
        report = report_factory.create()
        assert report.id is not None

    def test_str(self, report_factory):
        parent_parent_report = report_factory.create(parent_report=None)
        parent_report = report_factory.create(parent_report=parent_parent_report)
        report = report_factory.create(parent_report=parent_report)
        assert parent_parent_report.__str__() == parent_parent_report.title
        assert parent_report.__str__() == parent_report.title + f" [{parent_parent_report.title}]"
        assert report.__str__() == report.title + f" [{parent_report.title} - {parent_parent_report.title}]"

    def test_version(self, report_factory, report_version_factory):
        report = report_factory.create()
        report2 = report_factory.create()
        version_date = fake.date_object()
        version = report_version_factory.create(
            report=report, parameters={"a": "b"}, is_primary=True, version_date=version_date
        )
        version2 = report_version_factory.create(
            report=report, parameters={"a": "b"}, is_primary=False, version_date=version_date + dt.timedelta(days=1)
        )
        assert report.primary_version == version
        assert report.earliest_version == version
        assert report.last_version == version2
        assert report2.earliest_version is None
        assert report2.primary_version is None
        assert report2.last_version is None

    def test_get_gradient(self, report_factory):
        report = report_factory.create()
        palette = report.get_gradient()
        assert len(list(palette)) == len(report.color_palette.colors)

    def test_get_context(self, report_factory):
        report = report_factory.create()
        base_context = report.get_context()
        assert list(base_context.keys()) == [
            "report_title",
            "slugify_report_title",
            "report_base_color",
            "colors_palette",
            "report_logo_file_id",
        ]

    def test_set_primary_version(self, report_factory, report_version_factory):
        report = report_factory.create()
        report_version_factory.create(report=report, is_primary=True, parameters={"iteration": 0})
        assert ReportVersion.objects.filter(is_primary=True).count() == 1
        report_version_factory.create(report=report, is_primary=False, parameters={"iteration": 1})
        assert ReportVersion.objects.filter(is_primary=True, parameters={"iteration": 1}).count() == 0
        report.set_primary_versions({"iteration": 1})
        assert ReportVersion.objects.filter(is_primary=True, parameters={"iteration": 1}).count() == 1

    def test_get_or_create_version(self, report_factory):
        report = report_factory.create()
        assert ReportVersion.objects.count() == 0
        report.get_or_create_version({"iteration": 0}, update_context=True)
        assert ReportVersion.objects.count() == 1

    def test_get_next_parameters(self, report_factory, report_version_factory):
        report = report_factory.create()

        # No Report Version, no explicit parameters, therefore no next parameters.
        next_parameters = report.get_next_parameters()
        assert next_parameters is None

        # Explicit parameters.
        next_parameters = report.get_next_parameters(next_parameters={"a": "b"})
        assert next_parameters is not None

        end_date = fake.date_object()
        report_version_factory.create(report=report, parameters={"iteration": 0, "end": self.convert_date(end_date)})
        next_parameters = report.get_next_parameters()
        assert next_parameters == {"iteration": 1, "end": self.convert_date(end_date + dt.timedelta(days=1))}

    def test_generate_next_reports(self, report_factory, report_version_factory):
        end_date = fake.date_object()
        # The parent report.
        parent_report = report_factory.create(parent_report=None, is_active=True)

        # Report 1 (parent_report child) has one version.
        report1 = report_factory.create(parent_report=parent_report, is_active=True)
        report_version_factory.create(report=report1, parameters={"iteration": 0, "end": self.convert_date(end_date)})

        # Report 2 (parent_report child) has one version but the report is not active.
        report2 = report_factory.create(parent_report=parent_report, is_active=False)
        report_version_factory.create(report=report2, parameters={"iteration": 0, "end": self.convert_date(end_date)})

        # A third report (parent_report child), but no version.
        report_factory.create(parent_report=parent_report, is_active=True)

        parent_report.generate_next_reports(next_parameters=None)
        assert ReportVersion.objects.count() == 2 + 1  # report1 make a new version.

        # Same function but with "next_parameters" not None: it will make first new version for no existing versions
        # of report (Parent report + report3) and generate next report version for already existing version report.
        parent_report.generate_next_reports(
            next_parameters={"iteration": 2, "end": self.convert_date(end_date + dt.timedelta(days=2))}
        )
        assert ReportVersion.objects.count() == 3 + 3

        # Same function but for only leaves node.
        parent_report.generate_next_reports(max_depth_only=True)
        assert ReportVersion.objects.count() == 6 + 2

    def test_bulk_create(self, report_factory):
        parent_report = report_factory.create(is_active=True)
        report_factory.create_batch(5, parent_report=parent_report, is_active=True)
        end_date = fake.date_object()
        parent_report.bulk_create_child_reports(
            start_parameters={"iteration": 0, "end": self.convert_date(end_date)},
            end_parameters={"iteration": 2, "end": self.convert_date(end_date + dt.timedelta(days=2))},
        )
        assert ReportVersion.objects.count() == 5 * 3 + 3

    def test_set_primary_report_version(self, report_factory):
        parent_report = report_factory.create(parent_report=None, is_active=True)
        report_factory.create_batch(5, parent_report=parent_report, is_active=True)
        end_date = fake.date_object()
        parent_report.generate_next_reports({"iteration": 0, "end": self.convert_date(end_date)})
        parent_report.generate_next_reports()
        parent_report.set_primary_report_version(
            {"iteration": 1, "end": self.convert_date(end_date + dt.timedelta(days=1))}
        )
        parent_report.set_primary_report_version()  # will set primary to the same parameters.
        assert (
            ReportVersion.objects.filter(
                parameters={"iteration": 1, "end": self.convert_date(end_date + dt.timedelta(days=1))}, is_primary=True
            ).count()
            == 6
        )


@pytest.mark.django_db
class TestReportVersionModel:
    def test_init(self, report_version_factory):
        report_version = report_version_factory.create(parameters={"a": "b"})
        assert report_version.id is not None

    def test_generate_file(self, report_version_factory, report_factory):
        report_version = report_version_factory.create(parameters={"a": "b"})
        report_version.update_context()
        output = report_version.generate_file()
        assert output.getvalue().decode("utf_8") == report_version.title

    def test_generate_html(self, report_version_factory):
        report_version = report_version_factory.create(parameters={"a": "b"})
        report_version.update_context()
        output = report_version.generate_html()
        assert output == f"<p>{report_version.title}</p>"

    @override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
    def test_send_mail(self, report_version_factory, mail_template):
        report_version = report_version_factory.create(parameters={"a": "b"})
        report_version.send_mail(mail_template)
        assert MassMail.objects.count() == 1

    def test_get_context(self, report_version_factory):
        report_version = report_version_factory.create(parameters={"a": "b"})
        context = report_version.get_context()
        assert set(context.keys()) == {
            "uuid",
            "download_url",
            "version_title",
            "slugify_version_title",
            "title",
            "report_title",
            "slugify_report_title",
            "comment",
            "report_base_color",
            "colors_palette",
            "report_logo_file_id",
        }

    def test_update_context(self, report_version_factory):
        report_version = report_version_factory.create(parameters={"a": "b"})
        assert report_version.context == dict()
        report_version.update_context()
        assert report_version.context["title"] == report_version.title

    def test_update_context_with_error(self, report_version_factory):
        report_version = report_version_factory.create(parameters=dict())
        assert report_version.context == dict()
        assert report_version.disabled is False
        report_version.update_context()
        assert report_version.context == dict()
        assert report_version.disabled is True
