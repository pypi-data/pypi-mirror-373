from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

TENANTUSER_MENUITEM = MenuItem(
    label="Tenant Users",
    endpoint="wbintegrator_office365:tenantuser-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbintegrator_office365.view_tenantuser", "wbintegrator_office365.administrate_event"],
    ),
)

CALLUSER_MENUITEM = MenuItem(
    label="Call Users",
    endpoint="wbintegrator_office365:calluser-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbintegrator_office365.view_calluser", "wbintegrator_office365.administrate_event"],
    ),
)

SUBSCRIPTION_MENUITEM = MenuItem(
    label="Subscriptions",
    endpoint="wbintegrator_office365:subscription-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbintegrator_office365.view_subscription", "wbintegrator_office365.administrate_event"],
    ),
)

EVENT_MENUITEM = MenuItem(
    label="Events",
    endpoint="wbintegrator_office365:event-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbintegrator_office365.view_event", "wbintegrator_office365.administrate_event"],
    ),
)

CALLEVENT_MENUITEM = MenuItem(
    label="Call Events",
    endpoint="wbintegrator_office365:callevent-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbintegrator_office365.view_callevent", "wbintegrator_office365.administrate_event"],
    ),
)

CALLEVENTCHART_MENUITEM = MenuItem(
    label="Call Reception Delay",
    endpoint="wbintegrator_office365:calleventchart-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbintegrator_office365.view_callevent", "wbintegrator_office365.administrate_event"],
    ),
)

CALLEVENTSUMMARYGRAPH_MENUITEM = MenuItem(
    label="Call Summary Graph",
    endpoint="wbintegrator_office365:calleventsummarygraph-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbintegrator_office365.view_callevent", "wbintegrator_office365.administrate_event"],
    ),
)
