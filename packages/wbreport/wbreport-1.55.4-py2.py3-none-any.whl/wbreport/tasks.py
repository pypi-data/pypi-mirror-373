import zipfile
from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from slugify import slugify
from wbcore.contrib.authentication.models import User
from wbcore.utils.html import convert_html2text

from wbreport.models import Report, ReportVersion


@shared_task()
def generate_and_send_current_report_file(user_id, parent_report_id, parameters=None):
    zip_buffer = BytesIO()
    parent_report = Report.objects.get(id=parent_report_id)
    if not parameters:
        parameters = parent_report.last_version.parameters
    report_date = parent_report.report_class.get_version_date(parameters)
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        summary = ""
        for version in ReportVersion.objects.filter(
            parameters=parameters,
            report__parent_report=parent_report,
            report__is_active=True,
            report__file_disabled=False,
            disabled=False,
        ):
            basename = f"report_{slugify(version.title)}"
            try:
                output = version.generate_file()
                zip_file.writestr(output.name, output.getvalue())
                msg = f"VALID: Report {basename} generated with success"
            except Exception as e:
                msg = f"ERROR: Could not generate Report {basename} (error: {e})"
            print(msg)  # noqa: T201
            summary += f"{msg}\n"

        zip_file.writestr("summary.txt", summary)

    html = get_template("notifications/email_template.html")
    notification = {
        "message": f"Please find all the reports you requested for {parent_report.title}",
        "title": "Your Report bundle",
    }
    html_content = html.render({"notification": notification})

    msg = EmailMultiAlternatives(
        "Your Report bundle",
        body=convert_html2text(html_content),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[User.objects.get(id=user_id).email],
    )
    msg.attach_alternative(html_content, "text/html")

    zip_buffer.seek(0)

    msg.attach(f"reports_bundle_{report_date}.zip", zip_buffer.read(), "application/zip")
    msg.send()
