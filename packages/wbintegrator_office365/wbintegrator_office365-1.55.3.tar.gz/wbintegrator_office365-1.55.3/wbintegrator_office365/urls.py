from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbintegrator_office365.viewsets import viewsets

router = WBCoreRouter()
router.register(
    r"tenantuserrepresentation", viewsets.TenantUserRepresentationViewSet, basename="tenantuserrepresentation"
)
router.register(r"tenantuser", viewsets.TenantUserViewSet)

router.register(
    r"subscriptionrepresentation", viewsets.SubscriptionRepresentationViewSet, basename="subscriptionrepresentation"
)
router.register(r"subscription", viewsets.SubscriptionViewSet, basename="subscription")

router.register(r"eventrepresentation", viewsets.EventRepresentationViewSet, basename="eventrepresentation")
router.register(r"event", viewsets.EventViewSet, basename="event")

router.register(r"calluserrepresentation", viewsets.CallUserRepresentationViewSet, basename="calluserrepresentation")
router.register(r"calluser", viewsets.CallUserViewSet, basename="calluser")

router.register(
    r"calleventrepresentation", viewsets.CallEventRepresentationViewSet, basename="calleventrepresentation"
)
router.register(r"callevent", viewsets.CallEventViewSet, basename="callevent")

router.register(r"calleventchart", viewsets.CallEventReceptionTime, basename="calleventchart")
router.register(r"calleventsummarygraph", viewsets.CallEventSummaryGraph, basename="calleventsummarygraph")

router.register(r"eventlog", viewsets.EventLogViewSet, basename="eventlog")
router.register(r"eventlog", viewsets.EventLogRepresentationViewSet, basename="eventlogrepresentation")

event_router = WBCoreRouter()
event_router.register(
    r"eventlog",
    viewsets.EventLogEventViewSet,
    basename="event-eventlog",
)


urlpatterns = [
    path("", include(router.urls)),
    path("event/<str:last_event_id>/", include(event_router.urls)),
    path("listen", viewsets.listen, name="listen"),
    path("callback/permissions", viewsets.callback_consent_permission),
]
