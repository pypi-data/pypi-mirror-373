from django.apps import apps
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.color.factories import ColorGradientFactory
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbmailing.factories import MailTemplateFactory
from wbreport.factories import (
    ReportAssetFactory,
    ReportCategoryFactory,
    ReportClassFactory,
    ReportFactory,
    ReportVersionFactory,
)

register(ColorGradientFactory)
register(ReportAssetFactory)
register(ReportCategoryFactory)
register(ReportClassFactory)
register(ReportFactory)
register(ReportVersionFactory)
register(MailTemplateFactory)


pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbreport"))
