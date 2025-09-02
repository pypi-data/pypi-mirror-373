import pytest
from django.core import mail
from django.test import override_settings
from wbcore.contrib.authentication.factories import SuperUserFactory
from wbreport.tasks import generate_and_send_current_report_file


@pytest.mark.django_db
class TestTasks:
    @override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
    def test_generate_and_send_current_report_file(self, report_factory):
        parent_report = report_factory.create(is_active=True)
        report_factory.create_batch(5, is_active=True, parent_report=parent_report)
        parent_report.generate_next_reports({"iteration": 0})
        user = SuperUserFactory()
        generate_and_send_current_report_file(user.id, parent_report.id)
        assert len(mail.outbox) == 1
