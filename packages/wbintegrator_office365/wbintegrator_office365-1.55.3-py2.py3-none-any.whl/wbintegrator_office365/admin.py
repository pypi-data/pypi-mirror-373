from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from wbcore.admin import ExportCsvMixin, ImportCsvMixin

from wbintegrator_office365.models.event import fetch_tenantusers
from wbintegrator_office365.models.subscription import (
    resubscribe_as_task,
    verification_subscriptions,
)

from .models import CallEvent, CallUser, Event, EventLog, Subscription, TenantUser


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin, ImportCsvMixin, ExportCsvMixin):
    search_fields = ("tenant_id", "display_name", "mail", "phone", "profile__computed_str", "tenant_organization_id")
    list_display = (
        "tenant_id",
        "display_name",
        "mail",
        "phone",
        "profile",
        "tenant_organization_id",
    )
    change_list_template = "admin/tenant_change_list.html"
    list_filter = ("is_internal_organization",)
    readonly_fields = ("is_internal_organization",)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("fetch_tenantusers/", self._fetch_tenantusers)]
        return my_urls + urls

    def _fetch_tenantusers(self, request):
        datum, count_added = fetch_tenantusers()
        self.message_user(
            request, str(len(datum)) + " tenants users found " + str(count_added) + " new tenants users added"
        )
        return redirect("..")


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    search_fields = ("id", "change_type", "last_event__resource", "last_event__subscription_id", "id_event")
    list_display = (
        "id",
        "order_received",
        "change_type",
        "is_handled",
        "resource",
        "created",
        "changed",
        "last_event",
        "id_event",
    )
    ordering = ["-id", "-order_received"]
    list_filter = ("change_type", "created", "changed")


class EventLogTabularInline(admin.TabularInline):
    model = EventLog
    fields = ["id", "order_received", "change_type", "is_handled", "resource", "created", "changed"]
    readonly_fields = ("id", "order_received", "change_type", "resource", "created", "changed")
    extra = 0
    autocomplete_fields = ["last_event"]
    ordering = ["-id", "-order_received"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "id_event",
        "resource",
        "subscription_id",
        "tenant_user__display_name",
        "tenant_user__mail",
        "tenant_user__phone",
        "tenant_user__profile__computed_str",
        "tenant_user__tenant_organization_id",
    )
    list_display = (
        "id",
        "auto_inc_id",
        "nb_received",
        "type",
        "change_type",
        "tenant_user",
        "is_handled",
        "created",
        "changed",
        "uuid_event",
        "id_event",
        "subscription_id",
    )
    raw_id_fields = ["tenant_user"]
    ordering = ["-auto_inc_id"]
    inlines = [EventLogTabularInline]
    list_filter = ("type", "change_type", "created", "changed")


@admin.register(CallEvent)
class CallEventAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "event__id",
        "organizer__tenant_user__display_name",
        "organizer__tenant_user__mail",
        "organizer__tenant_user__phone",
        "organizer__tenant_user__profile__computed_str",
        "organizer__tenant_user__tenant_organization_id",
    )
    list_display = (
        "id",
        "event",
        "organizer",
        "version",
        "start",
        "end",
        "created",
        "last_modified",
        "is_internal_call",
    )
    list_filter = ("is_internal_call", "created", "last_modified", "start", "end")


@admin.register(CallUser)
class CallUserAdmin(admin.ModelAdmin):
    search_fields = (
        "tenant_user__display_name",
        "tenant_user__mail",
        "tenant_user__phone",
        "tenant_user__profile__computed_str",
        "tenant_user__tenant_organization_id",
    )
    list_display = ("id", "tenant_user", "is_guest", "is_phone")
    list_filter = ("is_guest", "is_phone")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "subscription_id",
        "resource",
        "tenant_user__display_name",
        "tenant_user__mail",
        "tenant_user__phone",
        "tenant_user__profile__computed_str",
        "tenant_user__tenant_organization_id",
    )
    list_display = (
        "id",
        "subscription_id",
        "expiration_date",
        "type_resource",
        "tenant_user",
        "is_enable",
        "created",
        "change_type",
        "resource",
        "notification_url",
    )
    list_filter = ("is_enable", "type_resource", "expiration_date", "created")

    def disable_selected_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.is_enable = False
            subscription.save()

        self.message_user(
            request,
            "Operation completed, we unsubscribe the subscriptions selected",
        )

    def verification_selected_subscriptions(self, request, queryset):
        for subscription in queryset:
            verification_subscriptions.delay(subscription.id)
            self.message_user(
                request,
                "Verification completed for the subscriptions selected",
            )

    def renew_selected_subscriptions(self, request, queryset):
        for subscription in queryset:
            resubscribe_as_task.delay(subscription.id)
            self.message_user(request, "Active subscriptions are renewed on microsoft")
        return redirect("..")

    actions = [disable_selected_subscriptions, verification_selected_subscriptions, renew_selected_subscriptions]

    readonly_fields = [
        "subscription_id",
        "change_type",
        "expiration_date",
        "notification_url",
        "resource",
        "application_id",
        "creator_id",
        "client_state",
        "latest_supported_tls_version",
        "notification_content_type",
        "odata_context",
        "encryption_certificate_id",
        "encryption_certificate",
        "include_resource_data",
        "notification_query_options",
        "is_enable",
    ]
