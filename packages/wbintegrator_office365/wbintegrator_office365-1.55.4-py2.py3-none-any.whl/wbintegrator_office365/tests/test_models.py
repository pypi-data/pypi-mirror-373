from unittest.mock import patch

import pytest
from wbintegrator_office365.factories import EventFactory, SubscriptionFactory
from wbintegrator_office365.importer import DisableSignals
from wbintegrator_office365.models import (
    CallEvent,
    CallUser,
    Event,
    Subscription,
    TenantUser,
)


@pytest.mark.django_db
class TestModels:
    def test_tenantuser(self, tenant_user_factory):
        assert TenantUser.objects.count() == 0
        tenant_user_factory()
        assert TenantUser.objects.count() == 1

    def test_event(self, event_factory):
        assert Event.objects.count() == 0
        # obj = event_factory() # there is a confusion with another model event from another app
        EventFactory()
        assert Event.objects.count() == 1

    @patch("wbintegrator_office365.models.subscription.unsubscribe.delay")
    @patch("wbintegrator_office365.models.subscription.chain")
    @patch("requests.post")
    def test_subscription(self, mock_post, mock_chain, mock_unsubscribe):
        with patch("wbintegrator_office365.models.event.transaction.on_commit", new=lambda fn: fn()):
            assert Subscription.objects.count() == 0
            assert mock_chain.call_count == 0
            SubscriptionFactory()
            assert Subscription.objects.count() == 1
            assert mock_chain.call_count == 0

            assert mock_unsubscribe.call_count == 0
            SubscriptionFactory(is_enable=False)
            assert mock_chain.call_count == 1

    def test_call_event_disconnect_signal(self, call_event_factory):
        assert CallEvent.objects.count() == 0
        with DisableSignals():
            call_event_factory()
        assert CallEvent.objects.count() == 1

    def test_call_event(self, call_event_factory):
        assert CallEvent.objects.count() == 0
        call_event_factory()
        assert CallEvent.objects.count() == 1

    def test_call_user(self, call_user_factory):
        assert CallUser.objects.count() == 0
        call_user_factory()
        assert CallUser.objects.count() == 1

    def test_post_save_participant_event(self, call_event_factory, call_user_factory):
        obj = call_event_factory()
        call_user = call_user_factory()
        obj.participants.add(call_user)
        assert obj.is_internal_call is False
        obj.participants.remove(call_user)
        assert obj.is_internal_call is True
