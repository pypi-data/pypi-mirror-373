from wbcore import filters as wb_filters

from wbreport.models import Report, ReportVersion


class ReportFilterSet(wb_filters.FilterSet):
    is_active = wb_filters.BooleanFilter(initial=True)

    parent_report = wb_filters.ModelChoiceFilter(
        label="Parent",
        queryset=Report.objects.all(),
        endpoint=Report.get_representation_endpoint(),
        value_key=Report.get_representation_value_key(),
        label_key=Report.get_representation_label_key(),
        hidden=True,
    )
    parent_report__isnull = wb_filters.BooleanFilter(field_name="parent_report", lookup_expr="isnull", hidden=True)

    class Meta:
        model = Report
        fields = {
            "category": ["exact"],
            "permission_type": ["exact"],
            "base_color": ["exact"],
            "mailing_list": ["exact"],
        }


class ReportVersionFilterSet(wb_filters.FilterSet):
    disabled = wb_filters.BooleanFilter(method="boolean_is_disabled", initial=False)

    def boolean_is_disabled(self, queryset, name, value):
        if value is True:
            return queryset.filter(disabled=True)
        if value is False:
            return queryset.filter(disabled=False)
        return queryset

    class Meta:
        model = ReportVersion
        fields = {
            "report": ["exact"],
            "version_date": ["gte", "exact", "lte"],
            "creation_date": ["gte", "exact", "lte"],
            "update_date": ["gte", "exact", "lte"],
            "is_primary": ["exact"],
        }
