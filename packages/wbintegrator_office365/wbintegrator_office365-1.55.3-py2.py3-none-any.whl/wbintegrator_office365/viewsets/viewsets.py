import json
import logging
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from django.db import transaction
from django.db.models import Case, CharField, F, When
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from plotly.subplots import make_subplots
from rest_framework import filters
from wbcore import viewsets
from wbcore.filters import DjangoFilterBackend
from wbhuman_resources.models import EmployeeHumanResource

from wbintegrator_office365.filters import (
    CallEventFilter,
    CallEventSummaryGraphFilter,
    CallUserFilter,
    EventFilter,
    EventLogFilter,
    SubscriptionFilter,
    TenantUserFilter,
)
from wbintegrator_office365.importer import parse
from wbintegrator_office365.models import (
    CallEvent,
    CallUser,
    Event,
    EventLog,
    Subscription,
    TenantUser,
)
from wbintegrator_office365.models.event import handle_event_from_webhook
from wbintegrator_office365.serializers import (
    CallEventModelSerializer,
    CallEventRepresentationSerializer,
    CallUserModelSerializer,
    CallUserRepresentationSerializer,
    EventLogModelSerializer,
    EventLogRepresentationSerializer,
    EventModelSerializer,
    EventRepresentationSerializer,
    SubscriptionListModelSerializer,
    SubscriptionModelSerializer,
    SubscriptionRepresentationSerializer,
    TenantUserModelSerializer,
    TenantUserRepresentationSerializer,
)

from .display import (
    CallEventDisplayConfig,
    CallUserDisplayConfig,
    EventDisplayConfig,
    EventLogDisplayConfig,
    EventLogEventDisplayConfig,
    SubscriptionDisplayConfig,
    TenantUserDisplayConfig,
)
from .endpoints import (
    CallEventEndpointConfig,
    CallUserEndpointConfig,
    EventEndpointConfig,
    EventLogEndpointConfig,
    EventLogEventEndpointConfig,
    SubscriptionEndpointConfig,
    TenantUserEndpointConfig,
)
from .titles import (
    CallEventReceptionTimeTitleConfig,
    CallEventSummaryGraphTitleConfig,
    CallEventTitleConfig,
    CallUserTitleConfig,
    SubscriptionTitleConfig,
    TenantUserTitleConfig,
)

logger = logging.getLogger("wbintegrator_office365")


class TenantUserRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbintegrator_office365:tenantuserrepresentation"
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = [
        "profile__computed_str",
        "display_name",
        "mail",
        "phone",
    ]
    serializer_class = TenantUserRepresentationSerializer
    queryset = TenantUser.objects.all()


class SubscriptionRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbintegrator_office365:subscriptionrepresentation"
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering = ["-created"]
    search_fields = ["subscription_id"]
    serializer_class = SubscriptionRepresentationSerializer
    queryset = Subscription.objects.all()


class EventRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbintegrator_office365:eventrepresentation"
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering = ["-auto_inc_id"]
    search_fields = ["id"]
    serializer_class = EventRepresentationSerializer
    queryset = Event.objects.all()


class CallUserRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbintegrator_office365:calleventrepresentation"

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = [
        "tenant_user__tenant_id",
        "tenant_user__profile__computed_str",
        "tenant_user__display_name",
        "tenant_user__mail",
        "tenant_user__phone",
    ]

    serializer_class = CallUserRepresentationSerializer
    queryset = CallUser.objects.all()


class CallEventRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbintegrator_office365:calleventrepresentation"
    serializer_class = CallEventRepresentationSerializer
    queryset = CallEvent.objects.all()


class TenantUserViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbintegrator_office365:tenantuser"
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering_fields = [
        "id",
        "tenant_id",
        "profile",
        "display_name",
        "mail",
        "phone",
        "tenant_organization_id",
        "is_internal_organization",
    ]
    ordering = ["id"]
    search_fields = [
        "profile__computed_str",
        "display_name",
        "mail",
        "phone",
    ]

    filterset_class = TenantUserFilter

    display_config_class = TenantUserDisplayConfig
    title_config_class = TenantUserTitleConfig
    endpoint_config_class = TenantUserEndpointConfig

    serializer_class = TenantUserModelSerializer
    queryset = TenantUser.objects.all()


class SubscriptionViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbintegrator_office365:subscription"
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering_fields = [
        "subscription_id",
        "change_type",
        "expiration_date",
        "type_resource",
        "is_enable",
        "tenant_user",
        "created",
    ]
    ordering = ["-created"]
    search_fields = [
        "subscription_id",
        "tenant_user__profile__computed_str",
        "tenant_user__display_name",
        "tenant_user__mail",
        "tenant_user__phone",
    ]
    title_config_class = SubscriptionTitleConfig
    display_config_class = SubscriptionDisplayConfig
    endpoint_config_class = SubscriptionEndpointConfig

    filterset_class = SubscriptionFilter

    serializer_class = SubscriptionModelSerializer
    queryset = Subscription.objects.all()

    def get_serializer_class(self):
        if self.get_action() in ["list", "list-metadata"]:
            return SubscriptionListModelSerializer
        return super().get_serializer_class()


class CallUserViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbintegrator_office365:calluser"
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering_fields = ["is_guest", "is_phone", "tenant_user"]
    ordering = ["id"]
    search_fields = [
        "tenant_user__profile__computed_str",
        "tenant_user__display_name",
        "tenant_user__mail",
        "tenant_user__phone",
    ]

    display_config_class = CallUserDisplayConfig
    title_config_class = CallUserTitleConfig
    endpoint_config_class = CallUserEndpointConfig

    filterset_class = CallUserFilter

    serializer_class = CallUserModelSerializer
    queryset = CallUser.objects.all()

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .annotate(
                name_user=Case(
                    When(tenant_user__profile__isnull=True, then=F("tenant_user__display_name")),
                    default=F("tenant_user__profile__computed_str"),
                    output_field=CharField(),
                ),
                phone=F("tenant_user__phone"),
                mail=F("tenant_user__mail"),
            )
        )
        return qs


class EventViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbintegrator_office365:event"
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = [
        "auto_inc_id",
        "nb_received",
        "id",
        "type",
        "change_type",
        "tenant_user",
        "created",
        "changed",
        "subscription_id",
        "id_event",
        "is_handled",
    ]

    ordering = ["-changed", "-created"]

    filterset_class = EventFilter

    display_config_class = EventDisplayConfig
    endpoint_config_class = EventEndpointConfig

    serializer_class = EventModelSerializer

    queryset = Event.objects.all()


class EventLogRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = EventLogRepresentationSerializer
    queryset = EventLog.objects.all()


class EventLogViewSet(viewsets.ModelViewSet):
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    endpoint_config_class = EventLogEndpointConfig
    display_config_class = EventLogDisplayConfig
    serializer_class = EventLogModelSerializer
    filterset_class = EventLogFilter
    ordering_fields = ["id", "order_received", "last_event", "change_type", "created", "changed", "id_event"]
    ordering = ["-changed", "-created"]

    queryset = EventLog.objects.all()


class EventLogEventViewSet(EventLogViewSet):
    endpoint_config_class = EventLogEventEndpointConfig
    display_config_class = EventLogEventDisplayConfig

    def get_queryset(self):
        return super().get_queryset().filter(last_event=self.kwargs["last_event_id"])


class CallEventViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbintegrator_office365:callevent"
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ["event", "organizer", "created", "start", "end", "change_type", "is_internal_call"]
    ordering = ["-created"]

    filterset_class = CallEventFilter

    display_config_class = CallEventDisplayConfig
    title_config_class = CallEventTitleConfig
    endpoint_config_class = CallEventEndpointConfig

    serializer_class = CallEventModelSerializer
    queryset = CallEvent.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(change_type=F("event__change_type"))


class CallEventReceptionTime(viewsets.ChartViewSet):
    IDENTIFIER = "wbintegrator_office365:calleventchart"
    queryset = CallEvent.objects.all()
    title_config_class = CallEventReceptionTimeTitleConfig

    def get_plotly(self, queryset):
        fig = go.Figure()
        if queryset.exists():
            df = pd.DataFrame(queryset.values("start", "end", "created"))
            df["delay"] = np.where(df["created"] > df["end"], df["created"] - df["end"], df["created"] - df["start"])
            df["minutes"] = df.delay.dt.seconds / 60
            df = df.loc[df["minutes"] < 1000]
            # print(df.loc[100, ["delay", "minutes"]])
            df["mean_minutes"] = df.minutes.mean()
            df["median_minutes"] = df.minutes.median()
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df.minutes,
                    mode="lines+markers",
                    name="Delay",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df.mean_minutes,
                    mode="lines",
                    name="Average",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df.median_minutes,
                    mode="lines",
                    name="Median",
                )
            )

            fig.update_layout(
                title="<b>Call reception delay</b>",
                xaxis=dict(
                    title="Calls",
                ),
                yaxis=dict(
                    title="Delay in minutes",
                    # type= 'date'
                ),
                autosize=True,
                xaxis_rangeslider_visible=True,
                height=850,
            )

        return fig


class CallEventSummaryGraph(viewsets.ChartViewSet):
    filter_backends = (DjangoFilterBackend,)
    IDENTIFIER = "wbintegrator_office365:calleventsummarygraph"
    queryset = CallEvent.objects.all()
    title_config_class = CallEventSummaryGraphTitleConfig
    filterset_class = CallEventSummaryGraphFilter

    def get_queryset(self):
        return super().get_queryset().annotate(duration_seconds=F("end") - F("start"))

    def get_dataframe_business_days(self, start_date, end_date):
        temp_date = start_date
        list_date = []
        while temp_date <= end_date:
            if temp_date.weekday() <= 4:
                list_date.append(temp_date)
            temp_date += timedelta(days=1)
        return pd.DataFrame(list_date, columns=["day"])

    def merge_df_with_business_days(self, df):
        start_date = self.request.GET.get("start", None)
        end_date = self.request.GET.get("end", None)
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date and start_date != "null" else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date and end_date != "null" else date.today()
        end_date = end_date if end_date <= date.today() else date.today()

        if start_date and end_date:
            df_day = self.get_dataframe_business_days(start_date, end_date)
            df_day.columns = pd.MultiIndex.from_product([df_day.columns, [""]])
            df = df.merge(df_day, on=["day"], how="outer")
            df[["count", "sum", "mean", "median"]] = df[["count", "sum", "mean", "median"]].fillna(0)
            df["average_count_period"] = df["count"]["minutes"].mean()
            df["average_sum_period"] = df["sum"]["minutes"].mean()
            df["average_mean_period"] = df["mean"]["minutes"].mean()
            df["average_median_period"] = df["median"]["minutes"].mean()
            df = df.sort_values(by=["day"]).reset_index()
        return df

    def get_plotly(self, queryset):
        fig = go.Figure()
        if queryset.exists():
            df = pd.DataFrame(queryset.annotate(day=F("created__date")).values("start", "end", "day"))
            dict_df = {"employee": df}
            df_compare_employee = pd.DataFrame()
            if compare_employee_id := self.request.GET.get("compare_employee", None):
                compare_employee = EmployeeHumanResource.objects.get(id=compare_employee_id)

                qs2 = CallEvent.objects.filter(
                    participants__tenant_user__profile__computed_str__icontains=compare_employee.profile.computed_str
                )
                if start_compare := self.request.GET.get("start", None):
                    qs2 = qs2.filter(start__gte=start_compare)

                if end_compare := self.request.GET.get("end", None):
                    qs2 = qs2.filter(end__lte=end_compare)
                if call_duration := self.request.GET.get("call_duration", None):
                    qs2 = qs2.annotate(duration_seconds=F("end") - F("start")).filter(
                        duration_seconds__gte=timedelta(seconds=float(call_duration))
                    )
                if call_type := self.request.GET.get("call_type", None):
                    qs2 = qs2.filter(type=call_type)
                if call_area := self.request.GET.get("call_area", None):
                    qs2 = qs2.filter(is_internal_call=call_area)
                df_compare_employee = pd.DataFrame(qs2.annotate(day=F("created__date")).values("start", "end", "day"))
                if not df_compare_employee.empty:
                    dict_df["compare_employee"] = df_compare_employee

            for key, df in dict_df.items():
                df["duration"] = df["end"] - df["start"]
                df["minutes"] = df.duration.dt.seconds / 60
                df = df.pivot_table(index=["day"], values="minutes", aggfunc=["count", "sum", "mean", "median"])
                df["average_count_period"] = df["count"]["minutes"].mean()
                df["average_sum_period"] = df["sum"]["minutes"].mean()
                df["average_mean_period"] = df["mean"]["minutes"].mean()
                df["average_median_period"] = df["median"]["minutes"].mean()

                df[
                    [
                        "sum",
                        "mean",
                        "median",
                        "average_count_period",
                        "average_sum_period",
                        "average_mean_period",
                        "average_median_period",
                    ]
                ] = df[
                    [
                        "sum",
                        "mean",
                        "median",
                        "average_count_period",
                        "average_sum_period",
                        "average_mean_period",
                        "average_median_period",
                    ]
                ].round(2)
                df = df.reset_index()

                dict_df[key] = df

            df = dict_df["employee"]
            if compare_employee_id and not df_compare_employee.empty:
                df2 = dict_df["compare_employee"]

            if (business_day_without_call := self.request.GET.get("business_day_without_call", None)) and (
                business_day_without_call == "true"
            ):
                df = self.merge_df_with_business_days(df)
                if compare_employee_id and not df_compare_employee.empty:
                    df2 = self.merge_df_with_business_days(df2)

                # df = df.merge(df2[['day']], on=['day'], how = 'outer', indicator=True)
                # df[['count', 'sum', 'mean', 'median']] = df[['count', 'sum', 'mean', 'median']].fillna(0)
                # df[["average_count_period", "average_sum_period", "average_mean_period", "average_median_period"]] = df[["average_count_period", "average_sum_period", "average_mean_period", "average_median_period"]].fillna(0)
                # df = df.sort_values(by=['day']).reset_index()

                # df2 = df2.merge(df[['day']], on=['day'], how = 'outer', indicator=True)
                # df2[['count', 'sum', 'mean', 'median']] = df2[['count', 'sum', 'mean', 'median']].fillna(0)
                # df2[["average_count_period", "average_sum_period", "average_mean_period", "average_median_period"]] = df2[["average_count_period", "average_sum_period", "average_mean_period", "average_median_period"]].fillna(0)
                # df2 = df2.sort_values(by=['day']).reset_index()

            fig = make_subplots(
                rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.2, 0.3, 0.25, 0.25]
            )

            fig.add_trace(
                go.Bar(
                    x=df["day"],
                    y=df["count"]["minutes"],
                    name="Number of calls",
                    text=df["count"]["minutes"],
                    textposition="auto",
                ),
                row=1,
                col=1,
            )
            if compare_employee_id and not df_compare_employee.empty:
                # df2 = dict_df["compare_employee"]
                fig.add_trace(
                    go.Bar(
                        x=df["day"],
                        y=df2["count"]["minutes"],
                        name="Number of calls " + compare_employee.computed_str,
                        text=df2["count"]["minutes"],
                        textposition="auto",
                        marker=dict(color="#A9A9A9"),
                    ),
                    row=1,
                    col=1,
                )

            fig.add_trace(
                go.Scatter(
                    x=df["day"],
                    y=df["average_count_period"],
                    mode="lines",
                    line=dict(dash="dash", width=2),
                    name="Average number of calls for the period",
                    opacity=0.5,
                    marker=dict(color="red"),
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Bar(
                    x=df["day"],
                    y=df["sum"]["minutes"],
                    name="Total minutes",
                    text=df["sum"]["minutes"],
                    textposition="auto",
                    marker=dict(color="rgb(55, 83, 109)"),
                ),
                row=2,
                col=1,
            )
            if compare_employee_id and not df_compare_employee.empty:
                fig.add_trace(
                    go.Bar(
                        x=df2["day"],
                        y=df2["sum"]["minutes"],
                        name="Total minutes " + compare_employee.computed_str,
                        text=df2["sum"]["minutes"],
                        textposition="auto",
                        marker=dict(color="#696969"),
                    ),
                    row=2,
                    col=1,
                )

            fig.add_trace(
                go.Scatter(
                    x=df["day"],
                    y=df["average_sum_period"],
                    mode="lines",
                    line=dict(dash="dashdot", width=2),
                    name="Average Total minutes for the period",
                    opacity=0.5,
                    marker=dict(color="#FFD700"),
                ),
                row=2,
                col=1,
            )

            fig.add_trace(
                go.Bar(
                    x=df["day"],
                    y=df["median"]["minutes"],
                    name="Median minutes",
                    text=df["median"]["minutes"],
                    textposition="auto",
                    marker=dict(color="skyblue"),
                ),
                row=3,
                col=1,
            )
            if compare_employee_id and not df_compare_employee.empty:
                fig.add_trace(
                    go.Bar(
                        x=df2["day"],
                        y=df2["median"]["minutes"],
                        name="Median minutes " + compare_employee.computed_str,
                        text=df2["median"]["minutes"],
                        textposition="auto",
                        marker=dict(color="#D3D3D3"),
                    ),
                    row=3,
                    col=1,
                )

            fig.add_trace(
                go.Scatter(
                    x=df["day"],
                    y=df["average_median_period"],
                    mode="lines",
                    line=dict(dash="dash", width=2),
                    name="Median minutes for the period",
                    opacity=0.5,
                    marker=dict(color="orange"),
                ),
                row=3,
                col=1,
            )

            fig.add_trace(
                go.Bar(
                    x=df["day"],
                    y=df["mean"]["minutes"],
                    name="Average minutes",
                    text=df["mean"]["minutes"],
                    textposition="auto",
                    marker=dict(color="blue"),
                ),
                row=4,
                col=1,
            )
            if compare_employee_id and not df_compare_employee.empty:
                fig.add_trace(
                    go.Bar(
                        x=df2["day"],
                        y=df2["mean"]["minutes"],
                        name="Average minutes " + compare_employee.computed_str,
                        text=df2["mean"]["minutes"],
                        textposition="auto",
                        marker=dict(color="#808080"),
                    ),
                    row=4,
                    col=1,
                )

            fig.add_trace(
                go.Scatter(
                    x=df["day"],
                    y=df["average_mean_period"],
                    mode="lines",
                    line=dict(dash="dash", width=2),
                    name="Average minutes for the period",
                    opacity=0.5,
                    marker=dict(color="#BDB76B"),
                ),
                row=4,
                col=1,
            )

            # Update xaxis properties
            fig.update_xaxes(type="category", row=1, col=1, gridcolor="white")
            fig.update_xaxes(type="category", row=2, col=1, gridcolor="white")
            fig.update_xaxes(type="category", row=3, col=1, gridcolor="white")
            fig.update_xaxes(
                title_text="days", type="category", row=4, col=1, rangeslider_visible=True, gridcolor="white"
            )
            # Update yaxis properties
            fig.update_yaxes(title_text="Number of calls", title_font_size=12, row=1, col=1)
            fig.update_yaxes(title_text="Total minutes", title_font_size=12, row=2, col=1)
            fig.update_yaxes(title_text="Median Minutes", row=3, title_font_size=12, col=1)
            fig.update_yaxes(title_text="Average Minutes", row=4, title_font_size=12, col=1)

            fig.update_layout(
                title="<b>Call Summary Graph</b>",
                autosize=True,
                height=800,
                hovermode="x",
            )

        return fig


def callback_consent_permission(request):
    result = request.GET.get("admin_consent")
    return HttpResponse(result, content_type="text/plain")


# @require_POST
@csrf_exempt
def listen(request):
    # handle validation
    if request.GET.get("validationToken"):
        token = request.GET.get("validationToken")
        return HttpResponse(token, content_type="text/plain")

    # handle notifications
    # Latency for delivery of the change notification callRecord Less than 15 minutes Maximum latency	60 minutes
    notifications = None
    if request.body:
        # logger.warning(f"{timezone.now():%Y-%m-%d %H:%M:%S.%f} {request.body}")
        json_body = json.loads(request.body)
        if json_body.get("value"):
            notifications = parse(json_body.get("value"))
            for notification in notifications:
                # print(colored(f"{timezone.now():%Y-%m-%d %H:%M:%S.%f} {notification}", 'blue'))
                if (resource_data := notification.get("resource_data")) and (id_event := resource_data.get("id")):
                    transaction.on_commit(lambda: handle_event_from_webhook.delay(id_event, notification))
    return HttpResponse(notifications, content_type="text/plain")
