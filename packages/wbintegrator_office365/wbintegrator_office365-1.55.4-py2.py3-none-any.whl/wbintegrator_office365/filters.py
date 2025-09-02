from datetime import date, timedelta

from psycopg.types.range import DateRange
from wbcore import filters as wb_filters
from wbhuman_resources.models import EmployeeHumanResource

from wbintegrator_office365.models import (
    CallEvent,
    CallUser,
    Event,
    EventLog,
    Subscription,
    TenantUser,
)


class TenantUserFilter(wb_filters.FilterSet):
    class Meta:
        model = TenantUser
        fields = {
            "profile": ["exact"],
            "display_name": ["exact", "icontains"],
            "mail": ["exact", "icontains"],
            "phone": ["exact", "icontains"],
            "tenant_id": ["exact", "icontains"],
            "tenant_organization_id": ["exact", "icontains"],
            "is_internal_organization": ["exact"],
        }


class SubscriptionFilter(wb_filters.FilterSet):
    class Meta:
        model = Subscription
        fields = {
            "change_type": ["exact", "icontains"],
            "subscription_id": ["exact", "icontains"],
            "expiration_date": ["lte", "gte"],
            "type_resource": ["exact"],
            "tenant_user": ["exact"],
            "is_enable": ["exact"],
            "created": ["lte", "gte"],
        }


def current_year(field, request, view):
    today = date.today()
    return date(today.year, 1, 1)


class EventFilter(wb_filters.FilterSet):
    created__gte = wb_filters.DateFilter(
        label="Created",
        lookup_expr="gte",
        field_name="created",
        method="created_filter",
        initial=current_year,
    )

    def created_filter(self, queryset, name, value):
        if value:
            return queryset.filter(created__gte=value)
        return queryset

    class Meta:
        model = Event
        fields = {
            "id": ["exact"],
            "nb_received": ["exact"],
            "type": ["exact"],
            "change_type": ["exact"],
            "created": ["gte", "lte"],
            "changed": ["gte", "lte"],
            "tenant_user": ["exact"],
            "subscription_id": ["icontains", "exact"],
            "id_event": ["icontains", "exact"],
            "is_handled": ["exact"],
        }


class EventLogFilter(wb_filters.FilterSet):
    class Meta:
        model = EventLog
        fields = {
            "id": ["exact"],
            "order_received": ["exact"],
            "last_event": ["exact"],
            "change_type": ["exact"],
            "id_event": ["icontains", "exact"],
            "created": ["gte", "lte"],
            "changed": ["gte", "lte"],
        }


class CallEventFilter(wb_filters.FilterSet):
    change_type = wb_filters.CharFilter(label="Type", lookup_expr="icontains")
    participants = wb_filters.ModelMultipleChoiceFilter(
        label="Participants",
        queryset=CallUser.objects.all(),
        endpoint=CallUser.get_representation_endpoint(),
        value_key=CallUser.get_representation_value_key(),
        label_key=CallUser.get_representation_label_key(),
        method="filter_participants",
    )
    start__gte = wb_filters.DateFilter(
        label="Start",
        lookup_expr="gte",
        field_name="start",
        method="start_filter",
        initial=current_year,
    )

    def filter_participants(self, queryset, name, value):
        if value:
            return queryset.filter(participants__in=value)
        return queryset

    def start_filter(self, queryset, name, value):
        if value:
            return queryset.filter(start__gte=value)
        return queryset

    class Meta:
        model = CallEvent
        fields = {
            "event": ["exact"],
            "organizer": ["exact"],
            "start": ["gte", "exact", "lte"],
            "end": ["gte", "exact", "lte"],
            "created": ["gte", "exact", "lte"],
            "is_internal_call": ["exact"],
        }


class CallUserFilter(wb_filters.FilterSet):
    name_user = wb_filters.CharFilter(label="Question", lookup_expr="icontains")
    phone = wb_filters.CharFilter(label="Question", lookup_expr="icontains")
    mail = wb_filters.CharFilter(label="Question", lookup_expr="icontains")

    class Meta:
        model = CallUser
        fields = {
            "tenant_user": ["exact"],
            "is_phone": ["exact"],
            "is_guest": ["exact"],
        }


def previous_month(*args, **kwargs):
    return date.today() - timedelta(days=30)


def next_day(*args, **kwargs):
    return date.today() + timedelta(days=1)


class CallEventSummaryGraphFilter(wb_filters.FilterSet):
    date_range = wb_filters.DateTimeRangeFilter(
        method="filter_date_range",
        label="Date Range",
        required=True,
        clearable=False,
        initial=lambda f, v, q: DateRange(previous_month(f, v, q), next_day(f, v, q)),
    )

    employee = wb_filters.ModelChoiceFilter(
        label="Employee",
        queryset=EmployeeHumanResource.objects.all(),
        endpoint=EmployeeHumanResource.get_representation_endpoint(),
        value_key=EmployeeHumanResource.get_representation_value_key(),
        label_key=EmployeeHumanResource.get_representation_label_key(),
        method="filter_employee",
    )

    call_type = wb_filters.ChoiceFilter(
        label="Type of call",
        choices=[("groupCall", "Group Call"), ("peerToPeer", "Peer To Peer")],
        method="filter_call_type",
    )

    call_area = wb_filters.ChoiceFilter(
        label="Call area",
        choices=[("True", "Internal Call"), ("False", "External Call")],
        method="filter_call_area",
    )

    compare_employee = wb_filters.ModelChoiceFilter(
        label="Compare to an employee",
        queryset=EmployeeHumanResource.objects.all(),
        endpoint=EmployeeHumanResource.get_representation_endpoint(),
        value_key=EmployeeHumanResource.get_representation_value_key(),
        label_key=EmployeeHumanResource.get_representation_label_key(),
        method="filter_compare_employee",
    )

    call_duration = wb_filters.NumberFilter(
        label="Include calls of at least how many secondes", initial=30, method="filter_call_duration", required=False
    )

    business_day_without_call = wb_filters.BooleanFilter(
        label="Include business day without call", initial=False, method="filter_business_day_without_call"
    )

    def filter_date_range(self, queryset, name, value):
        if value:
            return queryset.filter(start__gte=value.lower, end__lte=value.upper)
        return queryset

    def filter_employee(self, queryset, name, value):
        if value:
            return queryset.filter(
                participants__tenant_user__profile__computed_str__icontains=value.profile.computed_str
            )
        return queryset

    def filter_call_duration(self, queryset, name, value):
        if value:
            return queryset.filter(duration_seconds__gte=timedelta(seconds=float(value)))
        return queryset

    def filter_call_type(self, queryset, name, value):
        if value:
            return queryset.filter(type=value)
        return queryset

    def filter_call_area(self, queryset, name, value):
        if value is not None:
            return queryset.filter(is_internal_call=value)
        return queryset

    def filter_compare_employee(self, queryset, name, value):
        return queryset

    def filter_business_day_without_call(self, queryset, name, value):
        return queryset

    class Meta:
        model = CallEvent
        fields = {}
