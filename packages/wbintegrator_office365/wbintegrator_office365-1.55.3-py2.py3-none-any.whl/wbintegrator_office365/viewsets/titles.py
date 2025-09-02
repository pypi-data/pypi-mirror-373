from wbcore.metadata.configs.titles import TitleViewConfig


class TenantUserTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Tenant User: {{tenant_id}}"

    def get_list_title(self):
        return "Tenant Users"

    def get_create_title(self):
        return "New Tenant User"


class CallUserTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Call User: {{_tenant_user.profile_str}}"

    def get_list_title(self):
        return "Call Users"

    def get_create_title(self):
        return "New Call User"


class CallEventTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Call Event: {{_event.id}}"

    def get_list_title(self):
        return "Call Events"

    def get_create_title(self):
        return "New Call Event"


class CallEventReceptionTimeTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Call Events Reception Delay"


class CallEventSummaryGraphTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Call Events Summary Graph"


class SubscriptionTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Subscription: {{id_str}}"
