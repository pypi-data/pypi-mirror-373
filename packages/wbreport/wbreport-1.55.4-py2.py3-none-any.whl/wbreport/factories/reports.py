from io import BytesIO

import factory
from PIL import Image
from wbcore.contrib.color.factories import ColorGradientFactory

from wbreport.models import (
    Report,
    ReportAsset,
    ReportCategory,
    ReportClass,
    ReportVersion,
)


def create_test_image():
    file = BytesIO()
    image = Image.new("RGBA", size=(50, 50), color=(155, 0, 0))
    image.save(file, "png")
    file.name = "test.png"
    file.seek(0)
    return file


class ReportAssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportAsset

    key = factory.Sequence(lambda n: f"Report Asset {n}")
    description = factory.Faker("paragraph")
    text = factory.Faker("paragraph")
    asset = factory.django.ImageField()


class ReportCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportCategory

    title = factory.Sequence(lambda n: f"Report Category {n}")


class ReportClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportClass

    title = factory.Sequence(lambda n: f"Report Class {n}")
    class_path = "wbreport.factories.data_classes"


class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Report

    category = factory.SubFactory(ReportCategoryFactory)
    report_class = factory.SubFactory(ReportClassFactory)
    is_active = factory.Faker("boolean")
    base_color = factory.Faker("color")
    title = factory.Sequence(lambda n: f"Report {n}")
    logo_file = factory.django.ImageField()
    color_palette = factory.SubFactory(ColorGradientFactory)
    mailing_list = factory.SubFactory("wbmailing.factories.MailingListFactory")
    parent_report = factory.SubFactory("wbreport.factories.ParentReportFactory")


class ParentReportFactory(ReportFactory):
    parent_report = None
    key = factory.Sequence(lambda n: f"key-{n}")


class ReportVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportVersion

    title = factory.Sequence(lambda n: f"Report Version {n}")
    lookup = factory.Sequence(lambda n: f"lookup-{n}")
    is_primary = True
    disabled = False
    report = factory.SubFactory(ReportFactory)
    comment = factory.Faker("paragraph")
    parameters = factory.Sequence(lambda n: {"type": f"type{n}"})
