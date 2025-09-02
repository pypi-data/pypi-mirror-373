from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import IntegerPreference

report_section = Section("report")


@global_preferences_registry.register
class ReportMailTemplateIdPreference(IntegerPreference):
    section = report_section
    name = "report_mail_template_id"
    default = -1

    verbose_name = "Report Mail Template ID"
    help_text = "The Template ID used to send the report by email"
