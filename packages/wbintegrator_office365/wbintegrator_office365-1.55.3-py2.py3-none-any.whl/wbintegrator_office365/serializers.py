from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbintegrator_office365.models import (
    CallEvent,
    CallUser,
    Event,
    EventLog,
    Subscription,
    TenantUser,
)


class TenantUserRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbintegrator_office365:tenantuser-detail")
    profile_str = wb_serializers.StringRelatedField(source="profile")
    id_str = wb_serializers.CharField(source="id")

    class Meta:
        model = TenantUser
        fields = ("id", "tenant_id", "profile_str", "id_str", "_detail")


class SubscriptionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbintegrator_office365:subscription-detail")

    class Meta:
        model = Subscription
        fields = ("id", "subscription_id", "created", "_detail")


class EventRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbintegrator_office365:event-detail")
    id_str = wb_serializers.CharField(source="id")

    class Meta:
        model = Event
        fields = ("id", "id_str", "uuid_event", "_detail")


class CallUserRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbintegrator_office365:calluser-detail")
    tenant_user_str = wb_serializers.StringRelatedField(source="tenant_user")
    id_str = wb_serializers.CharField(source="id")

    class Meta:
        model = CallUser
        fields = ("id", "tenant_user_str", "id_str", "_detail")


class CallEventRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbintegrator_office365:callevent-detail")

    class Meta:
        model = CallEvent
        fields = ("id", "_detail")


class TenantUserModelSerializer(wb_serializers.ModelSerializer):
    _profile = PersonRepresentationSerializer(source="profile")

    class Meta:
        model = TenantUser
        fields = (
            "id",
            "tenant_id",
            "display_name",
            "mail",
            "phone",
            "profile",
            "_profile",
            "tenant_organization_id",
            "is_internal_organization",
        )


class CallUserModelSerializer(wb_serializers.ModelSerializer):
    _tenant_user = TenantUserRepresentationSerializer(source="tenant_user")

    name_user = wb_serializers.CharField(read_only=True)
    phone = wb_serializers.CharField(read_only=True)
    mail = wb_serializers.CharField(read_only=True)

    class Meta:
        model = CallUser
        fields = read_only_fields = (
            "id",
            "tenant_user",
            "_tenant_user",
            "is_guest",
            "is_phone",
            "acs_user",
            "splool_user",
            "encrypted",
            "on_premises",
            "acs_application_instance",
            "spool_application_instance",
            "application_instance",
            "application",
            "device",
            "name_user",
            "phone",
            "mail",
        )


class SubscriptionModelSerializer(wb_serializers.ModelSerializer):
    _tenant_user = TenantUserRepresentationSerializer(source="tenant_user")
    id_str = wb_serializers.CharField(source="id")

    class Meta:
        model = Subscription
        fields = read_only_fields = (
            "id",
            "id_str",
            "subscription_id",
            "change_type",
            "notification_url",
            "resource",
            "expiration_date",
            "application_id",
            "creator_id",
            "client_state",
            "created",
            "latest_supported_tls_version",
            "notification_content_type",
            "odata_context",
            "encryption_certificate_id",
            "encryption_certificate",
            "include_resource_data",
            "notification_query_options",
            "tenant_user",
            "_tenant_user",
            "is_enable",
            "type_resource",
        )
        read_only_fields = (
            "id",
            "subscription_id",
            "change_type",
            "notification_url",
            "resource",
            "expiration_date",
            "application_id",
            "creator_id",
            "client_state",
            "created",
            "latest_supported_tls_version",
            "notification_content_type",
            "odata_context",
            "encryption_certificate_id",
            "encryption_certificate",
            "include_resource_data",
            "notification_query_options",
            "tenant_user",
            "is_enable",
            "type_resource",
        )


class SubscriptionListModelSerializer(SubscriptionModelSerializer):
    class Meta:
        model = Subscription
        fields = read_only_fields = (
            "id",
            "subscription_id",
            "change_type",
            "expiration_date",
            "type_resource",
            "resource",
            "tenant_user",
            "_tenant_user",
            "is_enable",
            "created",
        )


class EventModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        resources = {
            "eventlog": reverse("wbintegrator_office365:event-eventlog-list", args=[instance.id], request=request),
        }
        return resources

    id = wb_serializers.PrimaryKeyCharField()
    id_str = wb_serializers.CharField(source="id")

    _tenant_user = TenantUserRepresentationSerializer(source="tenant_user")

    class Meta:
        model = Event
        fields = read_only_fields = (
            "id",
            "id_str",
            "auto_inc_id",
            "nb_received",
            "type",
            "subscription_id",
            "change_type",
            "resource",
            "created",
            "changed",
            "tenant_user",
            "_tenant_user",
            "_additional_resources",
            "id_event",
            "uuid_event",
            "is_handled",
        )


class EventLogRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _last_event = EventRepresentationSerializer(source="last_event")
    _detail = wb_serializers.HyperlinkField(reverse_name="wbintegrator_office365:eventlog-detail")

    class Meta:
        model = EventLog
        fields = read_only_fields = ("id", "last_event", "_last_event", "order_received", "_detail")


class EventLogModelSerializer(wb_serializers.ModelSerializer):
    _last_event = EventRepresentationSerializer(source="last_event")

    class Meta:
        model = EventLog
        fields = read_only_fields = (
            "id",
            "last_event",
            "_last_event",
            "change_type",
            "order_received",
            "created",
            "changed",
            "id_event",
            "resource",
            "is_handled",
        )


class CallEventModelSerializer(wb_serializers.ModelSerializer):
    _event = EventRepresentationSerializer(source="event")
    _organizer = CallUserRepresentationSerializer(source="organizer")
    _participants = CallUserRepresentationSerializer(source="participants", many=True)
    change_type = wb_serializers.CharField(required=False, read_only=True)

    class Meta:
        model = CallEvent
        fields = read_only_fields = (
            "id",
            "event",
            "_event",
            "organizer",
            "_organizer",
            "type",
            "change_type",
            "start",
            "end",
            "last_modified",
            "created",
            "participants",
            "_participants",
            "is_internal_call",
            "version",
            "join_web_url",
        )
