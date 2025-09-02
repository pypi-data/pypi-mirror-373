from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Operator
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbintegrator_office365.models import Event


class TenantUserDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="tenant_id", label="Tenant Id"),
            dp.Field(key="profile", label="Profile"),
            dp.Field(key="display_name", label="Display name"),
            dp.Field(key="mail", label="Mail"),
            dp.Field(key="phone", label="Phone"),
            dp.Field(key="tenant_organization_id", label="Tenant Organisation"),
            dp.Field(key="is_internal_organization", label="Is internal organization"),
        ]
        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "profile")],
                [repeat_field(2, "display_name")],
                ["mail", "phone"],
                ["tenant_id", "tenant_organization_id"],
            ]
        )


class CallUserDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="tenant_user", label="Tenant User"),
            dp.Field(key="is_guest", label="Is guest"),
            dp.Field(key="is_phone", label="Is phone"),
            dp.Field(key="name_user", label="Display Name"),
            dp.Field(key="phone", label="Phone"),
            dp.Field(key="mail", label="Mail"),
        ]
        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "tenant_user")],
                ["is_guest", "is_phone"],
                [repeat_field(2, "name_user")],
                ["phone", "mail"],
                ["acs_user", "splool_user"],
                ["encrypted", "on_premises"],
                ["acs_application_instance", "spool_application_instance"],
                ["application_instance", "application"],
                [repeat_field(2, "device")],
            ]
        )


class SubscriptionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="subscription_id", label="Subscription Id"),
            dp.Field(key="change_type", label="Change Type"),
            dp.Field(key="expiration_date", label="Expiration"),
            dp.Field(key="type_resource", label="Resource"),
            dp.Field(key="tenant_user", label="Tenant User"),
            dp.Field(key="is_enable", label="Is enable"),
            dp.Field(key="created", label="Created"),
        ]
        return dp.ListDisplay(
            fields=fields,
            formatting=[
                dp.Formatting(
                    column="type_resource",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=Event.Type.CALENDAR),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=Event.Type.CALLRECORD),
                        ),
                    ],
                )
            ],
            legends=[
                dp.Legend(
                    key="type_resource",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value, label=Event.Type.CALENDAR.label, value=Event.Type.CALENDAR
                        ),
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=Event.Type.CALLRECORD.label,
                            value=Event.Type.CALLRECORD,
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "id_str")],
                [repeat_field(2, "subscription_id")],
                [repeat_field(2, "is_enable")],
                ["type_resource", "tenant_user"],
                ["change_type", "change_type"],
                ["created", "expiration_date"],
                [repeat_field(2, "resource")],
                [repeat_field(2, "notification_url")],
                [repeat_field(2, "odata_context")],
                ["application_id", "creator_id"],
                ["client_state", "latest_supported_tls_version"],
                ["notification_content_type", "include_resource_data"],
                ["encryption_certificate_id", "encryption_certificate"],
                [repeat_field(2, "notification_query_options")],
            ]
        )


class EventDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="id", label="Id"),
            dp.Field(key="nb_received", label="Nb received"),
            dp.Field(key="type", label="Type"),
            dp.Field(key="change_type", label="Change Type"),
            dp.Field(key="created", label="Created"),
            dp.Field(key="changed", label="Changed"),
            dp.Field(key="tenant_user", label="Tenant User"),
            dp.Field(key="is_handled", label="Is Handled"),
            dp.Field(key="uuid_event", label="Event UId"),
            dp.Field(key="id_event", label="Event Id"),
            dp.Field(key="subscription_id", label="Subscription id"),
        ]
        return dp.ListDisplay(
            fields=fields,
            formatting=[
                dp.Formatting(
                    column="type",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=Event.Type.CALENDAR),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=Event.Type.CALLRECORD),
                        ),
                    ],
                )
            ],
            legends=[
                dp.Legend(
                    key="type",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value, label=Event.Type.CALENDAR.label, value=Event.Type.CALENDAR
                        ),
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=Event.Type.CALLRECORD.label,
                            value=Event.Type.CALLRECORD,
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "id_str")],
                [repeat_field(2, "uuid_event")],
                [repeat_field(2, "id_event")],
                [repeat_field(2, "is_handled")],
                ["auto_inc_id", "nb_received"],
                ["type", "change_type"],
                ["created", "changed"],
                ["tenant_user", "subscription_id"],
                [repeat_field(2, "resource")],
                [repeat_field(2, "eventlog_section")],
            ],
            [create_simple_section("eventlog_section", "Event Logs", [["eventlog"]], "eventlog", collapsed=True)],
        )


class EventLogDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="id", label="Id"),
            dp.Field(key="order_received", label="Order received"),
            dp.Field(key="change_type", label="Change Type"),
            dp.Field(key="created", label="Created"),
            dp.Field(key="changed", label="Changed"),
            dp.Field(key="last_event", label="Last Event"),
            dp.Field(key="is_handled", label="Is handled"),
            dp.Field(key="id_event", label="Event Id"),
        ]
        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "last_event")],
                [repeat_field(2, "id_event")],
                [repeat_field(2, "is_handled")],
                ["order_received", "change_type"],
                ["created", "changed"],
                [repeat_field(2, "resource")],
            ]
        )


class EventLogEventDisplayConfig(EventLogDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="order_received", label="Order received"),
            dp.Field(key="change_type", label="Change Type"),
            dp.Field(key="is_handled", label="Is handled"),
            dp.Field(key="id_event", label="Event Id"),
            dp.Field(key="resource", label="Resource"),
            dp.Field(key="created", label="Created"),
            dp.Field(key="changed", label="Changed"),
        ]
        return dp.ListDisplay(
            fields=fields,
            formatting=[
                dp.Formatting(
                    column="is_handled",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=True),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREY.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=False),
                        ),
                    ],
                )
            ],
            legends=[
                dp.Legend(
                    key="is_handled",
                    items=[
                        dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label="Present in Outlook", value=True),
                        dp.LegendItem(
                            icon=WBColor.GREY.value,
                            label="Deleted in Outlook",
                            value=False,
                        ),
                    ],
                ),
            ],
        )


class CallEventDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="event", label="Event"),
            dp.Field(key="organizer", label="Organizer"),
            dp.Field(key="change_type", label="Type"),
            dp.Field(key="start", label="Start"),
            dp.Field(key="end", label="End"),
            dp.Field(key="created", label="Created"),
            dp.Field(key="last_modified", label="Last modified"),
            dp.Field(key="is_internal_call", label="Is Internal Call"),
            dp.Field(key="participants", label="Participants"),
        ]
        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "organizer")],
                ["change_type", "type"],
                ["version", "is_internal_call"],
                ["start", "end"],
                ["last_modified", "created"],
                [repeat_field(2, "participants")],
                [repeat_field(2, "join_web_url")],
            ]
        )
